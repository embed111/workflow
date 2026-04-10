# workflow-pm-wake-summary

- checked_at: `2026-04-08T21:43:13+08:00`
- ticket_id: `asg-20260407-103450-fb8ba8`
- node_id: `node-sti-20260408-b3f07178`
- run_id: `arun-20260408-213311-c43ce6`
- memory_ref: `.codex/memory/2026-04/2026-04-08.md`
- active_version: `V1`
- active_task_packages: `V1-P1 / V1-P2 / V1-P3 / V1-P4`
- current_lane: `测试探测`
- lifecycle_stage: `基于基线测试`

## 巡检结论

1. 当前不升级。
   - live `prod` 的 `/api/runtime-upgrade/status` 返回 `current=candidate=20260408-211517`、`candidate_is_newer=false`、`running_task_count=5`、`can_upgrade=false`。
   - 按任务要求排除当前巡检节点 `node-sti-20260408-b3f07178` 后，升级门禁收口为 `running_task_count=4`、`blocking_reason=running_tasks_present`、`can_upgrade=false`；说明现在不是“只有我这轮巡检占槽”，而是 4 条 helper 也已经真实接力。
   - `.running/control/envs/prod.json`、`.running/control/instances/prod.json` 与 `.running/control/prod-last-action.json` 一致确认 live 版本已经是 `20260408-211517`。
2. 当前不补链。
   - `[持续迭代] workflow` 的当前主线入口已经以 `node-sti-20260408-3e42b807` 的 `ready` 节点保留在全局主图里。
   - 两条 once schedule 也都还在：`sch-20260407-20001ab4 -> 2026-04-08T22:02:00+08:00`，`sch-20260407-5ef5e5c8 -> 2026-04-08T22:32:00+08:00`。
   - 当前同时具备 `ready 主线 + future 主线 + future 保底` 三层出口，done_definition 继续满足。
3. 当前 live 真相已收口为 `5 running / 1 queued`。
   - `workflow -> node-sti-20260408-b3f07178 -> arun-20260408-213311-c43ce6`
   - `workflow_bugmate -> node-20260408-213902-67c377 -> arun-20260408-214050-6c6293`
   - `workflow_devmate -> node-20260408-213915-365d03 -> arun-20260408-214114-e09a24`
   - `workflow_testmate -> node-20260408-214023-b639b9 -> arun-20260408-214137-700022`
   - `workflow_qualitymate -> node-20260408-214036-ba519d -> arun-20260408-214201-60c0b4`
   - 当前唯一 queued 主线节点：`workflow -> node-sti-20260408-3e42b807`
   - `/api/status` 已回写 `assignment_workboard_summary.running_task_count=5`、`queued_task_count=1`。
4. 当前最该推进的泳道仍是 `测试探测 / 基于基线测试`。
   - baseline 已经是 live `prod=20260408-211517`。
   - 我已经把 `V1-P1 / V1-P2 / V1-P3 / V1-P4` 的四条 fresh helper 任务重新挂到同一条基线下，并全部推进到真实运行，当前版本没有空转。
5. 当前还暴露出一条新的运维级风险。
   - 我第一次用 PowerShell 直接把 `ConvertTo-Json` 的字符串 body 发给 `POST /api/assignments/{ticket_id}/nodes` 时，`workflow_bugmate / workflow_devmate` 这两条新节点的中文 `node_name / node_goal` 被 live API 写成了 `?`。
   - 第二次改成 `UTF-8` 字节 body 后，`workflow_testmate / workflow_qualitymate` 的中文字段恢复正常；因此这轮不用再补节点，但后续手工建单必须按 UTF-8 bytes 调接口。

## 核验范围

- `docs/workflow/governance/PM版本推进计划.md`
- `docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`
- `GET /healthz`
- `GET /api/status`
- `GET /api/runtime-upgrade/status`
- `GET /api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260407-103450-fb8ba8&exclude_assignment_node_id=node-sti-20260408-b3f07178`
- `GET /api/schedules`
- `GET /api/assignments/asg-20260407-103450-fb8ba8/graph`
- `POST /api/assignments/asg-20260407-103450-fb8ba8/nodes`
- `POST /api/assignments/asg-20260407-103450-fb8ba8/dispatch-next`

## 证据路径

- `logs/runs/workflow-pm-wake-summary-20260408-214313.md`
- `workflow-pm-wake-summary.md`
- `docs/workflow/governance/PM版本推进计划.md`
- `.codex/memory/2026-04/2026-04-08.md`
- `.codex/experience/runtime-upgrade-and-agent-monitoring.md`
- `.running/control/envs/prod.json`
- `.running/control/instances/prod.json`
- `.running/control/prod-last-action.json`
- `.running/control/prod-candidate.json`
- `.running/control/runtime/prod/logs/events/schedules.jsonl`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-b3f07178.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-3e42b807.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-20260408-213902-67c377.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-20260408-213915-365d03.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-20260408-214023-b639b9.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-20260408-214036-ba519d.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-213311-c43ce6/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-214050-6c6293/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-214114-e09a24/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-214137-700022/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-214201-60c0b4/run.json`

## 下一次建议唤醒时间

- 主线 ready next: `node-sti-20260408-3e42b807`
- 主线 future next: `sch-20260407-20001ab4 -> 2026-04-08T22:02:00+08:00`
- 保底 future next: `sch-20260407-5ef5e5c8 -> 2026-04-08T22:32:00+08:00`
- 泳道/阶段 next: `测试探测 / 基于基线测试`
