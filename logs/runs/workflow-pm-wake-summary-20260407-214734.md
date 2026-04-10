# workflow-pm-wake-summary

- preference_ref: state/user-preferences.md
- delta_observation: 这轮 `21:37` 保底巡检要求我只按 live prod 真相判断是否升级或补链，而且你依然需要从记忆里的 `next` 直接看出主线/保底有没有继续滚动。
- delta_validation: 我已读取 `docs/workflow/governance/PM版本推进计划.md`、`docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`，并交叉核对 `/healthz`、`/api/status`、`/api/runtime-upgrade/status`、`/api/schedules`、`.running/control/envs/prod.json`、`.running/control/instances/prod.json`、`.running/control/prod-last-action.json`、`C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/task.json`、`C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260407-a7fd93ea.json`、`C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260407-cb9fc7de.json`、`C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260407-101db522.json`、`C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260407-214401-a33916/run.json`、`C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260407-212312-7e0bee/run.json`、`C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl` 与 `.running/control/runtime/prod/logs/events/schedules.jsonl`。其中 assignment graph / status-detail HTTP 接口在本轮 20 秒窗口内仍会超时，所以我回退到 task/nodes/runs/audit 文件真相；这些文件与 `/api/status`、`/api/schedules` 的结果一致。

## 巡检结论

- 截至 `2026-04-07T21:47:34+08:00`，`prod` 仍运行在 `20260407-200414`，候选版本是 `20260407-213849`；`/api/runtime-upgrade/status` 返回 `running_task_count=1`、`can_upgrade=false`、`blocking_reason=存在运行中任务，暂不可升级`，所以本轮没有调用 `/api/runtime-upgrade/apply`。
- 当前主链没有断。任务中心真相是 `node-sti-20260407-a7fd93ea=running`、`node-sti-20260407-cb9fc7de=ready`，同时两条 schedule 已自动续挂 future 入口：`sch-20260407-20001ab4 -> 2026-04-07T22:14:00+08:00`，`sch-20260407-5ef5e5c8 -> 2026-04-07T22:44:00+08:00`。
- 这意味着当前已经同时保留了 `running + ready + future` 三层接力，所以本轮不需要再人工补链；done_definition 里的“prod 至少保留一条未来可执行的 workflow 主线入口”已经满足。
- `21:07` 那轮 `[持续迭代] workflow` 节点 `node-sti-20260407-101db522` 已在 `2026-04-07T21:45:01+08:00` 被系统按 `运行句柄缺失或 workflow 已重启，请手动重跑。` 收口失败；对应 run `arun-20260407-212312-7e0bee` 先在 `2026-04-07T21:43:51+08:00` 记录了 `assignment execution timeout after 1200s`，随后 audit 又把下一轮主线/保底时间续挂到了 `22:14:00 / 22:44:00`。
- 当前更值得继续盯的 live 风险不是“未来入口缺失”，而是 `node-sti-20260407-cb9fc7de` 这条 `ready` 主线何时真正 dispatch；如果当前 `running` 节点收尾后它仍不进入 `running`，下一轮应继续追 `dispatch_requested / trigger_resume_requested / recover_assignment_node` 的循环真相。

## 证据路径

- `docs/workflow/governance/PM版本推进计划.md`
- `docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`
- `.running/control/envs/prod.json`
- `.running/control/instances/prod.json`
- `.running/control/prod-last-action.json`
- `.running/control/runtime/prod/logs/events/schedules.jsonl`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/task.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260407-a7fd93ea.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260407-cb9fc7de.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260407-101db522.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260407-214401-a33916/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260407-212312-7e0bee/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`
- `/healthz`
- `/api/status`
- `/api/runtime-upgrade/status`
- `/api/schedules`

## 下一次建议唤醒时间

- 主线 next: `sch-20260407-20001ab4 -> 2026-04-07T22:14:00+08:00`
- 保底 next: `sch-20260407-5ef5e5c8 -> 2026-04-07T22:44:00+08:00`
- 当前运行节点: `node-sti-20260407-a7fd93ea`
- 当前待开始节点: `node-sti-20260407-cb9fc7de`
- 建议观察点: 如果 `node-sti-20260407-cb9fc7de` 在当前 `running` 节点收尾后仍不 dispatch，下一轮直接继续拆 `dispatch_requested / trigger_resume_requested / recover_assignment_node` 的 live 行为，而不是重复补链。
- memory_ref: `.codex/memory/2026-04/2026-04-07.md`
