# workflow 连续迭代运行摘要 2026-04-08 17:42:59

## 结论
- live `prod` 已是 `20260408-171450`，`/api/runtime-upgrade/status` 返回 `current=candidate=20260408-171450`。
- 当前主线 `node-sti-20260408-8b322e0c` 仍在 `running`；排除该节点后升级门禁收口为 `running_task_count=0 / candidate_is_newer=false / blocking_reason=no_candidate / can_upgrade=false`，所以本轮不执行 `apply`。
- 当前任务图真相为 `1 running + 4 ready + 31 succeeded + 33 failed`；我已把 `V1-P1 / V1-P2 / V1-P3 / V1-P4` 分别续挂成新的 `ready` 节点。
- 保底唤醒 `sch-20260407-5ef5e5c8` 仍保留 `2026-04-08T17:49:00+08:00`，7x24 接力未断。

## 本轮动作
- 复核 `healthz`、`/api/status`、`/api/runtime-upgrade/status`、两条 schedule detail、任务图和 `status-detail`。
- 确认 live `prod` 当前版本、上一轮升级动作和当前 running 主线都已一致落到 `20260408-171450`。
- 不继续修改 `.repository/pm-main` 代码，避免当前主线还在运行时触发新的 candidate/apply 路径。
- 在全局主图续挂 4 个 fresh ready 节点：
  - `node-20260408-173431-adfdb4` `V1-P1 helper 启动瞬断复核 / 2026-04-08 17:21:00`
  - `node-20260408-173453-8f522a` `V1-P2 helper 续挂与交付鲁棒性 / 2026-04-08 17:21:00`
  - `node-20260408-173601-4cde2d` `V1-P3 7x24 当前版回归 smoke / 2026-04-08 17:21:00`
  - `node-20260408-173602-8e68b6` `V1-P4 prod 171450 质量巡检 / 2026-04-08 17:21:00`

## 现场风险
- `status-detail` 默认查询仍会选到旧失败节点 `node-sti-20260407-8d910bd6`，而不是当前 running 的 `node-sti-20260408-8b322e0c`；这条默认节点选择逻辑仍属于 `V1-P1` 的真相源缺口。
- 当前主线 schedule `sch-20260407-20001ab4` 已从 future 入口转成当前 running 节点，因此 `next_trigger_at` 为空；当前可依赖的未来入口是保底 `2026-04-08T17:49:00+08:00` 和 4 个 ready helper 节点。

## 证据
- API:
  - `GET http://127.0.0.1:8090/healthz`
  - `GET http://127.0.0.1:8090/api/status`
  - `GET http://127.0.0.1:8090/api/runtime-upgrade/status`
  - `GET http://127.0.0.1:8090/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260407-103450-fb8ba8&exclude_assignment_node_id=node-sti-20260408-8b322e0c`
  - `GET http://127.0.0.1:8090/api/schedules/sch-20260407-20001ab4`
  - `GET http://127.0.0.1:8090/api/schedules/sch-20260407-5ef5e5c8`
  - `GET http://127.0.0.1:8090/api/assignments/asg-20260407-103450-fb8ba8/graph`
  - `GET http://127.0.0.1:8090/api/assignments/asg-20260407-103450-fb8ba8/status-detail`
  - `GET http://127.0.0.1:8090/api/assignments/asg-20260407-103450-fb8ba8/status-detail?node_id=node-sti-20260408-8b322e0c`
- 控制文件:
  - `.running/control/envs/prod.json`
  - `.running/control/prod-last-action.json`
- 任务文件:
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-8b322e0c.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-20260408-173431-adfdb4.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-20260408-173453-8f522a.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-20260408-173601-4cde2d.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-20260408-173602-8e68b6.json`

## 下一步
- 主线继续观察 `node-sti-20260408-8b322e0c` 的收尾与自动续挂。
- 保底继续依赖 `sch-20260407-5ef5e5c8 -> 2026-04-08T17:49:00+08:00`。
- 当前 active 版本继续优先收 `V1-P1` 的 detail 真相源分叉，同时等待 `V1-P2 / V1-P3 / V1-P4` 的 fresh ready 节点接力执行。

- memory_ref: `.codex/memory/2026-04/2026-04-08.md`
