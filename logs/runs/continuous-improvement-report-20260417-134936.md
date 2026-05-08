# Continuous Improvement Report

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260417-83874562`
- phase: `基于基线测试`
- lane: `测试探测`
- root_sync_state: `clean_synced`
- ahead_count: `0`
- dirty_tracked_count: `0`
- untracked_count: `0`
- push_block_reason: `-`
- next_push_batch: `等待 idle watcher 在空窗把 20260417-134734 切进 live；切版后优先复跑 V4 current-version smoke，并确认 assignment browser acceptance 在 live 侧没有回退`
- preference_ref: `state/user-preferences.md`
- memory_ref: `.codex/memory/2026-04/2026-04-17.md`

## 本轮推进
- 我先复现了 `run_acceptance_assignment_center_browser.py` 的红灯，确认它不是 probe 断言失败，而是第一张 `task_center_visible` 截图就稳定卡在 `msedge --headless` 超时。
- 我把 `run_acceptance_assignment_center_browser.py` 的 Edge harness 对齐到仓内稳定口径：补上完整启动参数、`shot/dom` 独立 profile、按 `assignment_probe_delay_ms` 推导 `budget/timeout`，并给 browser probe 加上统一重试。
- 我在 [`assignment_center_execution_runtime.js`](D:/code/AI/J-Agents/workflow/.repository/pm-main/src/workflow_app/web_client/assignment_center_execution_runtime.js) 里对 `assignment_probe=1` 加了 realtime fail-closed，停掉 detail 的 `EventSource / poller`，避免截图验收继续被长连接拖死。
- 我在 [`assignment_center_events.js`](D:/code/AI/J-Agents/workflow/.repository/pm-main/src/workflow_app/web_client/assignment_center_events.js) 里修正了 `view_tabs` 的回切和 `surface_compact` 的准备态，让 probe 场景与断言重新一致。
- 我把这批代码收口到 `.repository/pm-main@4537b43 / ../workflow_code@4537b43`，停掉占口的旧 `test` 实例后重新部署，刷新出新的 `prod candidate=20260417-134734`。

## 当前 Active 需求评估
- `V4-R1`: `in_progress / 35% / eta=2026-04-19 / 未超时`。第一条 UCD 修复切片保持稳定，下一步是在 live candidate/prod 上确认不回退。
- `V4-R2`: `planned / 5% / eta=2026-04-20 / 未超时`。仍冻结为第二优先切片，等待 `R1 / R4` 第一批闭环收稳。
- `V4-R3`: `planned / 10% / eta=2026-04-20 / 未超时`。inventory 方向未变，本轮不扩面。
- `V4-R4`: `in_progress / 35% / eta=2026-04-20 / 未超时`。browser acceptance 已从超时故障转成真实绿灯；下一步是把首条“probe 失败 -> 正式路由 -> 修复交付 -> 回归复验”闭环推进到 live。
- `version_transition_decision=stay(V4)`；`V5` 继续保持 `backlog activation_readiness=draft`，本轮不切版。

## 验证
- `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- `.repository/pm-main/.test/20260417-132818-339/report.md`
- `.repository/pm-main/.test/20260417-134048-064/report.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260417-134520.md`
- `.running/control/logs/test/deploy-20260417-134734.json`
- `http://127.0.0.1:8090/healthz`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `http://127.0.0.1:8090/api/schedules`
- `http://127.0.0.1:8092/api/runtime-upgrade/status`

## 风险与下一步
- 当前 `prod=current_version=20260417-124332`，`candidate_version=20260417-134734`，因为 `running_task_count=1` 仍保持 `drain_active=true`；我没有在本轮主动触发 `/api/runtime-upgrade/apply`。
- 我已经检查了 helper 派发窗口：`parallel_candidate_count=2 / parallel_dispatched_count=0 / active_helper_tasks=[]`。这轮不派发的原因不是忽略小伙伴，而是浏览器 harness、probe JS 和 detail realtime guard 都在同一组 task-center 文件里，先由我一次收口更稳。
- 下一轮优先在 `candidate=20260417-134734` 切进 live 后复跑 `V4 current-version smoke`，再把 live screenshot 回归与首条正式缺陷/任务闭环切给 `workflow_testmate / workflow_ucdmate`。
