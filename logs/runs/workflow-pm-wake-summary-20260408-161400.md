# workflow-pm-wake-summary

- checked_at: `2026-04-08T16:14:00+08:00`
- ticket_id: `asg-20260407-103450-fb8ba8`
- node_id: `node-sti-20260408-263917f5`
- memory_ref: `.codex/memory/2026-04/2026-04-08.md`

## 巡检结论

1. 当前不升级。
   - live `prod` 已是 `20260408-154825`，`/api/runtime-upgrade/status` 返回 `current=candidate=20260408-154825`、`running_task_count=1`、`can_upgrade=false`。
   - 按任务要求排除当前巡检节点后，升级门禁收口为 `running_task_count=0`、`candidate_is_newer=false`、`blocking_reason=no_candidate`、`can_upgrade=false`，说明当前没有更高候选可升。
2. 当前不补链。
   - `[持续迭代] workflow` 的主线 schedule `sch-20260407-20001ab4` 仍为 `enabled=true`，且 `next_trigger_at=2026-04-08T16:30:00+08:00`。
   - 本轮保底 schedule `sch-20260407-5ef5e5c8` 已在 `2026-04-08T16:09:00+08:00` 命中并拉起当前节点，done_definition 已满足。
3. 当前 live 真相是“保底巡检 running + 主线 future”。
   - 当前 running 节点：`node-sti-20260408-263917f5`
   - 当前 run：`arun-20260408-160921-24ecc3`
   - `run.json` 显示 `status=running`、`updated_at=2026-04-08T16:13:23+08:00`、`provider_pid=35072`

## 证据路径

- `logs/runs/workflow-pm-wake-summary-20260408-161400.md`
- `state/session-snapshot.md`
- `docs/workflow/governance/PM版本推进计划.md`
- `.codex/memory/2026-04/2026-04-08.md`
- `.running/control/envs/prod.json`
- `.running/control/instances/prod.json`
- `.running/control/prod-last-action.json`
- `.running/control/prod-candidate.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/task.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-263917f5.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-160921-24ecc3/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`
- `.running/control/runtime/prod/logs/events/schedules.jsonl`

## 下一次建议唤醒时间

- 主线 next: `sch-20260407-20001ab4 -> 2026-04-08T16:30:00+08:00`
- 保底 next: 当前 `sch-20260407-5ef5e5c8` 的 `2026-04-08T16:09:00+08:00` 这轮仍在运行，暂时没有新的 future trigger
- 建议补看 next: 如果 `2026-04-08T16:30:00+08:00` 的主线没有按时建单，或当前保底节点收尾后仍没有自动续挂新的保底入口，建议在 `2026-04-08T16:35:00+08:00` 再做一次保底巡检
