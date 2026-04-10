# workflow-pm-wake-summary

- preference_ref: state/user-preferences.md
- delta_observation: 2026-04-07 21:07 这轮保底巡检不只要判断能否升级，还要在 `[持续迭代] workflow` 的 `next_trigger_at` 被消费为空后，确认主线是否仍有可执行入口，并在必要时补挂明确的 future 保底时间。
- delta_validation: 我已读取 `docs/workflow/governance/PM版本推进计划.md`、`docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`，并交叉核对 `/api/status`、`/api/runtime-upgrade/status`、`/api/schedules`、`C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260407-3ec1c5ec.json`、`C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260407-101db522.json`、`C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260407-210748-60d88b/run.json`、`C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`、`.running/control/envs/prod.json`、`.running/control/instances/prod.json`、`.running/control/prod-last-action.json` 与 `.running/control/runtime/prod/logs/events/schedules.jsonl`。由于当前仍有运行中任务，我没有调用 `/api/runtime-upgrade/apply`；同时已通过 `POST /api/schedules/sch-20260407-5ef5e5c8` 把下一次保底巡检重挂到 `2026-04-07T21:37:00+08:00`，审计留痕为 `saud-20260407-1433d722`。

## 巡检结论

- `V1` 仍是当前 active 版本，当前优先任务包仍是 `V1-P0 / V1-P1`。
- 截至 `2026-04-07T21:16:36+08:00`，prod 仍运行在 `20260407-200414`；候选版本是 `20260407-204710`，但 `/api/runtime-upgrade/status` 返回 `running_task_count=1`、`can_upgrade=false`、`blocking_reason=存在运行中任务，暂不可升级`，因此这轮没有执行无痛升级。
- 当前主链未断。`node-sti-20260407-3ec1c5ec` 正在 `running`，`node-sti-20260407-101db522` 已处于 `ready`，所以即使 `[持续迭代] workflow` 的 schedule 在 `21:07` 命中后把 `next_trigger_at` 消耗为空，任务中心里仍保留了一条当前版本可执行入口。
- 我额外挂了一条明确 future 保底入口：`sch-20260407-5ef5e5c8 -> next_trigger_at=2026-04-07T21:37:00+08:00`。现在 prod 真相是 `1 running + 1 ready + 1 future backup`，满足“主链不断 + 保底仍可接力”。
- 当前最值得继续盯的风险不是升级，而是 `node-sti-20260407-101db522` 一直停在 `ready`。`schedules.jsonl` 在 `2026-04-07T21:11:39+08:00` 到 `2026-04-07T21:16:33+08:00` 之间多次记录 `dispatch_requested -> trigger_resume_requested -> recover_assignment_node`，但节点仍未真正进入 `running`；下一轮应优先追这条 dispatch/recover 循环。

## 证据路径

- `docs/workflow/governance/PM版本推进计划.md`
- `docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`
- `.running/control/envs/prod.json`
- `.running/control/instances/prod.json`
- `.running/control/prod-last-action.json`
- `.running/control/runtime/prod/logs/events/schedules.jsonl`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260407-3ec1c5ec.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260407-101db522.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260407-210748-60d88b/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260407-210748-60d88b/events.log`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`
- `/api/status`
- `/api/runtime-upgrade/status`
- `/api/schedules`
- `/api/schedules/sch-20260407-5ef5e5c8`
- `/api/schedules/sch-20260407-20001ab4`

## 下一次建议唤醒时间

- 主线 next: `node-sti-20260407-101db522` 已在 `2026-04-07T21:07:00+08:00` 进入 `ready`，待当前保底巡检收尾后应立即具备执行条件。
- 保底 next: `sch-20260407-5ef5e5c8 -> 2026-04-07T21:37:00+08:00`
- 建议观察点: 若到 `2026-04-07T21:37:00+08:00` 前，`node-sti-20260407-101db522` 仍持续停在 `ready`，下一轮直接追 `dispatch_requested / trigger_resume_requested / recover_assignment_node` 的循环原因，而不是重复补链。
- memory_ref: `.codex/memory/2026-04/2026-04-07.md`
