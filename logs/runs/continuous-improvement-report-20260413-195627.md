# Continuous Improvement Report

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260413-1e073c5b`
- executed_at: `2026-04-13T19:56:27+08:00`
- lane: `功能开发`
- lifecycle_stage: `开发实现`
- progress_type: `当前需求开发`
- active_version: `V2`
- preference_ref: `state/user-preferences.md`
- memory_ref: `.codex/memory/2026-04/2026-04-13.md`

## Result Summary
- 我把 `V2-R8` 从“只有 planned version schema/readiness probe”推进到了“切版前专用 activation gate / probe binding 真门禁”。`pm_version_board` 现在会同时检查 `draft:` probe、`blocking_items`、`activation_readiness` 和开发工作区里的真实 acceptance probe 绑定，不再把 `V3` 误报成 `next_activation_ready=true`。
- 我新增了 `.repository/pm-main/scripts/acceptance/verify_planned_version_activation_gate_binding.py`，并把它接进 `workflow gate`；同时更新 `verify_pm_version_board_view.py`，把现网期望改成 `V3 next_activation_ready=false / hard_failures=['V3']`。
- 我完成 `.repository/pm-main -> ../workflow_code` 收口到 `f2b7880`，重新跑通 `workflow gate`，并刷新 `test/prod candidate=20260413-195450`。`prod` 当前仍是 `20260413-184546`，继续由 idle watcher 等空窗自动切版。

## Live Truth
- `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=f2b7880 / push_block_reason=- / next_push_batch=待切批`
- `prod /api/runtime-upgrade/status` 当前为 `current_version=20260413-184546 / candidate_version=20260413-195450 / candidate_is_newer=true / request_pending=false / drain_active=true / can_upgrade=false / running_task_count=1`
- 当前 `7x24` 仍保持 `running_task_count=1 / queued_task_count=2 / workflow_mainline_starvation_state=mitigated`
- `test /api/status` 已验证新门禁生效：`pm_version_board.activation_summary.next_activation_ready=false / hard_failures=['V3']`

## Validation
- `python scripts/quality/check_workspace_line_budget.py --root .`
  - report: `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- `python scripts/acceptance/verify_pm_version_board_view.py`
  - session: `.repository/pm-main/.test/20260413-195146-854/report.md`
- `python scripts/acceptance/verify_planned_version_activation_gate_binding.py`
  - session: `.repository/pm-main/.test/20260413-194349-951/report.md`
- `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
  - report: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260413-195341.md`
- `powershell -File .repository/pm-main/scripts/deploy_workflow_env.ps1 -Environment test`
  - report: `.running/control/logs/test/deploy-20260413-195450.json`
- `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8092/healthz`
- `Invoke-RestMethod http://127.0.0.1:8092/api/status`
- `Invoke-RestMethod http://127.0.0.1:8090/api/runtime-upgrade/status`

## Requirement Evaluation
- `V2-R1`: `status=in_progress / progress=65% / eta=2026-04-18 / timeout=未超时`
  - 自动补档和最近 `7` 份保留清理已经落地，剩余缺口是正式编号化回归与更可见的治理展示层。
- `V2-R2`: `status=in_progress / progress=55% / eta=2026-04-18 / timeout=未超时`
  - 真实版本推进视图已落地，剩余缺口是更聚焦的负责人筛选与独立详情视图。
- `V2-R3`: `status=planned / progress=55% / eta=2026-04-19 / timeout=未超时`
  - 新候选已刷新到 `195450`，但“候选刷新与发布边界助手”本身仍缺独立专项验收。
- `V2-R4`: `status=planned / progress=25% / eta=2026-04-19 / timeout=未超时`
  - 当前版 smoke/dispatch 证据已具备，治理动作助手化仍缺专项自动化回归。
- `V2-R5`: `status=planned / progress=5% / eta=2026-04-17 / timeout=未超时`
  - `workflow_ucdmate` 仍待在 `R1 / R2 / R8` 骨架更稳后切入。
- `V2-R6`: `status=in_progress / progress=80% / eta=2026-04-15 / timeout=未超时`
  - `24 -> 28` 文档归属分叉已消除，剩余缺口是 `row 28` 的跨版本治理继续吸收。
- `V2-R7`: `status=in_progress / progress=75% / eta=2026-04-16 / timeout=未超时`
  - 用例/证据矩阵已成形，剩余缺口是编号化回归口径继续沉淀。
- `V2-R8`: `status=in_progress / progress=96% / eta=2026-04-16 / timeout=未超时`
  - activation gate / probe binding 已落地，剩余缺口已从“没有门禁”切换为“`V3` 的 `draft:` probe 与 blocker 尚未清理成真实 ready”。

## Delta
- delta_observation: `pm-main` 的真实 acceptance probe 在 `.repository/pm-main/scripts/acceptance/`，不能只按 PM 壳仓根的 `scripts/acceptance/` 去找，否则 activation gate 会把已存在的 probe 误判成未绑定。
- delta_validation: 下一轮继续清理 `V3` 的 `draft:` probe、`blocking_items` 与 `activation_readiness`，再通过 `test /api/status` 确认 `next_activation_ready` 是否从 `false` 变成真实 `true`。

## Next
- 我下一步优先清理 `V3` 的 `draft:` probe 与 blocker，让 `next activation` 从 fail-closed 走向真实 ready。
- 我随后补 `V2-R1` 的正式编号化回归与更可见的治理展示层。
- 我继续等待 idle watcher 在空窗把 `prod` 从 `20260413-184546` 切到 `20260413-195450`。
