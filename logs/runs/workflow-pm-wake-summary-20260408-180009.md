# workflow-pm-wake-summary

- checked_at: `2026-04-08T18:00:09+08:00`
- ticket_id: `asg-20260407-103450-fb8ba8`
- node_id: `node-sti-20260408-98a52773`
- run_id: `arun-20260408-175359-0d87b5`
- memory_ref: `.codex/memory/2026-04/2026-04-08.md`

## 巡检结论

1. 当前不升级。
   - live `prod` 的 `/api/runtime-upgrade/status` 返回 `current=candidate=20260408-171450`、`running_task_count=3`、`can_upgrade=false`、`blocking_reason=存在运行中任务，暂不可升级`。
   - 按任务要求排除当前巡检节点 `node-sti-20260408-98a52773` 后，升级门禁仍为 `running_task_count=2`、`can_upgrade=false`；说明除了我这轮保底巡检，还存在 `workflow_bugmate` 与 `workflow_testmate` 的运行中 helper 节点，因此这轮不能 `apply`。
   - 当前也不存在更高 candidate：`candidate_is_newer=false`。
2. 当前不补链。
   - `[持续迭代] workflow` 的主线 schedule `sch-20260407-20001ab4` 仍为 `enabled=true`，`next_trigger_at=2026-04-08T18:20:00+08:00`。
   - 保底 schedule `sch-20260407-5ef5e5c8` 仍为 `enabled=true`，`next_trigger_at=2026-04-08T18:50:00+08:00`。
   - `schedules.jsonl` 在 `2026-04-08T17:50:42+08:00` 与 `2026-04-08T17:53:36+08:00` 已记录 `assignment-self-iteration` 对两条 schedule 的更新，主线 future 与保底 future 都已经落盘。
3. 当前 live 真相是“3 running / 0 ready / 双 future 已挂”。
   - `workflow`：`node-sti-20260408-98a52773`，`run_id=arun-20260408-175359-0d87b5`，`updated_at=2026-04-08T17:59:01+08:00`
   - `workflow_bugmate`：`node-20260408-173431-adfdb4`，`run_id=arun-20260408-174925-e6dafe`，`updated_at=2026-04-08T17:58:52+08:00`
   - `workflow_testmate`：`node-20260408-173601-4cde2d`，`run_id=arun-20260408-175138-653761`，`updated_at=2026-04-08T17:58:50+08:00`
   - `/api/status` 在 `2026-04-08T17:59:00+08:00` 返回 `running_task_count=3`、`assignment_running_agent_count=3`、`schedule_total=2`、`assignment_workboard_summary.active_agent_count=3`，与任务图和升级门禁一致。
4. 这轮 `done_definition` 已满足。
   - `prod` 仍保留未来可执行的 workflow 主线入口 `2026-04-08T18:20:00+08:00`
   - 本次巡检结论与证据已落盘
   - 主链未断，因此这轮无需手工补链

## 核验范围

- `docs/workflow/governance/PM版本推进计划.md`
- `docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`
- `GET /healthz`
- `GET /api/status`
- `GET /api/runtime-upgrade/status`
- `GET /api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260407-103450-fb8ba8&exclude_assignment_node_id=node-sti-20260408-98a52773`
- `GET /api/schedules`
- `GET /api/schedules/sch-20260407-20001ab4`
- `GET /api/schedules/sch-20260407-5ef5e5c8`
- `GET /api/assignments/asg-20260407-103450-fb8ba8/graph`

## 证据路径

- `logs/runs/workflow-pm-wake-summary-20260408-180009.md`
- `workflow-pm-wake-summary.md`
- `state/session-snapshot.md`
- `docs/workflow/governance/PM版本推进计划.md`
- `.codex/memory/2026-04/2026-04-08.md`
- `.running/control/envs/prod.json`
- `.running/control/instances/prod.json`
- `.running/control/prod-last-action.json`
- `.running/control/prod-candidate.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/task.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-98a52773.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-175359-0d87b5/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-175359-0d87b5/events.log`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-174925-e6dafe/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-175138-653761/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`
- `.running/control/runtime/prod/logs/events/schedules.jsonl`

## 下一次建议唤醒时间

- 主线 next: `sch-20260407-20001ab4 -> 2026-04-08T18:20:00+08:00`
- 保底 next: `sch-20260407-5ef5e5c8 -> 2026-04-08T18:50:00+08:00`
- 建议补看 next: 如果 `2026-04-08T18:20:00+08:00` 的主线未按时建单，或当前 `3` 个 running 节点在主线命中后仍未释放且没有新的 `future/ready` 入口，建议在 `2026-04-08T18:25:00+08:00` 再做一次保底巡检
