# workflow-pm-wake-summary

- generated_at: `2026-04-07T22:41:54+08:00`
- ticket_id: `asg-20260407-103450-fb8ba8`
- node_id: `node-sti-20260407-dfbed611`
- graph_name: `任务中心全局主图`
- active_version: `V1`
- active_packages: `V1-P0 / V1-P1`

## 巡检结论

1. 当前不升级。
   `GET /api/runtime-upgrade/status` 在 `2026-04-07T22:41:54+08:00` 返回：`current_version=20260407-200414`、`candidate_version=20260407-215842`、`running_task_count=1`、`can_upgrade=false`、`blocking_reason=存在运行中任务，暂不可升级`。本轮未调用 `/api/runtime-upgrade/apply`。
2. 当前不补链。
   `GET /api/schedules/sch-20260407-20001ab4` 仍保留 `[持续迭代] workflow` 的 future 入口：`next_trigger_at=2026-04-07T22:59:00+08:00`。因此 prod 仍满足“至少保留一条未来可执行的 workflow 主线入口”的保底要求。
3. 当前 live 真相是“保底巡检 running + 主线 future”。
   当前保底巡检节点 `node-sti-20260407-dfbed611` 已在 `2026-04-07T22:38:20+08:00` 进入 `running`，对应执行批次 `arun-20260407-223841-8713b3` 在 `2026-04-07T22:40:27+08:00` 仍有 `item.started` 新事件；`/api/status` 同时返回 `assignment_running_task_count=1`。
4. 当前仍有一个需要继续盯的运行真相分叉。
   `.running/control/envs/prod.json` 与 live `healthz`/监听端口都指向 `127.0.0.1:8090`，但 `.running/control/instances/prod.json` 仍写 `port=8098`。这说明 `V1-P0 / V1-P1` 的运行真相一致性还没完全收口，不过它不阻塞本轮“是否升级/是否补链”的判断。

## 证据路径

- `docs/workflow/governance/PM版本推进计划.md`
- `docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`
- `.running/control/envs/prod.json`
- `.running/control/instances/prod.json`
- `.running/control/prod-last-action.json`
- `.running/control/runtime/prod/logs/events/schedules.jsonl`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/task.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260407-dfbed611.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260407-95eee679.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260407-223841-8713b3/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260407-220844-2b92ad/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260407-220844-2b92ad/result.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`

## 下一次建议唤醒

- 主线 next: `sch-20260407-20001ab4 -> 2026-04-07T22:59:00+08:00`
- 保底 next: 当前 `sch-20260407-5ef5e5c8` 的 `2026-04-07T22:38:00+08:00` 这轮已在运行中，暂时没有新的 future trigger
- 升级 next: 等 `running_task_count=0` 且 `/api/runtime-upgrade/status.can_upgrade=true` 后，优先复核一次真相，再直接 `apply 20260407-215842`

- memory_ref: `.codex/memory/2026-04/2026-04-07.md`
