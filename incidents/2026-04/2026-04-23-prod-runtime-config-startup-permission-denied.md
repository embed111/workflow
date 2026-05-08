# 生产事故记录 | 2026-04-23 | prod 启动期 runtime-config 写回权限拒绝

- incident_id: `INC-20260423-prod-runtime-config-permission-denied`
- severity: `SEV-2`
- environment: `prod`
- detected_at: `2026-04-23T19:45:46+08:00`
- detected_by: `workflow(pm)`
- related_version:
  - `broken_on_prod=20260423-133937`
  - `fixed_in_workspace=1294ca9`
  - `fixed_on_test=20260423-202301`
  - `fixed_on_prod=20260423-202504`
- related_requirement:
  - `V9-R4`
- status: `resolved`
- resolution_time: `2026-04-23T20:25:06+08:00`
- aar_policy: `defer_until_version_close`
- aar_target_version: `V9`

## 1. 事故摘要
- `prod` 在启动/重启时反复退出，`8090` 无 listener，supervisor 持续进入 `watchdog_restart`。
- 任务中心表面症状是“token 停止消耗、run 被收成运行句柄缺失”，但直接故障不在 schedule 或 provider，而在 web server 启动期写 `runtime-config.json`。

## 2. 用户面影响
- 正式环境 `8090` 一度不可达。
- 期间 `workflow` 主线与巡检任务会出现新 node 仍能建出，但运行记录空 `stdout/stderr`、缺 `result.json`，最后被收成 `运行句柄缺失` 或 watchdog 自动失败。
- 运行态误导风险：
  - 容易被误判成 `schedule` 断链或 `Codex` provider 不稳定。
  - 实际上是 web server 进程启动失败，导致运行句柄和读面都一起漂移。

## 3. 现场真相
- `prod-last-action.json` 连续出现：
  - `action=watchdog_restart`
  - `status=retrying`
  - `reason=launcher exited with code 1`
- 启动 stderr 真正异常：
  - `PermissionError: [WinError 5] 拒绝访问`
  - 位置：`runtime-config.json.tmp -> runtime-config.json` 的 `tmp.replace(path)`
- 对应调用链：
  - `src/workflow_app/server/bootstrap/web_server_runtime_parts/event_persistence_and_flags.py:858`
  - `src/workflow_app/server/bootstrap/web_server_runtime_parts/runtime_paths_and_config.py:402`
  - `src/workflow_app/runtime/device_path_config.py:114`

## 4. 根因判断
- 启动链在进入 web server 前，会无条件把启动期计算出的 `runtime_patch` 写回 `runtime-config.json`。
- Windows 上该文件一旦被其他进程短时占用，`tmp.replace(path)` 会直接抛 `PermissionError [WinError 5]`。
- 旧实现把这条异常当成硬失败处理，导致整个 launcher 退出，supervisor 继续 watchdog restart，形成“现网一直在重启”的事故形态。

## 5. 修复动作
- 代码修复：
  - 在 `runtime_paths_and_config.py` 中给 `save_runtime_config` 增加：
    - no-op patch 跳过
    - 权限拒绝识别
    - `fail_open_permission_error`
    - `save_runtime_config_startup_fail_open()`
  - 在 `event_persistence_and_flags.py` 启动路径改为：
    - startup 持久化命中权限拒绝时只告警，不再让 web server 启动失败
- 验证：
  - `scripts/acceptance/verify_startup_runtime_config_permission_fail_open.py`
  - `scripts/acceptance/verify_runtime_config_device_paths.py`
  - `run_acceptance_workflow_gate.py`
- 发布：
  - `workflow_code/main` 收口到 `1294ca9`
  - `test=20260423-202301`
  - `prod=20260423-202504`

## 6. 事故证据
- 启动失败证据：
  - `.tmp-prod-recover-20260420-1856-stderr.log`
- 修复提交：
  - `pm-main@1294ca9`
- 验证报告：
  - `.repository/pm-main/.test/20260423-195951-301/report.md`
  - `.repository/pm-main/.test/20260423-200000-836/report.md`
  - `.repository/pm-main/.test/20260423-201445-091/report.md`
- 部署报告：
  - `.running/control/logs/test/deploy-20260423-202301.json`
  - `.running/control/logs/prod/deploy-20260423-202504.json`

## 7. 后续避免方向（供版本结束 AAR 展开）
- 启动链中所有“写运行态配置”的动作，需要区分：
  - `必须成功的硬前提`
  - `可延后/可跳过的持久化优化`
- `prod` 启动路径需要统一审视类似文件写回点：
  - `runtime-config`
  - snapshot refresh
  - store/index/meta writeback
- 需要补一条版本结束 AAR，回答至少三件事：
  - 为什么启动链会把配置写回当成硬前提
  - 为什么现网最初被误判成 `schedule/provider` 问题
  - 如何把“启动 fail-open 合同”扩展成统一的 prod 启动稳定性规则

## 8. AAR 约束
- 当前不在本文件里直接展开完整 AAR。
- 版本结束条件满足后，必须补做：
  - `pm/versions/V9/aar/YYYY-MM/<date>-startup-runtime-config-permission-denied.md`
- 目标：
  - 从“单点修复”升级到“启动链 fail-open 设计规则 + probe 覆盖 + 运维判障口径”。
