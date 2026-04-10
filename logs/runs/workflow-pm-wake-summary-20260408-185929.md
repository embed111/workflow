# workflow-pm-wake-summary

- checked_at: `2026-04-08T18:59:29+08:00`
- ticket_id: `asg-20260407-103450-fb8ba8`
- node_id: `node-sti-20260408-fb574035`
- run_id: `arun-20260408-185024-9ac17e`
- memory_ref: `.codex/memory/2026-04/2026-04-08.md`
- active_version: `V1`
- active_task_packages: `V1-P0 / V1-P1 / V1-P2 / V1-P3 / V1-P4`
- current_lane: `测试探测`
- lifecycle_stage: `基于基线测试`

## 巡检结论

1. 当前不升级。
   - live `prod` 的 `/api/runtime-upgrade/status` 返回 `current=candidate=20260408-180347`、`running_task_count=1`、`can_upgrade=false`、`blocking_reason=存在运行中任务，暂不可升级`。
   - 按任务要求排除当前巡检节点 `node-sti-20260408-fb574035` 后，升级门禁收口为 `running_task_count=0`、`can_upgrade=false`、`blocking_reason=no_candidate`；说明当前并不是被别的 helper 占槽卡住，而是已经没有更高 candidate。
   - 当前不存在更高候选版本：`candidate_is_newer=false`。
2. 当前不补链。
   - `[持续迭代] workflow` 的主线 schedule `sch-20260407-20001ab4` 仍为 `enabled=true`，`next_trigger_at=2026-04-08T19:16:00+08:00`。
   - 当前保底 schedule `sch-20260407-5ef5e5c8` 正在执行本轮 `node-sti-20260408-fb574035`，因此 `next_trigger_at` 为空属于运行中现场，不是断链。
   - 当前至少保留了 1 条未来可执行的 workflow 主线入口，done_definition 已满足。
3. 已补齐 `V1-P1 ~ V1-P4` 协作泳道。
   - `workflow_bugmate`：`node-20260408-185605-35144b`，`V1-P1 prod 180347 stale终态与detail真相复核 / 2026-04-08 18:53:00`，`ready`
   - `workflow_devmate`：`node-20260408-185632-41010f`，`V1-P2 prod 180347 helper续挂与交付鲁棒性 / 2026-04-08 18:53:00`，`ready`
   - `workflow_testmate`：`node-20260408-185717-67fac0`，`V1-P3 prod 180347 7x24当前版回归smoke / 2026-04-08 18:53:00`，`ready`
   - `workflow_qualitymate`：`node-20260408-185759-b3dfba`，`V1-P4 prod 180347 质量巡检 / 2026-04-08 18:53:00`，`ready`
4. 当前 live 真相已收口为 `1 running / 4 ready / 1 future main`。
   - 当前唯一 running 节点：`workflow -> node-sti-20260408-fb574035`
   - 当前四条 helper 节点都已进图且为 `ready`
   - `/api/status` 返回 `assignment_workboard_summary.active_agent_count=5`、`running_task_count=1`、`queued_task_count=4`
   - `/api/assignments/asg-20260407-103450-fb8ba8/graph` 返回 `status_counts.running=1`、`status_counts.ready=4`

## 核验范围

- `docs/workflow/governance/PM版本推进计划.md`
- `docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`
- `GET /healthz`
- `GET /api/status`
- `GET /api/runtime-upgrade/status`
- `GET /api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260407-103450-fb8ba8&exclude_assignment_node_id=node-sti-20260408-fb574035`
- `GET /api/schedules`
- `GET /api/schedules/sch-20260407-20001ab4`
- `GET /api/schedules/sch-20260407-5ef5e5c8`
- `GET /api/assignments/asg-20260407-103450-fb8ba8/graph`
- `POST /api/assignments/asg-20260407-103450-fb8ba8/nodes` x4

## 证据路径

- `logs/runs/workflow-pm-wake-summary-20260408-185929.md`
- `workflow-pm-wake-summary.md`
- `state/session-snapshot.md`
- `docs/workflow/governance/PM版本推进计划.md`
- `.codex/memory/2026-04/2026-04-08.md`
- `.running/control/envs/prod.json`
- `.running/control/instances/prod.json`
- `.running/control/prod-last-action.json`
- `.running/control/prod-candidate.json`
- `.running/control/runtime/prod/logs/events/schedules.jsonl`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/task.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-fb574035.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-20260408-185605-35144b.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-20260408-185632-41010f.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-20260408-185717-67fac0.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-20260408-185759-b3dfba.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-185024-9ac17e/run.json`

## 下一次建议唤醒时间

- 主线 next: `sch-20260407-20001ab4 -> 2026-04-08T19:16:00+08:00`
- 保底 next: 当前 `node-sti-20260408-fb574035` 正在运行；如果它在主线命中前后收尾，且系统没有自动续挂新的保底 future，建议在 `2026-04-08T19:21:00+08:00` 再做一次保底巡检
- 协作 next: 继续观察 `node-20260408-185605-35144b / node-20260408-185632-41010f / node-20260408-185717-67fac0 / node-20260408-185759-b3dfba` 何时从 `ready` 进入真实 dispatch
