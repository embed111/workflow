# 7x24 接力修复与退役项目门禁收口

- preference_ref: state/user-preferences.md
- code_workspace: `.repository/pm-main`
- code_commit: `fa57d38`（同步到 `../workflow_code/main`）
- test_deploy_version: `20260428-014158`
- prod_candidate: `20260428-014158`

## 根因
- `workflow` 主线：执行终态已经写入 run/node，但 finalize 的 already-terminal 分支会提前返回，导致没有耐久记录 `mainline_handoff`，下一棒没有被补排。
- AI 小说项目：schedule recovery 遇到已终态 assignment ref 时直接跳过，没有把 trigger/plan 的 stale `running` 状态回写为终态，导致计划层看起来仍卡在旧接力。

## 修复
- 增加 terminal mainline handoff backfill；finalize 异常后或重复收尾时，若 run/node 已经终态，仍补记并 drain 下一棒。
- schedule trigger recovery 遇到终态 assignment ref 时，回写 trigger progress 与 plan last result，避免 stale running 卡住下一次触发。
- `failure_retry_max_attempts` 默认改为 `0`，治理口径定义为无限失败接力；非零次数只允许作为升级/告警阈值，不作为停止条件。
- 删除退役 `Comics Bootstrap Smoke` 相关旧 live/restore gate 脚本；新增代码引用扫描，阻止 `project-comics-smoke` / `Comics Bootstrap Smoke` 回到 `src`/`scripts`/部署脚本。

## 红绿节奏
- 上次 7x24 停止红灯：
  - `verify_mainline_handoff_backfill_after_finalize_exception.py` 红灯：`.repository/pm-main/.test/20260428-004120-936/report.md`
  - 同用例绿灯：`.repository/pm-main/.test/20260428-005959-119/report.md`
- AI 小说 stale trigger 红绿：
  - baseline 红灯现象：terminal assignment ref 后 trigger 仍为 `running / dispatch_requested`
  - 绿灯：`.repository/pm-main/.test/20260428-010013-647/report.md`
- 无限失败接力红绿：
  - 红灯：`.repository/pm-main/.test/20260428-005429-773/report.md`
  - 绿灯：`.repository/pm-main/.test/20260428-005704-352/report.md`
- 退役项目引用扫描红绿：
  - 红灯：`.repository/pm-main/.test/20260428-005446-865/report.md`
  - 绿灯：`.repository/pm-main/.test/20260428-005726-106/report.md`

## 验证
- 受影响 focused probes 通过，含：
  - `.repository/pm-main/.test/20260428-010605-285/report.md`
  - `.repository/pm-main/.test/20260428-010613-961/report.md`
  - `.repository/pm-main/.test/20260428-010550-654/report.md`
  - `.repository/pm-main/.test/20260428-010557-914/report.md`
- rebase 后验证：
  - `python scripts/quality/check_workspace_line_budget.py --root .`：`.repository/pm-main/.test/20260428-013843-270/report.md`
  - `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`：`.repository/pm-main/.test/20260428-012741-010/report.md`
- `test` 部署门禁通过：`.running/control/reports/test-gate-20260428-014158.json`
- `test` 运行态部署后复查发现旧状态里仍有 `project-comics-smoke=active`，已同步改成 tombstone：
  - `.running/control/runtime/test/state/project-registry.json`: `lifecycle_state=archived`
  - `.running/control/runtime/test/state/project-runtime-policies.json`: `manual_pause=true / failure_retry_max_attempts=0`
- 代码扫描：
  - `.repository/pm-main/src`
  - `.repository/pm-main/scripts`
  - `.running/test/src`
  - `.running/test/scripts`
  - 均未命中 `project-comics-smoke` / `Comics Bootstrap Smoke` / 旧 restore/live gate 脚本名。

## 当前运行态
- `prod current=20260427-215714`
- `prod candidate=20260428-014158`
- `prod` 当前 `running_task_count=1`，running gate 正常阻止热切。
- `workflow`: `operation_state=running`，`operation_mode=continuous_7x24`，`running_count=1`。
- `project-ai-novel-profit`: `operation_state=interval_waiting`，下一次 `[持续迭代] novel_project_pm` 为 `2026-04-28T03:51:00+08:00`。
- `project-comics-smoke`: `lifecycle_state=archived`，`manual_pause=true`，`startup_ready=false`；当前 schedules 未出现 Comics 项目恢复项。
- `prod/test` 的运行态策略均已把 `project-comics-smoke` 保持为 manual pause tombstone；`workflow` 与 AI 小说项目的策略文件已收敛到 `failure_retry_max_attempts=0`。

## 增量观察
- delta_observation: 用户明确要求退役项目不要再被恢复、7x24 用例按先红后绿、失败后应一直接力而非按次数停住。
- delta_validation: 后续涉及 7x24 失败恢复、项目恢复或发布门禁时，优先检查退役项目 tombstone、无限失败接力默认值和 red/green 证据是否仍在。
