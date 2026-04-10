# Workflow PM Wake Summary

- ticket_id: `asg-20260407-103450-fb8ba8`
- node_id: `node-sti-20260408-cad685a9`
- generated_at: `2026-04-08T07:46:25+08:00`
- memory_ref: `.codex/memory/2026-04/2026-04-08.md`

## 本次结论
- 截至 `2026-04-08T07:46:25+08:00`，live `prod` 仍是 `20260407-200414`，`candidate=20260408-073535`；`/api/runtime-upgrade/status` 返回 `running_task_count=1`、`can_upgrade=false`、`blocking_reason=存在运行中任务，暂不可升级`，所以这轮不执行 `POST /api/runtime-upgrade/apply`。
- 当前唯一 active `running` 节点就是本轮保底巡检 `node-sti-20260408-cad685a9`。`/api/status`、`C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-cad685a9.json` 与 `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-074134-4e9614/run.json` 一致显示当前运行槽正被本轮占用。
- 主链没有断。`07:19` 的 `[持续迭代] workflow` 节点 `node-sti-20260408-54d72aab` 已在 `2026-04-08T07:41:27+08:00` 因 `assignment execution timeout after 1200s` 失败；随后 audit `aaud-20260408-074251-187b03` 与 `/api/schedules` 已把下一次主线/保底入口续挂为 `2026-04-08T08:12:00+08:00 / 2026-04-08T08:42:00+08:00`，因此这轮不需要补链。
- `candidate=20260408-073535` 已经存在，且 `.running/control/reports/test-gate-20260408-073535.json` 结果为 `passed`；但只要当前 running 槽未释放，现网仍继续 fail-closed，不提前升级。

## 关键证据
- API:
  - `http://127.0.0.1:8090/healthz`
  - `http://127.0.0.1:8090/api/status`
  - `http://127.0.0.1:8090/api/runtime-upgrade/status`
  - `http://127.0.0.1:8090/api/schedules/sch-20260407-20001ab4`
  - `http://127.0.0.1:8090/api/schedules/sch-20260407-5ef5e5c8`
- 控制文件:
  - `.running/control/envs/prod.json`
  - `.running/control/instances/prod.json`
  - `.running/control/prod-last-action.json`
  - `.running/control/prod-candidate.json`
  - `.running/control/reports/test-gate-20260408-073535.json`
- 任务与运行真相:
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/task.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-cad685a9.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260408-54d72aab.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-074134-4e9614/run.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-072023-8f6844/run.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260408-072023-8f6844/result.json`
  - `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`
  - `.running/control/runtime/prod/logs/events/schedules.jsonl`

## 风险提示
- `sch-20260407-5ef5e5c8` 在 `2026-04-08T07:22:08+08:00 ~ 2026-04-08T07:40:55+08:00` 间仍反复出现 `dispatch_requested -> trigger_resume_requested -> recover_assignment_node`，直到 `07:43:01+08:00` 才在 schedule 事件里收口为 `running`。这轮没有造成断链，但说明旧 `prod` 上的保底 dispatch 稳定性仍未完全收住。

## 下一步
- 主线 next: `sch-20260407-20001ab4 -> 2026-04-08T08:12:00+08:00`
- 保底 next: `sch-20260407-5ef5e5c8 -> 2026-04-08T08:42:00+08:00`
- 升级 next: 等 `node-sti-20260408-cad685a9` 收尾后立即复核 `/api/runtime-upgrade/status`；仅当 `running_task_count=0` 且 `can_upgrade=true` 时，直接 apply `20260408-073535`
