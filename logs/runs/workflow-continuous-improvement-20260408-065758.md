# Continuous Improvement Report

- ticket_id: `asg-20260407-103450-fb8ba8`
- node_id: `node-sti-20260408-bb040ccc`
- generated_at: `2026-04-08T06:57:58+08:00`

## 本轮结论
- 我继续按 `V1` 活跃版本推进，但这轮没有在旧 `prod` 上重复追已经修进 candidate 的 1200 秒固定超时，而是把结论收成“当前 running 槽未释放前继续 fail-closed，等待 `20260408-061833` 接管后再验 live 真相”。
- 截至 `2026-04-08T06:57:58+08:00`，live `prod` 仍是 `20260407-200414`；当前主线节点 `node-sti-20260408-bb040ccc` 对应 `run_id=arun-20260408-065107-e877c7` 仍在运行，`/api/status` 与 `/api/runtime-upgrade/status` 一致返回 `running_task_count=1`、`can_upgrade=false`，所以本轮未执行 `apply`。
- 当前 `prod candidate=20260408-061833` 已经包含两条最关键修复：
  - `0ea5233 fix(workflow): avoid timing out active assignment runs`
  - `26684e1 fix(workflow): request prod upgrade after self-iteration finalize`
- 这版候选也已经通过 `workflow-gate-acceptance-20260408-061716`。因此当前最高优先差异不再是“继续在旧 prod 上追 1200s 墙钟超时”，而是“等待当前节点收尾后让 `20260408-061833` 接管，并验证 live `schedule_total / schedule_workboard_preview` 从旧版 `4` 条 active 计划收口到真实主线 + 保底 `2` 条”。
- 我这轮没有提前续挂 `workflow_bugmate / workflow_devmate / workflow_testmate / workflow_qualitymate` 的真实任务，因为 live prod 还没接到 teammate memory bootstrap 与 self-upgrade loopback；现在补挂只会在旧版本上重复回放已知失败。

## 关键证据
- live 状态：
  - `GET /api/status` => `running_task_count=1`，当前 running 节点 `node-sti-20260408-bb040ccc`
  - `GET /api/runtime-upgrade/status` => `current=20260407-200414`、`candidate=20260408-061833`、`running_task_count=1`、`can_upgrade=false`
  - `GET /api/schedules` => 当前主线 schedule 正在运行、未来保底入口仍保留 `sch-20260407-5ef5e5c8 -> 2026-04-08T07:20:00+08:00`
- run / audit 真相：
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-065107-e877c7/run.json` 仍为 `status=running`，`latest_event_at=2026-04-08T06:58:12+08:00`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl` 最近记录显示 `node-sti-20260408-bb040ccc` 已于 `2026-04-08T06:50:30+08:00` 被真实 dispatch
- candidate 真相：
  - `.running/control/prod-candidate.json` => `version=20260408-061833`
  - `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260408-061716.md` => `runtime_upgrade_self_exclusion / assignment_self_upgrade_loopback / assignment_execution_activity_timeout` 等关键门禁均已通过
  - `git -C .repository/pm-main log --oneline -n 8` => 最新候选包含 `26684e1` 与 `0ea5233`

## 验证
- `Get-Date -Format o`
- `Invoke-RestMethod http://127.0.0.1:8090/api/status`
- `Invoke-RestMethod http://127.0.0.1:8090/api/runtime-upgrade/status`
- `Invoke-RestMethod http://127.0.0.1:8090/api/schedules`
- `Get-Content C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-065107-e877c7/run.json`
- `Get-Content C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl -Tail 12`
- `Get-Content .running/control/prod-candidate.json`
- `git -C .repository/pm-main log --oneline -n 8`
- `Get-Content .repository/pm-main/.test/runs/workflow-gate-acceptance-20260408-061716.md`

## 证据路径
- `logs/runs/workflow-continuous-improvement-20260408-065758.md`
- `docs/workflow/governance/PM版本推进计划.md`
- `state/session-snapshot.md`
- `.codex/memory/2026-04/2026-04-08.md`
- `.running/control/prod-candidate.json`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260408-061716.md`

## 下一步
- 主线 next: 当前 `node-sti-20260408-bb040ccc` 仍在运行，收尾后优先观察旧 prod 是否立刻发起 `request_prod_upgrade -> apply 20260408-061833`
- 保底 next: `sch-20260407-5ef5e5c8 -> 2026-04-08T07:20:00+08:00`
- 升级后验证 next: 若 `20260408-061833` 接管成功，优先复核 live `schedule_total / schedule_workboard_preview` 是否从旧版 `4` 条 active 计划收口到真实主线 + 保底 `2` 条
- 协作 next: 待 `20260408-061833` 接管后，再重跑 `workflow_bugmate / workflow_devmate / workflow_testmate / workflow_qualitymate` 的真实任务，确认 teammate memory bootstrap 已在 live 生效
- memory_ref: `.codex/memory/2026-04/2026-04-08.md`
