# fake running root cause 2026-04-29

- checked_at: `2026-04-29T19:45:45+08:00`
- incident_window: `2026-04-29T13:54:36+08:00` - `2026-04-29T14:54:26+08:00`
- node_id: `node-sti-20260429-48d95e4e`
- run_id: `arun-20260429-124942-63fdee`

## Conclusion
- This is a product bug, not normal expected behavior.
- The real run finished successfully at `13:54:36`, but the node did not get the normal `execution_succeeded` audit entry at that time.
- The system triggered prod upgrade checking after `final_result` was written but before the assignment node terminal status was committed.
- The watcher then observed a legitimate short finalizing window as `running_finalize_stall / running_node_projected_terminal`, attempted repair, and applied `candidate=20260429-133742` while the original finalize path had not fully completed.
- The prod restart interrupted the remaining finalize effects, so terminal truth, mainline handoff, and memory writeback were recovered later by `recover_terminal_run_truth`.

## Evidence Timeline
- `2026-04-29T13:54:36+08:00`
  - `deliver_artifact` was written for `node-sti-20260429-48d95e4e`.
  - `logs/runs/prod-idle-upgrade-watchdog-live.md` shows `operator=assignment-executor-final-result` watcher start.
- `2026-04-29T13:54:39+08:00`
  - watcher saw `running_finalize_stall`.
- `2026-04-29T13:55:21+08:00`
  - watcher applied `candidate=20260429-133742` while ghost running still existed.
- `2026-04-29T14:49:40+08:00`
  - `recover_terminal_run_truth` projected terminal result from run files after finalize stalled.
- `2026-04-29T14:50:49+08:00`
  - `mainline_handoff_recorded` was backfilled.
- `2026-04-29T14:51:04+08:00`
  - durable handoff scheduled next workflow mainline for `15:05`.
- `2026-04-29T14:54:26+08:00`
  - `repair_ghost_running` audit confirmed `status_before=running / status_after=succeeded`.

## Code Path
- Unsafe trigger:
  - `.repository/pm-main/src/workflow_app/server/services/assignment_service_parts/task_artifact_store_run_runtime.py`
  - `_assignment_maybe_request_prod_single_check_after_final_result(...)` is called immediately after `final_result` is written and before `_assignment_finalize_execution_run_fail_closed(...)`.
- Safer existing trigger:
  - `.repository/pm-main/src/workflow_app/server/services/assignment_service_parts/task_artifact_store_run_finalize_runtime.py`
  - `_assignment_finalize_post_commit_effects(...)` calls `_assignment_maybe_request_prod_upgrade_after_finalize(...)` after terminal node/run persistence.

## Recommended Fix
- Remove or gate the pre-finalize `final_result` single-check path.
- Only request prod auto-upgrade after the assignment node and run have both been committed to a terminal status, or after terminal recovery has successfully updated the node.
- Add a regression test that asserts a `final_result` file alone must not trigger prod upgrade while the node still shows `running`.
- Update or replace `verify_assignment_final_result_single_check.py`; its current expectation preserves the unsafe behavior.
