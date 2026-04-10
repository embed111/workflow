# workflow-pm-wake-summary

- generated_at: `2026-04-08T00:24:14+08:00`
- ticket_id: `asg-20260407-103450-fb8ba8`
- node_id: `node-sti-20260408-d5d29c5f`
- run_id: `arun-20260408-002055-ce05f6`
- graph_name: `任务中心全局主图`
- active_version: `V1`
- active_packages: `V1-P0 / V1-P2`

## 巡检结论

1. 当前不升级。
   `GET /api/runtime-upgrade/status` 在 `2026-04-08T00:24:14+08:00` 返回：`current_version=20260407-200414`、`candidate_version=20260408-000353`、`running_task_count=1`、`can_upgrade=false`、`request_pending=false`、`blocking_reason=存在运行中任务，暂不可升级`。当前唯一 running 节点就是本轮保底巡检 `node-sti-20260408-d5d29c5f`，所以本轮未调用 `/api/runtime-upgrade/apply`。
2. 当前不补链。
   `GET /api/schedules/sch-20260407-20001ab4` 仍保留 `[持续迭代] workflow` 的 future 入口：`next_trigger_at=2026-04-08T00:41:00+08:00`。因此 prod 仍满足“至少保留一条未来可执行的 workflow 主线入口”的保底要求。
3. 当前 live 真相是“保底巡检 running + 主线 future + 图里没有 queued/ready 节点堆着”。
   `GET /api/status` 在 `2026-04-08T00:24:15+08:00` 返回 `assignment_running_task_count=1`、`queued_task_count=0`；当前唯一 running 节点是 `node-sti-20260408-d5d29c5f`。对应执行批次 `arun-20260408-002055-ce05f6` 的 `run.json` 在 `2026-04-08T00:24:15+08:00` 仍有新事件，说明本轮保底巡检还在真实执行中。
4. 最近一次主线失败已经自动续挂了下一轮。
   `node-sti-20260407-bcbdf11a` 对应的 `run_id=arun-20260407-235044-21c618` 已在 `2026-04-08T00:11:05+08:00` 以 `assignment execution timeout after 1200s` 收口失败，但 `audit.jsonl` 同步记录了 `schedule_self_iteration`；而当前 schedule API 真相也已经收口到 `sch-20260407-20001ab4 -> next_trigger_at=2026-04-08T00:41:00+08:00`。所以这轮不需要再手工补链。

## 证据路径

- `docs/workflow/governance/PM版本推进计划.md`
- `docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`
- `.running/control/envs/prod.json`
- `.running/control/instances/prod.json`
- `.running/control/prod-last-action.json`
- `.running/control/prod-candidate.json`
- `.running/control/runtime/prod/logs/events/schedules.jsonl`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/task.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-d5d29c5f.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260407-bcbdf11a.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-002055-ce05f6/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260407-235044-21c618/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260407-235044-21c618/result.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`

## 下一次建议唤醒

- 主线 next: `sch-20260407-20001ab4 -> 2026-04-08T00:41:00+08:00`
- 保底 next: 当前 `sch-20260407-5ef5e5c8` 仍在执行 `node-sti-20260408-d5d29c5f`；如果 `2026-04-08T00:41:00+08:00` 的主线没有按时建单或没有自动续挂新的保底巡检，建议在 `2026-04-08T00:46:00+08:00` 再做一次保底巡检
- 升级 next: 等当前 `node-sti-20260408-d5d29c5f` 收尾、`running_task_count=0` 且 `/api/runtime-upgrade/status.can_upgrade=true` 后，优先复核一次真相，再直接 `apply 20260408-000353`

- memory_ref: `.codex/memory/2026-04/2026-04-08.md`
