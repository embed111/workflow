# Continuous Improvement Report

判断：`version_transition_decision=stay(V7)`。当前仍处于 `基于基线测试 / 测试探测`。`prod` 已在 `2026-04-22 07:15:24 +08:00` 从 `20260422-052659` 自动切到 `20260422-065617`，所以旧的 idle-apply blocker 已经退出；现在真正卡住的是 `workflow_testmate node-20260422-065757-c242e7 / arun-20260422-071532-f3352d` 还在给 `065617` 做 focused candidate/live readback，而 `V8-R1 / V8-R2 / V8-R3 / V8-R5` 的 activation probe binding 仍未补齐。

这轮推进不是重复派单，而是把现场真相和发布边界一起收干净。我用受支持的 developer workspace refresh 把 `pm-main / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 全部追平到 `workflow_code@185ccce`，清掉了 `workspace_head behind code_root` 的异常；同时我继续消费已经在跑的 `workflow_testmate` readback。它已经证明 `8092` 的 `assignment_graph_not_found` 不是“candidate runtime 没有 detail”，而是把 prod graph ticket 直接拿去打 test host 的路径错误，当前正在锁定 8092 上真实的 candidate detail path，并把 browser/API 证据落到新的 test session。

当前版本状态：`V7-R1 completed`，`V7-R2 completed`，`V7-R3 completed`，`V7-R4 in_progress(95%, eta=2026-04-23)`，`V7-R5 completed`，`V7-R6 completed`，`V7-R7 completed`。当前不切版的 blocker 已经收窄成两条：`workflow_testmate` 当前 run 还没写回终态；`V8` 的 activation probe binding 仍是占位。`next_activation_candidate=V8 / next_activation_ready=false`。

发布边界真相：`pm-main / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate / workflow_devmate root_sync_state=clean_synced / workspace_head=code_root_head=185ccce / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=-`。`pm-release` 仍停在历史提交 `54f6aa8`，但它不在当前发布链上。`next_push_batch=无代码待推；先消费 workflow_testmate 当前 run 的终态与 artifact`。

下一动作：先消费 `workflow_testmate node-20260422-065757-c242e7 / arun-20260422-071532-f3352d` 的终态。若同路径通过，我就把 `V7-R4` 往 completed 收口，并重检 `V8` 的激活条件；若同路径失败，我就按证据 route `workflow_qualitymate / workflow_bugmate`。当前 `pm/daily-execution-history/2026-04-20.md`、`2026-04-21.md`、`2026-04-22.md` 与 `pm/daily-learning-reports/2026-04-22/` 仍未补齐，这轮继续保留 warning，不伪造 daily 完成态。`memory_ref=.codex/memory/2026-04/2026-04-22.md`

- preference_ref: state/user-preferences.md
- delta_observation: 这轮我更倾向先清理 `workspace_head behind code_root` 这类会污染后续判断的治理噪音，再消费已经在正确方向上运行的 helper，而不是靠重复派单制造“看起来更忙”。
- delta_validation: 下一轮先读 `workflow_testmate arun-20260422-071532-f3352d` 的终态和 artifact，再决定是否补 `8090` rerun，还是正式 route `workflow_qualitymate / workflow_bugmate`。
