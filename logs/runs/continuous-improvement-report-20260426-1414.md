# [持续迭代] workflow / 2026-04-26 12:36

## 判断

`version_transition_decision=stay(V11)`。我这轮不切 `V12`：`V11-R1/R3/R4/R6` 已满足退出口径，`V12-R2` 测试路线已交付；但 `V12-R1/R5` 仍缺红灯 probe 与最小实现绿灯，且新候选 `prod candidate=20260426-140042` 还需等当前 PM 主线结束后由 idle watcher apply。

本轮属于 `开发实现 -> 基于基线测试 -> 验收/发布候选` 的恢复切片，最高价值泳道是 `工程质量探测`。我完成的推进性修改是代码修复与发布候选收口：`fe5cc87 fix(runtime): 缩短升级 watcher 等待并加快任务读面`，修掉页面读模型持锁/慢恢复与 prod watcher 同步等待风险，并补了用例。

## 已完成动作

- 在 `.repository/pm-main` 提交 `fe5cc87`，并同步到本机 `../workflow_code/main`。
- assignment overview/graph/scheduler/status-detail 改成轻量只读，不再在页面读面触发 stale reconcile、interface catalog backfill 或 ticket mutation lock。
- status-detail 对大 `events.log` 与文本预览加读取上限；前端 dashboard 启动恢复加 soft timeout。
- `prod-idle-upgrade-watchdog` 发起 apply 或确认 already pending 后立即交还 supervisor，不再同步等 8090 恢复。
- 新增 `scripts/acceptance/verify_assignment_read_model_fast_path.py`，并把相关 stale recovery 用例改为显式维护路径触发。
- 部署 `test=20260426-140042`，刷新 `prod candidate=20260426-140042`。

## 逐项状态

- `V11-R1`: `completed / 100% / 最近更新=2026-04-26T14:06:00+08:00 / ETA=2026-04-26 / 已完成，无 AAR`
- `V11-R2`: `v12_gate_test_route_delivered / 60% / 最近更新=2026-04-26T14:06:00+08:00 / ETA=2026-04-27 / 未超时`
- `V11-R3`: `completed / 100% / 最近更新=2026-04-26T14:06:00+08:00 / ETA=2026-04-24 / 已完成，无 AAR`
- `V11-R4`: `completed / 100% / 最近更新=2026-04-26T14:06:00+08:00 / ETA=2026-04-24 / 已完成，无 AAR`
- `V11-R5`: `v12_gate_recovery_fix_candidate_ready / 55% / 最近更新=2026-04-26T14:06:00+08:00 / ETA=2026-04-29 / 未超时`
- `V11-R6`: `completed / 100% / 最近更新=2026-04-26T14:06:00+08:00 / ETA=2026-04-24 / 已完成，无 AAR`

## 发布边界

- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `push_block_reason=-`
- `next_push_batch=prod candidate 20260426-140042 待 idle watcher apply；下一批在 prod apply 后或下一轮直接接管 V12-R1/R5 红灯 probe`
- `pm-main@fe5cc87` 与 `workflow_code@fe5cc87` 已对齐；`workflow_code` 相对 GitHub `origin/main` 的 `ahead 316` 只是上游参考，不作为本机发布边界阻塞。

## 证据

- `/healthz`: ok
- `/api/status`: `next_activation_candidate=V12 / next_activation_ready=false`
- `/api/runtime-upgrade/status`: `prod=20260426-120441 / candidate=20260426-140042 / candidate_is_newer=true / request_pending=false / can_upgrade=false(running_task_count=1) / ghost_running_detected=false`
- `/api/schedules`: `[持续迭代] workflow` enabled，当前节点 `node-sti-20260426-fc0a4ed4` 仍为 running
- line budget: `.repository/pm-main/.test/20260426-134458-581/report.md`
- py_compile: `.repository/pm-main/.test/20260426-134549-675/report.md`
- read-model fast path: `.repository/pm-main/.test/20260426-132300-788/report.md`
- prod watcher probe: `.repository/pm-main/.test/20260426-132713-570/report.md`
- web bundle syntax: `.repository/pm-main/.test/20260426-134632-333/report.md`
- full workflow gate: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260426-135708.md`
- test gate: `.running/control/reports/test-gate-20260426-140042.json`
- runtime read-model留痕: `logs/runs/runtime-read-model-fast-path-20260426-1406.md`

## 下一动作

当前 PM 主线结束后，等待 prod idle watcher apply `20260426-140042`。下一棒先复核 assignment graph/status-detail 真实响应；若读面恢复正常，就直接恢复或由我接管 `V12-R1/R5` 的 UTF-8、starting truth、watchdog false-running、role start closure 红灯 probe 与最小实现。只有这些 probe 绿灯后，才重检 `V11 -> V12` 切版。

## 记忆引用

- memory_ref: `.codex/memory/2026-04/2026-04-26.md`
