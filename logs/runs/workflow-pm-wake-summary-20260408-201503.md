# workflow-pm-wake-summary

- checked_at: `2026-04-08T20:15:03+08:00`
- ticket_id: `asg-20260407-103450-fb8ba8`
- node_id: `node-sti-20260408-90ac411d`
- run_id: `arun-20260408-200719-d53b1f`
- memory_ref: `.codex/memory/2026-04/2026-04-08.md`
- active_version: `V1`
- active_task_packages: `V1-P1 / V1-P2 / V1-P3 / V1-P4`
- current_lane: `测试探测`
- lifecycle_stage: `基于基线测试`

## 巡检结论

1. 当前不升级。
   - live `prod` 的 `/api/runtime-upgrade/status` 返回 `current=candidate=20260408-191653`、`candidate_is_newer=false`、`running_task_count=1`、`can_upgrade=false`。
   - 按任务要求排除当前巡检节点 `node-sti-20260408-90ac411d` 后，升级门禁收口为 `running_task_count=0`、`blocking_reason=no_candidate`、`can_upgrade=false`；说明当前不是被别的 helper 占槽卡住，而是已经没有更高 candidate。
   - `.running/control/envs/prod.json`、`.running/control/instances/prod.json` 与 `.running/control/prod-last-action.json` 也一致确认 live 版本已经是 `20260408-191653`。
2. 当前不补链。
   - `[持续迭代] workflow` 的主线 schedule `sch-20260407-20001ab4` 当前 `future_triggers=[]`，保底 schedule `sch-20260407-5ef5e5c8` 也没有新的 future。
   - 但 checklist 允许“补一条未来可执行入口或当前版本任务”；当前版本主线入口已经以 `node-sti-20260408-eaa62c26` 的 `ready` 节点存在，因此这轮不需要手工补 schedule。
   - 当前至少保留了 1 条可继续执行的 workflow 主线入口，done_definition 仍满足。
3. 当前 live 真相已收口为 `1 running / 5 ready`。
   - 当前唯一 running 节点：`workflow -> node-sti-20260408-90ac411d`
   - 当前 mainline ready 节点：`workflow -> node-sti-20260408-eaa62c26`
   - 当前四条 helper ready 节点：
     - `workflow_bugmate -> node-20260408-201227-3f596e`
     - `workflow_devmate -> node-20260408-201236-6bf549`
     - `workflow_testmate -> node-20260408-201247-fef362`
     - `workflow_qualitymate -> node-20260408-201257-454c6d`
   - `/api/status` 返回 `assignment_workboard_summary.active_agent_count=5`、`running_task_count=1`、`queued_task_count=5`
   - `/api/assignments/asg-20260407-103450-fb8ba8/graph` 返回 `status_counts.running=1`、`status_counts.ready=5`
4. 当前最该推进的泳道已切回 `测试探测 / 基于基线测试`。
   - baseline 已经是 live `prod=20260408-191653`
   - 当前不存在更高 candidate，需要先围绕 `191653` 做 smoke、质量巡检、缺陷复核和 helper 收尾鲁棒性验证
5. 当前仍有一条明确风险需要继续盯。
   - default `GET /api/assignments/asg-20260407-103450-fb8ba8/status-detail` 仍默认选中旧失败节点 `node-sti-20260407-8d910bd6`
   - 显式带 `?node_id=node-sti-20260408-90ac411d` 才能看到当前 running 巡检节点；这条 `V1-P1` 真相源分叉还没有完全收口

## 核验范围

- `docs/workflow/governance/PM版本推进计划.md`
- `docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`
- `GET /healthz`
- `GET /api/status`
- `GET /api/runtime-upgrade/status`
- `GET /api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260407-103450-fb8ba8&exclude_assignment_node_id=node-sti-20260408-90ac411d`
- `GET /api/schedules/sch-20260407-20001ab4`
- `GET /api/schedules/sch-20260407-5ef5e5c8`
- `GET /api/assignments/asg-20260407-103450-fb8ba8/graph`
- `GET /api/assignments/asg-20260407-103450-fb8ba8/status-detail`
- `GET /api/assignments/asg-20260407-103450-fb8ba8/status-detail?node_id=node-sti-20260408-90ac411d`

## 证据路径

- `logs/runs/workflow-pm-wake-summary-20260408-201503.md`
- `workflow-pm-wake-summary.md`
- `state/session-snapshot.md`
- `docs/workflow/governance/PM版本推进计划.md`
- `.codex/memory/2026-04/2026-04-08.md`
- `.running/control/envs/prod.json`
- `.running/control/instances/prod.json`
- `.running/control/prod-last-action.json`
- `.running/control/prod-candidate.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-200719-d53b1f/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-90ac411d.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-eaa62c26.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-20260408-201227-3f596e.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-20260408-201236-6bf549.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-20260408-201247-fef362.json`
- `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-20260408-201257-454c6d.json`

## 下一次建议唤醒时间

- 主线 next: `node-sti-20260408-eaa62c26 (ready)`，等当前 `node-sti-20260408-90ac411d` 释放 running 槽后自动接棒
- 保底 next: 如果到 `2026-04-08T20:25:00+08:00` 仍未出现新的 `future/ready` 入口，或 `node-sti-20260408-eaa62c26` 仍未 dispatch，建议在该时刻再做一次保底巡检
- 泳道/阶段 next: `测试探测 / 基于基线测试`
