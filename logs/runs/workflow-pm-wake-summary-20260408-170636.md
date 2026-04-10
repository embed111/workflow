# workflow-pm-wake-summary

- checked_at: `2026-04-08T17:06:36+08:00`
- ticket_id: `asg-20260407-103450-fb8ba8`
- node_id: `node-sti-20260408-4d7d733f`
- run_id: `arun-20260408-170020-2f88cd`
- memory_ref: `.codex/memory/2026-04/2026-04-08.md`

## 巡检结论

1. 当前不升级。
   - live `prod` 已是 `20260408-164211`，`/api/runtime-upgrade/status` 返回 `current=candidate=20260408-164211`、`running_task_count=1`、`can_upgrade=false`。
   - 按任务要求排除当前巡检节点后，升级门禁收口为 `running_task_count=0`、`candidate_is_newer=false`、`blocking_reason=no_candidate`、`can_upgrade=false`，说明当前没有更高 candidate 可升，所以这轮不 `apply`。
2. 当前不补链。
   - `[持续迭代] workflow` 的主线 schedule `sch-20260407-20001ab4` 仍为 `enabled=true`，且 `next_trigger_at=2026-04-08T17:19:00+08:00`。
   - 当前保底 schedule `sch-20260407-5ef5e5c8` 已在 `2026-04-08T17:00:00+08:00` 命中并拉起本轮节点，done_definition 已满足。
3. 当前 live 真相是“保底巡检 running + 主线 future”。
   - 当前唯一 active 非终态节点：`node-sti-20260408-4d7d733f`
   - 当前 run：`arun-20260408-170020-2f88cd`
   - `run.json` 显示 `status=running`、`updated_at=2026-04-08T17:04:51+08:00`、`provider_pid=25340`
   - `Win32_Process` 显示 `provider_pid=25340` 对应 `node.exe`，命令行为 `node .../@openai/codex/bin/codex.js exec ...`

## 核验范围

- `docs/workflow/governance/PM版本推进计划.md`
- `docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`
- `GET /healthz`
- `GET /api/status`
- `GET /api/runtime-upgrade/status`
- `GET /api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260407-103450-fb8ba8&exclude_assignment_node_id=node-sti-20260408-4d7d733f`
- `GET /api/schedules`
- `GET /api/schedules/sch-20260407-20001ab4`
- `GET /api/schedules/sch-20260407-5ef5e5c8`

## 证据路径

- `logs/runs/workflow-pm-wake-summary-20260408-170636.md`
- `state/session-snapshot.md`
- `docs/workflow/governance/PM版本推进计划.md`
- `.codex/memory/2026-04/2026-04-08.md`
- `.running/control/envs/prod.json`
- `.running/control/instances/prod.json`
- `.running/control/prod-last-action.json`
- `.running/control/prod-candidate.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/task.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-4d7d733f.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-170020-2f88cd/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-170020-2f88cd/events.log`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`
- `.running/control/runtime/prod/logs/events/schedules.jsonl`

## 下一次建议唤醒时间

- 主线 next: `sch-20260407-20001ab4 -> 2026-04-08T17:19:00+08:00`
- 保底 next: 当前 `sch-20260407-5ef5e5c8` 的 `2026-04-08T17:00:00+08:00` 这轮仍在运行，尚未自动续挂新的 future trigger
- 建议补看 next: 如果 `2026-04-08T17:19:00+08:00` 主线没有按时建单，或当前巡检节点收尾后仍没有新的保底入口，建议在 `2026-04-08T17:24:00+08:00` 再做一次保底巡检
