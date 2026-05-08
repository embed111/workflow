# Continuous Improvement Report

- generated_at: `2026-04-13T23:59:21+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260413-8ebc7aac`
- active_version: `V2`
- phase: `功能开发 / 开发实现`
- advancement_type: `当前需求开发`
- release_boundary: `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=2e18988`
- memory_ref: `.codex/memory/2026-04/2026-04-13.md` + `.codex/memory/2026-04/2026-04-14.md`

## 本轮推进
- `V2-R1`：把 `pm_daily_governance_status` 接进 `/api/status` 与 `/api/dashboard`，并在任务中心版本推进区新增“每日治理”卡，直接显示 daily history、学习报告缺口、学习目录与保留清理候选。
- `task-center workboard`：把 `assignment_center_events.js`、`index_training_loop_panels.css`、`run_acceptance_assignment_center_browser.py` 与 `verify_assignment_workboard_layout_rules.js` 一起收口，补上布局探针与浏览器工作面约束。
- `发布边界`：在 `.repository/pm-main` 提交 `2e18988 feat(task-center): 增加每日治理看板并收口工作面布局探针`，随后把本机 `../workflow_code` fast-forward 到同一批次，并刷新 `test/prod candidate=20260413-235441`。

## 验证
- `python scripts/quality/check_workspace_line_budget.py --root .`
  - 证据：`.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- `node scripts/acceptance/check_web_client_bundle_syntax.js`
  - 证据：`.repository/pm-main/.test/20260413-234543-933/report.md`
- `python scripts/acceptance/verify_pm_version_board_view.py`
  - 证据：`.repository/pm-main/.test/20260413-234559-623/report.md`
- `node scripts/acceptance/verify_assignment_version_board_filters.js`
  - 证据：`.repository/pm-main/.test/20260413-234617-930/report.md`
- `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
  - 证据：`.repository/pm-main/.test/runs/workflow-gate-acceptance-20260413-234822.md`
- `powershell -File .repository/pm-main/scripts/deploy_workflow_env.ps1 -Environment test`
  - 证据：`.running/control/logs/test/deploy-20260413-235441.json`
- live 复核：
  - `http://127.0.0.1:8092/healthz`
  - `http://127.0.0.1:8092/api/status`
  - `http://127.0.0.1:8090/api/runtime-upgrade/status`
  - `http://127.0.0.1:8090/api/schedules`

## Active Requirements
- `V2-R1`: `in_progress / 82% / ETA 2026-04-18 / 未超时`
- `V2-R2`: `in_progress / 75% / ETA 2026-04-18 / 未超时`
- `V2-R3`: `in_progress / 88% / ETA 2026-04-19 / 未超时`
- `V2-R4`: `planned / 25% / ETA 2026-04-19 / 未超时`
- `V2-R5`: `planned / 10% / ETA 2026-04-17 / 未超时`
- `V2-R6`: `in_progress / 80% / ETA 2026-04-15 / 未超时`
- `V2-R7`: `in_progress / 75% / ETA 2026-04-16 / 未超时`
- `V2-R8`: `completed / 100% / 已于 2026-04-13 完成`

## Live Truth
- `prod current_version=20260413-231634`
- `prod candidate_version=20260413-235441`
- `candidate_is_newer=true / drain_active=true / can_upgrade=false / blocking_reason=running_tasks_present`
- 当前主线仍为 `node-sti-20260413-8ebc7aac / [持续迭代] workflow / 2026-04-13 22:59:00 / arun-20260413-232817-7af153 / running`
- 新的 mainline once 节点 `node-sti-20260413-04a028fe` 已建单待调度；保底下一次巡检触发时间是 `2026-04-14T00:00:00+08:00`

## 风险与下一步
- 当前剩余即时风险：`V2-R1` 仍缺正式编号化回归；`V2-R2` 若继续下钻只剩独立版本详情页/更广可见性；`20260413-235441` 仍待 idle watcher 在空窗切入。
- 下一步优先补 `V2-R1` 的正式编号化回归，让 daily governance 不只可见，而且有独立编号化验收口径。
- `R1 / R2` 收口后切入 `V2-R5` 的 `workflow_ucdmate` 创建与首批职责接线。

## Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: `V2-R1` 的自动补档/保留清理如果只停在文件与脚本层，PM 在任务中心里仍然看不到治理真相；这轮已经把它补到状态接口和版本推进区工作面。
- delta_validation: 下一轮先补 `V2-R1` 的正式编号化回归，并继续观察 `20260413-235441` 是否由 idle watcher 自动切入 prod。
