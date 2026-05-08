# 7x24 ready-dispatch 非阻塞恢复 - 2026-04-27 14:00

- preference_ref: state/user-preferences.md
- delta_observation: 用户要求“7x24 小时运行又停了，定位根因，补充用例，并恢复运行”；本轮确认故障是 schedule worker 被同步 ready-dispatch 恢复调用卡住。
- delta_validation: 后续若再次出现 `/healthz` 正常但 `schedules.jsonl` 停更，要优先检查 worker 是否被同步副作用阻塞，并复跑 `schedule_ready_dispatch_recovery_nonblocking`。

## 现场
- prod healthz 正常，但 `[持续迭代] workflow` schedule 停在 `last_result_status=queued`，`next_trigger_at=""`。
- 全局主图 `asg-20260327-223335-b79f27` 当时 `running=0 / ready=1 / pending=10`，ready 节点为 `node-sti-20260427-6d194ca4`。
- `.running/control/runtime/prod/logs/events/schedules.jsonl` 在 `2026-04-27T10:51:44+08:00` 后无新 schedule 事件；手工 `POST /api/assignments/asg-20260327-223335-b79f27/dispatch-next` 超时。

## 根因
- `schedule_trigger_runtime._resume_pending_schedule_triggers()` 每轮都会调用 `_recover_stalled_ready_assignment_dispatch()`。
- 旧实现中 `_recover_stalled_ready_assignment_dispatch()` 在 schedule worker 主循环内同步调用 `_request_assignment_dispatch()`。
- 当 dispatch/recovery 路径卡住时，HTTP 服务仍在线，但 schedule worker 主循环被阻塞，导致 7x24 主线不再继续扫描、恢复或补派发。

## 止血恢复
- 仅重启 prod Python 子进程，保留 supervisor；supervisor 自动拉起 prod。
- 重启后 schedule worker 自动补派发旧 ready 节点。
- 恢复回读：
  - `healthz`: `ok=true / ts=2026-04-27T13:56:53+08:00`
  - `node-sti-20260427-6d194ca4`: `run_status=running / run_id=arun-20260427-132220-6633ce / provider_pid=38632 / execution_truth=live_execution`
  - `/api/runtime-upgrade/status`: `ghost_running_detected=false`

## 修复
- 代码提交：`.repository/pm-main@dc9ab6a`，已 fast-forward 同步到 `../workflow_code/main`。
- 关键改动：
  - `src/workflow_app/server/services/schedule_ready_dispatch_runtime.py`
  - `scripts/acceptance/verify_schedule_ready_dispatch_recovery.py`
  - `scripts/acceptance/verify_schedule_ready_dispatch_recovery_nonblocking.py`
  - `scripts/acceptance/workflow_gate_probe_registry.py`
- 行为变化：
  - ready-dispatch recovery 只在 worker 主循环里完成老化判断与 `ready_dispatch_recovery_requested` 留痕。
  - 真实 `_request_assignment_dispatch()` 改到 daemon 后台线程执行。
  - 同一 `root + ticket_id` 只允许一个 recovery dispatch 线程在飞，避免重复补派发。
  - 后台线程补写 `ready_dispatch_recovery_completed` 或 `ready_dispatch_recovery_failed`。

## 验证
- 新增非阻塞回归：
  - `python scripts/acceptance/verify_schedule_ready_dispatch_recovery_nonblocking.py`
  - session: `.repository/pm-main/.test/20260427-132942-903/report.md`
  - 结果：PASS，慢 dispatch 下 `_resume_pending_schedule_triggers` 约 `0.0396s` 返回。
- 既有 ready-dispatch 恢复：
  - `python scripts/acceptance/verify_schedule_ready_dispatch_recovery.py`
  - session: `.repository/pm-main/.test/20260427-133000-910/report.md`
  - 结果：PASS，ready 节点最终进入 `running`。
- 行数门禁：
  - `python scripts/quality/check_workspace_line_budget.py --root .`
  - session: `.repository/pm-main/.test/20260427-133026-107/report.md`
  - 结果：PASS。
- 完整 workflow gate：
  - `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
  - report: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260427-135324.md`
  - session: `.repository/pm-main/.test/20260427-134504-997/report.md`
  - 结果：PASS。
- 额外治理修正：
  - 对齐 `pm/versions/V12/版本计划.md` 当前状态快照，修复 PM snapshot alignment gate 的 lane/lifecycle 文本漂移。

## 发布
- `test` 部署：`20260427-135534`
- 部署报告：`.running/control/logs/test/deploy-20260427-135534.json`
- prod candidate：`20260427-135534`
- candidate evidence: `.running/control/reports/test-gate-20260427-135534.json`
- 当前 prod：`20260427-083036`
- 未直接 apply prod：当前 `running_task_count=2`，`can_upgrade=false / blocking_reason=running_tasks_present`；按默认发布约束，仅刷新 candidate，等待空窗或用户明确升级指令。
