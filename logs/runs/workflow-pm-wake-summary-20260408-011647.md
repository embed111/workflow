# workflow-pm-wake-summary

- generated_at: `2026-04-08T01:16:47+08:00`
- ticket_id: `asg-20260407-103450-fb8ba8`
- node_id: `node-sti-20260408-12f34ca2`
- run_id: `arun-20260408-011150-e30b52`
- graph_name: `任务中心全局主图`
- active_version: `V1`
- active_packages: `V1-P0 / V1-P2`

## 巡检结论

1. 当前不升级。
   `GET /api/runtime-upgrade/status` 在 `2026-04-08T01:15:56+08:00` 返回：`current_version=20260407-200414`、`candidate_version=20260408-005244`、`running_task_count=1`、`can_upgrade=false`、`request_pending=false`、`blocking_reason=存在运行中任务，暂不可升级`。当前唯一 running 节点仍是本轮保底巡检 `node-sti-20260408-12f34ca2`，所以这轮没有调用 `/api/runtime-upgrade/apply`。
2. 当前不补链。
   `01:15` 的 `[持续迭代] workflow` 已经从 future 入口被消费成当前版本任务：`node-sti-20260408-378d2cc8` 在 `2026-04-08T01:15:08+08:00` 建单，节点文件显示 `status=ready`；`/api/status` 在 `2026-04-08T01:15:56+08:00` 也显示 `workflow` 当前为 `1 running + 1 queued/ready`。因此 prod 仍保有可执行的主线接力，这轮无需手工补链。
3. 当前 live 真相已经从“保留 future trigger”切到“保底巡检 running + 主线 ready + 升级门禁仍关闭”。
   `schedules.jsonl` 在 `2026-04-08T01:15:07~01:15:56+08:00` 连续记录了 `trigger_hit -> create_assignment_node -> dispatch_requested -> trigger_resume_requested -> recover_assignment_node`，对应的 schedule API 也把 `sch-20260407-20001ab4` 更新成 `last_result_status=queued`、`last_result_node_id=node-sti-20260408-378d2cc8`。这说明主线没有断，只是当前槽位仍被本轮巡检占用。
4. 当前 assignment graph 没有堆出新的异常状态。
   `task.json` 仍是 `scheduler_state=running`；当前 `run_id=arun-20260408-011150-e30b52` 的 `run.json` 在 `2026-04-08T01:16:47+08:00` 仍有新事件，说明本轮保底巡检还在真实执行；而新主线节点 `node-sti-20260408-378d2cc8` 还停在 `ready`，没有被误标成失败或消失。

## 证据路径

- `docs/workflow/governance/PM版本推进计划.md`
- `docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`
- `.running/control/envs/prod.json`
- `.running/control/instances/prod.json`
- `.running/control/prod-last-action.json`
- `.running/control/prod-candidate.json`
- `.running/control/runtime/prod/logs/events/schedules.jsonl`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/task.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-12f34ca2.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-378d2cc8.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-e3941a63.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-011150-e30b52/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-004148-2ef29a/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-004148-2ef29a/result.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`

## 下一次建议唤醒

- 主线 next: 当前可执行主线已经转成 `node-sti-20260408-378d2cc8 (ready)`；等 `node-sti-20260408-12f34ca2` 释放 running 槽后，优先观察它是否被自动 dispatch
- 保底 next: 如果当前 `running + ready` 这组接力在 `2026-04-08T01:20:00+08:00` 前还没有自动续挂新的 future/ready 入口，建议在 `2026-04-08T01:20:00+08:00` 再做一次保底巡检
- 升级 next: 等当前 running 槽释放后，立刻复核 `/api/runtime-upgrade/status`；只有在 `running_task_count=0` 且 `can_upgrade=true` 时，才直接 `apply 20260408-005244`

- memory_ref: `.codex/memory/2026-04/2026-04-08.md`
