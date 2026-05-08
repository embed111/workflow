# workflow 连续迭代留痕 2026-04-11 15:29:17

- active_version: `V1`
- task_package: `V1-P2`
- lane: `工程质量探测`
- lifecycle_stage: `变更控制`
- baseline: `prod=20260411-093051`
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`

## 结论摘要
- `pm-main` 与 `../workflow_code` 继续 `clean_synced(c55e357)`，本轮没有新增代码改动，也没有 commit/push/test/candidate 动作。
- live `prod` 仍在 `20260411-093051` 上运行；`candidate=20260411-131835` 仍待空窗升级。
- 当前执行真相为 `1 running / 2 ready`：主线 `node-sti-20260411-4e89690b / arun-20260411-150604-2052fe` 仍在 `running`，`node-sti-20260411-7fa4dfbe` 与 `node-sti-20260411-9a930f56` 都已处于 `ready`。
- 当前主线 schedule 已在 `15:21` materialize 成 `ready` 节点，不再保留 future；保底 schedule 则继续保留 `sch-20260405-67a89536 -> 2026-04-11T16:21:00+08:00` 的 future。

## 现场判断
- 直接对比 `D:/code/AI/J-Agents/workflow/.running/prod/src/workflow_app/server/services/release_boundary_service.py` 与 `D:/code/AI/J-Agents/workflow/.repository/pm-main/src/workflow_app/server/services/release_boundary_service.py` 后，我确认 live `prod=20260411-093051` 仍带着“相对 origin/main ahead 也算阻塞”的旧 release boundary 语义。
- 这也是为什么当前 `node-sti-20260411-4e89690b` 的 `node_goal / launch_summary_snapshot` 仍是 `clean_synced(c55e357)`，但 schedule plan 正文又会被 live 旧代码回写成 `ahead_clean`。
- 我已在 `2026-04-11T15:20:36+08:00` 用当前工作区模板对 live prod runtime 做一次受支持的 schedule 收口，把两条 schedule 正文重新刷回 `clean_synced ; ahead_count=0 ; push_block_reason=-`。
- `15:21` 主线最初吃到了我第一次 here-string 中文摘要造成的乱码 snapshot；随后我在 `2026-04-11T15:27:55+08:00 ~ 2026-04-11T15:28:42+08:00` 把 `node-sti-20260411-7fa4dfbe` 的 `node_goal` 与 `sti-20260411-7fa4dfbe` 的 snapshot 一并修回正常文案。

## 验证
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260327-223335-b79f27&exclude_assignment_node_id=node-sti-20260411-4e89690b'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules/sch-20260405-56eee156'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules/sch-20260405-67a89536'`
- `Get-Content -Raw 'C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-150604-2052fe/run.json'`
- `Get-Content -Raw 'C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/nodes/node-sti-20260411-7fa4dfbe.json'`
- `Get-Content -Raw 'D:/code/AI/J-Agents/workflow/.running/prod/src/workflow_app/server/services/release_boundary_service.py'`
- `Get-Content -Raw 'D:/code/AI/J-Agents/workflow/.repository/pm-main/src/workflow_app/server/services/release_boundary_service.py'`

## 下一步
- 主线 next: `node-sti-20260411-7fa4dfbe=ready`
- 保底 next: `node-sti-20260411-9a930f56=ready`，schedule future 也已续挂到 `2026-04-11T16:21:00+08:00`
- 升级 next: 当前主线释放后继续看 idle watcher 是否把 `20260411-131835` 接入 live prod
