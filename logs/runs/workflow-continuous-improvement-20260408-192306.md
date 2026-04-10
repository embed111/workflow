# [持续迭代] workflow / 2026-04-08 19:16:00

## 本轮结论
- active 版本仍是 `V1`；本轮最高价值任务包收口为 `V1-P1`，泳道切到 `工程质量探测`，生命周期阶段切到 `变更控制`。
- 当前 baseline 仍是 live `prod=20260408-180347`；当前受控变更是 `candidate=20260408-191653`，来源于 `pm-main` 提交 `8107c43 fix(workflow): harden assignment terminal recovery and timeout policy`，并已通过 `test-gate-20260408-191653`。
- 这轮不升级：`/api/runtime-upgrade/status` 返回 `current=20260408-180347`、`candidate=20260408-191653`、`running_task_count=5`、`can_upgrade=false`；按任务要求排除当前主线节点 `node-sti-20260408-bd6ab034` 后，门禁仍是 `running_task_count=4 / can_upgrade=false`。
- 当前主链未断：主线节点 `node-sti-20260408-bd6ab034 / arun-20260408-191645-c125d0` 已真实 `provider_start` 并持续写事件；保底 schedule `sch-20260407-5ef5e5c8` 仍保留 `2026-04-08T19:46:00+08:00` future 入口。
- 当前 live `prod` 仍残留一条 `V1-P1` 真相分叉：默认 `status-detail` 还会选到旧失败节点 `node-sti-20260407-8d910bd6`，显式带 `node_id=node-sti-20260408-bd6ab034` 才会显示当前 running 主线。

## 本轮推进
- 我把 `V1-P1` 从“持续排查”收口成了明确的 change-control 状态：baseline 固定为 `180347`，受控变更固定为 `191653`，升级条件固定为“等待当前 5 个 running 节点排空”。
- 我把这轮 live 真相同步写回 `docs/workflow/governance/PM版本推进计划.md`、`state/session-snapshot.md`、`logs/runs/workflow-continuous-improvement-20260408-192306.md` 和今日日记 `.codex/memory/2026-04/2026-04-08.md`，让版本计划、快照、运行报告和记忆保持同一口径。
- 我这轮没有在 `pm-main` 上继续叠加新代码；当前更高价值的是先把 `8107c43 -> test gate -> prod candidate` 这条受控变更与 live 风险边界钉死，避免在 `191653` 尚未入现网前又引入额外变量。

## 当前运行
- `workflow`：`node-sti-20260408-bd6ab034 / arun-20260408-191645-c125d0`
- `workflow_bugmate`：`node-20260408-185605-35144b / arun-20260408-190810-1fc089`
- `workflow_devmate`：`node-20260408-185632-41010f / arun-20260408-190900-d7addb`
- `workflow_testmate`：`node-20260408-185717-67fac0 / arun-20260408-190950-01a75b`
- `workflow_qualitymate`：`node-20260408-185759-b3dfba / arun-20260408-191039-8c1564`

## 风险与下一步
- `status-detail` 默认选中旧失败节点的问题还在 live `prod=180347` 上可见；它是当前 `V1-P1` 最明确的残留真相分叉，必须等 `191653` 升入现网后优先复核。
- 升级 next：只要 `/api/runtime-upgrade/status` 收敛到 `running_task_count=0 && can_upgrade=true`，就直接 `apply 20260408-191653`。
- 主线 next：当前 `node-sti-20260408-bd6ab034` 正在 running；如果它收尾后没有自动续挂新的 `[持续迭代] workflow` future，我要在 `2026-04-08T19:51:00+08:00` 结合保底结果复核并补链。
- 保底 next：`sch-20260407-5ef5e5c8 -> 2026-04-08T19:46:00+08:00`

## 证据路径
- `logs/runs/workflow-continuous-improvement-20260408-192306.md`
- `docs/workflow/governance/PM版本推进计划.md`
- `state/session-snapshot.md`
- `.codex/memory/2026-04/2026-04-08.md`
- `.running/control/prod-candidate.json`
- `.running/control/logs/test/deploy-20260408-191653.json`
- `.running/control/reports/test-gate-20260408-191653.json`
- `.running/control/envs/prod.json`
- `.running/control/instances/prod.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-191645-c125d0/run.json`

- memory_ref: `.codex/memory/2026-04/2026-04-08.md`
