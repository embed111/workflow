# 项目运维暂停启动运行开关 - 20260425-154536

- preference_ref: state/user-preferences.md
- delta_observation: 用户明确希望在项目运营页直接点击暂停或启动项目，后续可能因为换环境执行而需要先暂停当前项目派发。
- delta_validation: 后续项目启动/迁移/换环境时，先回读项目 runtime policy 的 `manual_pause` 与启动准入状态，再决定是否派发主控 PM。

## 目标
- 在项目运维面提供手动 `暂停` / `启动` 开关。
- 暂停后项目进入 `manual_pause_active` 阻塞，不再被误判为可启动。
- 启动后清除手动暂停，恢复按原 runtime policy 与 startup readiness 判断。

## 代码收口
- commit: `7139f47 feat(projects): 增加项目暂停启动运行开关`
- 已同步到 `.repository/pm-main` 与 `../workflow_code`。
- 后端新增：
  - `POST /api/projects/{project_id}/runtime-policy/pause`
  - `POST /api/projects/{project_id}/runtime-policy/resume`
  - runtime policy 持久化字段：`manual_pause`
- 前端新增：
  - 项目运维参数中的 `项目运行开关`
  - `manual_pause=false` 时显示 `暂停`
  - `manual_pause=true` 时显示 `启动`

## 验证
- `node scripts/acceptance/verify_project_ops_module_ui.js`
  - 红灯先行：缺少启动恢复动作时失败。
  - 绿灯报告：`.repository/pm-main/.test/20260425-152346-622/report.md`
- `python scripts/quality/check_workspace_line_budget.py --root .`
  - 通过：`.repository/pm-main/.test/20260425-152327-752/report.md`
- `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
  - 通过：`.repository/pm-main/.test/runs/workflow-gate-acceptance-20260425-153923.md`
  - gate 中已覆盖 `manual_pause_active` 阻塞与项目运维 UI。

## 发布
- 初次 `test` 部署因旧 test 进程 `PID=51776` 正在运行而 fail-closed。
- 已用受支持入口停止 `test`：
  - `powershell -NoProfile -ExecutionPolicy Bypass -File .repository/pm-main/scripts/stop_workflow_env.ps1 -Environment test`
- 已重新部署 `test` 并刷新 `prod` candidate：
  - version: `20260425-154411`
  - deploy report: `.running/control/logs/test/deploy-20260425-154411.json`
  - test gate evidence: `.running/control/reports/test-gate-20260425-154411.json`
  - prod candidate: `.running/control/prod-candidate.json`
- `prod` 未直接 apply：
  - current: `20260425-144452`
  - candidate: `20260425-154411`
  - `running_task_count=1`
  - `can_upgrade=false`
  - `request_pending=false`

## 结论
- 项目运营页已具备手动暂停/启动项目的产品能力。
- 当前发布边界已到 `test + prod candidate`，生产正式切换仍等待空窗或用户手动升级。
