# Continuous Improvement Report 2026-04-15 21:56:59 +08:00

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260415-46711d26`
- active_version: `V3`
- lane: `功能开发`
- lifecycle_stage: `开发实现`

## Summary
- 我把 `prod idle watcher` 的 `apply_wait_seconds` 从默认 `240s` 放宽到 `420s`，并让 `start_workflow_env.ps1 / workflow_env_common.ps1` 显式透传这条参数，避免正式升级其实成功、watcher 却先超时，导致 PM current-version snapshot refresh 漏跑。
- 我把 `verify_v3_test_asset_ownership.py` 从旧的 `V2` 矩阵改到当前 `V3` 矩阵，并把 `workflow_testmate / workflow_qualitymate` 的 owner cadence、矩阵回写和 current-version smoke 责任正式写进 `V3` 资产。
- 我补跑了 `prod=20260415-205106` 的 live current-version smoke、`TC-PM-003`、完整 `workflow gate`，随后把代码提交为 `039eb4e`、收口到本机 `../workflow_code`，并把 `test/prod candidate` 刷到 `20260415-215035`。

## Actions
- 修改 `.repository/pm-main/scripts/apply_prod_candidate_when_idle.py`，把 watcher 默认升级确认窗口收宽到 `420s`。
- 修改 `.repository/pm-main/scripts/workflow_env_common.ps1` 与 `.repository/pm-main/scripts/start_workflow_env.ps1`，把 `ApplyWaitSeconds` 作为显式参数和环境变量入口透传给 watcher。
- 修改 `.repository/pm-main/scripts/acceptance/verify_apply_prod_candidate_when_idle.py`，锁住默认等待窗口至少为 `360s`。
- 修改 `.repository/pm-main/scripts/acceptance/verify_v3_test_asset_ownership.py`，把 ownership probe 的真相源切到 `pm/versions/V3/需求映射与覆盖矩阵.md`。
- 运行 `refresh_pm_current_version_snapshot.py`，把 `pm/PM当前版本计划.md` 和 `pm/versions/V3/版本计划.md` 追平到 `baseline=prod=20260415-205106`，并继续反映 `candidate=20260415-215035`。
- 在全局主图下创建两条 `V3-R5` helper 节点：
  - `workflow_testmate / node-20260415-215247-cb143d`
  - `workflow_qualitymate / node-20260415-215337-95049b`
- 两次调用 `dispatch-next`，但都被 `upgrade_drain_active:candidate_newer_pending_idle_window` 合法冻结；helper 入口已保留，等待 `215035` 进 live 后继续派发。

## Validation
- `.repository/pm-main/.test/20260415-214450-298/report.md`
- `.repository/pm-main/.test/20260415-214500-329/report.md`
- `.repository/pm-main/.test/20260415-214509-540/report.md`
- `.repository/pm-main/.test/20260415-214518-229/report.md`
- `.repository/pm-main/.test/20260415-214538-468/report.md`
- `.repository/pm-main/.test/20260415-214616-070/report.md`
- `Invoke-RestMethod http://127.0.0.1:8090/api/status`
- `Invoke-RestMethod http://127.0.0.1:8090/api/runtime-upgrade/status`
- `logs/runs/prod-idle-upgrade-watchdog-live.md`
- `.running/control/logs/test/deploy-20260415-215035.json`

## Version
- `version_transition_decision=stay(V3)`
- 当前 active 需求逐项评估：
  - `V3-R1=status=in_progress / progress=55% / eta=2026-04-16 / timeout=未超时`
  - `V3-R2=status=in_progress / progress=65% / eta=2026-04-16 / timeout=未超时`
  - `V3-R3=status=planned / progress=25% / eta=2026-04-18 / timeout=未超时`
  - `V3-R4=status=in_progress / progress=80% / eta=2026-04-16 / timeout=未超时`
  - `V3-R5=status=in_progress / progress=70% / eta=2026-04-16 / timeout=未超时`
- 本轮无需求点超时，不触发新的版本 AAR。

## Boundary
- `root_sync_state=clean_synced`
- `ahead_count=0 / dirty_tracked_count=0 / untracked_count=0`
- `workspace_head=code_root_head=039eb4e`
- `push_block_reason=-`
- `next_push_batch=等待 candidate 20260415-215035 进入 live 后补 watcher post-upgrade snapshot refresh 与 helper current-version smoke`

## Parallel
- `parallel_candidate_count=2`
- `parallel_dispatched_count=0`
- `active_helper_tasks=[workflow_testmate node-20260415-215247-cb143d ready, workflow_qualitymate node-20260415-215337-95049b ready]`
- `parallel_block_reason=upgrade_drain_active:candidate_newer_pending_idle_window`
- `helper_dispatch_focus=V3-R5 owner cadence + quality freeze`
- `helper_dispatch_effect=两条 helper 节点已真实创建，但 dispatch-next 被 upgrade drain 冻结；等待 215035 进 live 后继续派发`

## Next
- 等 `prod` 从 `20260415-205106` 升到 `20260415-215035` 后，优先补 watcher post-upgrade snapshot refresh smoke，确认 `document_baseline` 不再因 watcher 先超时而漏刷。
- 继续接回 `workflow_testmate / workflow_qualitymate` 两条 `V3-R5` helper 节点，把真实交付折回矩阵和版本 history。
- 若 `215035` 进 live 后 smoke 继续通过，再把 `V3-R4 / V3-R5` 向退出门槛推进，并重新判断是否接近切版条件。

## Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: `prod idle watcher` 的默认等待窗口过短会制造“升级已成功但 PM 快照没刷新”的假回退；并且当 `candidate_is_newer=true` 时，helper dispatch 会被 `upgrade_drain_active` 合法冻结。
- delta_validation: 等 `20260415-215035` 进 live 后，补 `post-upgrade snapshot refresh + helper smoke`，确认 watcher wait window 与 drain 口径同时成立。
