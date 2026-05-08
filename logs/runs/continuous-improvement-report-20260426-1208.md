# continuous-improvement-report 2026-04-26 12:08

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260426-69f6e98e`
- active_version: `V11`
- version_transition_decision: `stay`

## 判断

我不切 `V12`。两份 V12 activation gate brief 已交付，但结论都不是“可以直接 active”：`V12-R1/R5` 还缺红灯 probe、最小实现和绿灯验证；`V12-R2` 还缺 `startup_bridge` 字段合同与七态 resolver 测试路线。

本轮先把准入缺口从 brief 消费推进到真实下游执行：已新建 `workflow_devmate node-20260426-1139-v12r15-dev-impl` 和 `workflow_testmate node-20260426-1139-v12r2-test-route`，均挂在当前主线节点 `node-sti-20260426-69f6e98e` 后面等待接棒。

发布边界检查中途发现 `pm-main` 出现一个 schedule catch-up 修复批。我没有把它当成背景脏状态，而是完成最小验证、完整 gate、提交同步和 `test/prod candidate` 刷新：代码已到 `pm-main@df8b4f9 / workflow_code@df8b4f9`，`test=20260426-120441`，`prod candidate=20260426-120441`。

## 推进

- `workflow_devmate node-20260426-063753-2ebad6` 已交付 `v12-activation-probe-brief.md`。
- `workflow_ucdmate node-20260426-v12r2-ucdmate-brief` 已交付 `v12-project-startup-bridge-brief.md`。
- 新派 `workflow_devmate node-20260426-1139-v12r15-dev-impl`：承接 `V12-R1/R5` 的 TDD probe 与最小实现。
- 新派 `workflow_testmate node-20260426-1139-v12r2-test-route`：承接 `V12-R2` 的 startup bridge 七态测试路线。
- 收口 `df8b4f9 fix(schedule): 防止持续迭代主线错过触发后被一次性计划修复误关`，同步到本机 `workflow_code/main`。
- 部署 `test=20260426-120441` 并刷新 `prod candidate=20260426-120441`，不直接 apply 正式环境。

## 版本状态

- `V11-R1`: `completed / 100% / 2026-04-26T12:08:00+08:00 / ETA=2026-04-26 / 已完成，无 AAR`
- `V11-R2`: `v12_gate_test_route_dispatched / 50% / 2026-04-26T12:08:00+08:00 / ETA=2026-04-27 / 未超时`
- `V11-R3`: `completed / 100% / 2026-04-26T12:08:00+08:00 / ETA=2026-04-24 / 已完成，无 AAR`
- `V11-R4`: `completed / 100% / 2026-04-26T12:08:00+08:00 / ETA=2026-04-24 / 已完成，无 AAR`
- `V11-R5`: `v12_gate_probe_implementation_dispatched / 45% / 2026-04-26T12:08:00+08:00 / ETA=2026-04-29 / 未超时`
- `V11-R6`: `completed / 100% / 2026-04-26T12:08:00+08:00 / ETA=2026-04-24 / 已完成，无 AAR`

## 证据

- `/healthz`: ok
- `/api/status`: `running_task_count=1 / active_version=V11 / next_activation_candidate=V12 / next_activation_ready=false`
- `/api/schedules/sch-20260405-56eee156`: enabled，`last_result_status=running / node=node-sti-20260426-69f6e98e`
- `/api/runtime-upgrade/status`: `current=20260426-012259 / candidate=20260426-120441 / candidate_is_newer=true / request_pending=false / ghost_running_detected=false / can_upgrade=false(running_task_count=1)`
- `/api/assignments/asg-20260327-223335-b79f27/graph`: 两条新节点均为 `pending`，上游为当前主线节点。
- `.repository/pm-main/.test/20260426-115124-385/report.md`: line budget pass
- `.repository/pm-main/.test/20260426-115153-226/report.md`: py_compile pass
- `.repository/pm-main/.test/20260426-115203-705/report.md`: `verify_assignment_mainline_handoff_outbox.py` pass
- `.repository/pm-main/.test/20260426-115320-532/report.md`: workflow gate pass on `8108`
- `.running/control/logs/test/deploy-20260426-120441.json`: deploy/test gate passed and prod candidate refreshed

## 发布边界

- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `push_block_reason=-`
- `current_workspace=pm-main@df8b4f9`
- `workflow_code=df8b4f9`
- `next_push_batch=等待 prod idle watcher 空窗 apply 20260426-120441；等待 V12 activation gate 两条执行节点交付`

## 下一步

当前主线结束后等待两条 helper 节点接棒。它们交付后重检 `next_activation_ready`；若 V12 gate 转 ready，同轮切 `V12`，否则按新 blocker 继续派实现或回归切片。

同时等待 `prod` 在 `running_task_count=0` 空窗由 supervisor idle watcher 自动 apply `20260426-120441`；apply 后复核 `/healthz / /api/status / /api/schedules / /api/runtime-upgrade/status` 与主线 handoff。

## warnings

- 两次 helper 创建 API 客户端超时，但 graph 与节点文件确认节点已落盘；本轮未重复创建。
- 第一次 full gate 使用 `8098` 被端口隔离保护拦住，已换空闲端口 `8108` 重跑通过。
- `pm/daily-execution-history/2026-04-26.md` 仍未补齐；本轮没有代写 helper 学习报告。
