# 7x24 mainline stop analysis - 2026-04-25 22:36 +08:00

## Trigger
- User reported that token consumption stopped after around `2026-04-25 20:10 +08:00`.
- Live prod must not be treated as healthy merely because `/healthz` is readable.

## Findings
- `arun-20260425-193924-9b993a` finished at `2026-04-25T20:03:07+08:00`; after that, later activity was recovery/audit, not provider token consumption.
- The node was finalized by `recover_terminal_run_truth`, not by the normal finalize path.
- Audit `aaud-20260425-213037-7f215e` recorded `schedule_result.queued=false` with reason `ticket_lock_unavailable_bypassed`.
- The recovered schedule was manually set to `2026-04-25T22:12:00+08:00`, but trigger `sti-20260425-9b176e30` initially stopped at `trigger_hit` without `assignment_ticket_id` or `assignment_node_id`.

## Recovery Actions
- Created recovery node `node-sti-20260425-9b176e30` for trigger `sti-20260425-9b176e30`.
- Restarted prod runtime process without changing version or applying a candidate.
- After restart, schedule detail bound the trigger to `asg-20260327-223335-b79f27 / node-sti-20260425-9b176e30` and moved it to queued/running projection.
- Dispatch audit `aaud-20260425-223349-f33f90` created run `arun-20260425-223149-91396a`.

## Current Risk
- `arun-20260425-223149-91396a` remains `status=starting` with `provider_pid=0`.
- `/api/status` still reports `running_task_count=0`, `queued_task_count=1`, `active_agent_count=1`.
- Therefore the system is not yet back to true token-consuming execution. It has an exit node and a run shell, but provider startup has not been observed.

## Design Conclusion
- The current 7x24 chain is over-composed for the core invariant.
- The invariant should be simpler: when a mainline run reaches any terminal state, a durable handoff record must be written once, and a single idempotent worker must ensure exactly one next node/run or a future pause gate.
- Schedule, trigger progress, assignment graph, dispatch, finalize recovery, upgrade drain, smoke guard, and ready-dispatch recovery currently share this invariant indirectly, which is why lock contention and recovery paths can still drop the baton.

## Evidence
- run: `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260425-193924-9b993a/run.json`
- trigger node: `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/nodes/node-sti-20260425-9b176e30.json`
- new run: `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260425-223149-91396a/run.json`
- audit: `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/audit/audit.jsonl`
