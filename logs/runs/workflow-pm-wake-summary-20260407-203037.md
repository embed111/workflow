# workflow-pm-wake-summary

- preference_ref: state/user-preferences.md
- delta_observation: 2026-04-07 20:26 这轮保底巡检要求我只按 live prod 真相决定是否升级、是否补链，并把下一次主线时间写清楚。
- delta_validation: 我已读取 `docs/workflow/governance/PM版本推进计划.md`、`docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`，并交叉核对 `/api/status`、`/api/runtime-upgrade/status`、`/api/schedules`、`/api/assignments/asg-20260407-103450-fb8ba8/graph`、`/api/assignments/asg-20260407-103450-fb8ba8/status-detail?node_id=node-sti-20260407-6085ec1f`、`.running/control/envs/prod.json`、`.running/control/instances/prod.json`、`.running/control/prod-last-action.json`、`C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260407-6085ec1f.json`、`C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260407-202650-c24346/run.json` 与 `events.log`。

## 巡检结论

- `V1` 仍是 active 版本，当前优先任务包仍是 `V1-P0 / V1-P1`。
- 截至 `2026-04-07T20:30:37+08:00`，prod 版本是 `20260407-200414`，`/api/status` 与 `/api/runtime-upgrade/status` 都显示 `running_task_count=1`，当前保底节点 `node-sti-20260407-6085ec1f` 正在运行，所以本轮不满足无痛升级条件，也没有调用 `/api/runtime-upgrade/apply`。
- `[持续迭代] workflow` 仍保留 future 入口 `sch-20260407-20001ab4 -> next_trigger_at=2026-04-07T20:37:00+08:00`，全局主图 `asg-20260407-103450-fb8ba8` 当前是 `17` 节点、`1 running / 0 ready`，因此主链未断，本轮无需现场补链。
- 当前保底巡检 schedule `sch-20260407-5ef5e5c8` 已于 `2026-04-07T20:26:00+08:00` 命中，并以 `run_id=arun-20260407-202650-c24346` 真实执行；文件真相与 API 真相一致。

## 证据路径

- `docs/workflow/governance/PM版本推进计划.md`
- `docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`
- `.running/control/envs/prod.json`
- `.running/control/instances/prod.json`
- `.running/control/prod-last-action.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260407-6085ec1f.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260407-202650-c24346/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260407-202650-c24346/events.log`
- `/api/status`
- `/api/runtime-upgrade/status`
- `/api/schedules`
- `/api/assignments/asg-20260407-103450-fb8ba8/graph`
- `/api/assignments/asg-20260407-103450-fb8ba8/status-detail?node_id=node-sti-20260407-6085ec1f`

## 下一次建议唤醒时间

- 主线 next: `2026-04-07T20:37:00+08:00`
- 保底观察点: `2026-04-07T20:37:00+08:00` 主线命中后立即复核；若届时 `[持续迭代] workflow` 未续挂新的 future 入口，再现场补一条新的 `pm持续唤醒 - workflow 主线巡检`
- memory_ref: `.codex/memory/2026-04/2026-04-07.md`
