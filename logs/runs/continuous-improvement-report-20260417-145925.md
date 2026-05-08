# Continuous Improvement Report

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260417-837f6da9`
- executed_at: `2026-04-17T14:59:25+08:00`
- lane: `测试探测`
- lifecycle_stage: `基于基线测试`

## This Round
- 我这轮把 `run_acceptance_assignment_center_browser.py` 扩成可直连 live `8090` 的 browser acceptance 入口，并新增 `.repository/pm-main/scripts/acceptance/collect_v4_r1_r4_current_version_smoke.py`，把 `V4-R4` 的 prod current-version smoke 固化成正式资产。
- 我把代码收口到 `.repository/pm-main@d1e96f3 / ../workflow_code@d1e96f3`，随后刷新 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 五个 developer workspace 到同一 head。
- 我跑通了 `line budget`、live `V4` smoke 和完整 `workflow gate`，再重新部署 `test`，刷新出新的 `prod candidate=20260417-145421`。
- 我还在任务中心创建了两条 helper 节点：
  - `node-20260417-145552-3e7085` `workflow_testmate`
  - `node-20260417-145653-922dce` `workflow_ucdmate`
  当前 `dispatch-next` 被 `upgrade_drain_active:candidate_newer_pending_idle_window` 合法冻结，等待 idle watcher 在空窗先切版。

## Active Version
- `V4-R1`: `in_progress / 40% / eta=2026-04-19 / 未超时`
  live smoke 已给 route brief 准备好截图和 probe 证据，`workflow_ucdmate` 的首条 route 节点已建但仍等上游 smoke ownership 节点与 idle upgrade 窗口。
- `V4-R2`: `planned / 5% / eta=2026-04-20 / 未超时`
  仍冻结在第二优先级。
- `V4-R3`: `planned / 10% / eta=2026-04-20 / 未超时`
  未新增超时或 AAR。
- `V4-R4`: `in_progress / 55% / eta=2026-04-20 / 未超时`
  `prod=20260417-134734` 上的 current-version smoke 已通过，新增 live browser screenshots/probes 与 smoke markdown，可直接作为后续 helper 回归入口。

## Release Boundary
- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `workspace_head=code_root_head=d1e96f3`
- `push_block_reason=-`
- `next_push_batch=等待 idle watcher 在空窗把 20260417-145421 切进 live；切版后优先让 node-20260417-145552-3e7085 / node-20260417-145653-922dce 脱离 upgrade drain`

## Live Truth
- `prod current_version=20260417-134734`
- `candidate_version=20260417-145421`
- `candidate_is_newer=true`
- `drain_active=true`
- `drain_reason_code=candidate_newer_pending_idle_window`
- `running_task_count=1`
- `can_upgrade=false`
- `ghost_running_detected=false`
- `parallel_candidate_count=2`
- `parallel_dispatched_count=2`
- `active_helper_tasks=[node-20260417-145552-3e7085, node-20260417-145653-922dce]`
- `pending_helper_nodes=[node-20260417-145552-3e7085:ready, node-20260417-145653-922dce:pending_upstream]`
- `parallel_block_reason=upgrade_drain_active:candidate_newer_pending_idle_window`

## Validation
- `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- `.repository/pm-main/.test/20260417-143837-417/report.md`
- `.repository/pm-main/.test/20260417-144846-784/report.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260417-145344.md`
- `.running/control/logs/test/deploy-20260417-145421.json`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `http://127.0.0.1:8090/api/config/developer-workspaces`
- `http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-20260417-145552-3e7085`

## Version Decision
- `version_transition_decision=stay(V4)`
- `next_activation_candidate=-`
- `next_activation_ready=false`
- `switch_blockers=V5 仍保持 backlog activation_readiness=draft；V4 还在等待 candidate 145421 切进 live，并把 workflow_testmate / workflow_ucdmate helper 链真正跑起来`
- `memory_ref=.codex/memory/2026-04/2026-04-17.md`
