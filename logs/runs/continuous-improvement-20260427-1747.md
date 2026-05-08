# continuous-improvement-report

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260427-d7c2c00c`
- report_time: `2026-04-27T17:59:00+08:00`
- active_version: `V12`
- version_transition_decision: `stay`
- memory_ref: `.codex/memory/2026-04/2026-04-27.md`

## 判断与取舍
我这轮保持 `V12`，不切 `V13`。原因很直接：`DTS-00012` 还没关闭，`V13` 仍是 `next_activation_ready=false / planned_with_blockers`，现在切版会把 R3 质量链路缺口带进下一版。

当前最高价值动作不是重复 R3 live readback，而是消费 `workflow_bugmate` 的 analyze 结果，并给 fix/release 后补上独立回归出口。

## 本轮推进性修改
- 已消费 `dr-20260427-79ceb34024-analyze / arun-20260427-172650-42fe1a`：结论为 R3 `controller-governance` API 在 prod 可用，缺陷主因是 qualitymate helper 执行链在连续 Codex stream disconnect 与 finalize/stale recovery 竞争下未稳定留下质量证据。
- 已创建 `workflow_testmate dr-20260427-79ceb34024-regression-testmate`，依赖 `dr-20260427-79ceb34024-release`，用于 bugmate fix/release 后复核 DTS-00012、R3 live readback、quality helper 修复效果与 ghost-running 状态。
- 当前 `dr-20260427-79ceb34024-fix / arun-20260427-174815-bd38b8` 为 `running/provider_pid=64072`，`latest_event_at=2026-04-27T18:05:39+08:00`；`release` 与 testmate regression 均保持等待上游。

## 当前证据
- `/healthz`: `ok=true`
- `/api/status`: `active_version=V12 / next_activation_candidate=V13 / next_activation_ready=false / running_task_count=2 / queued_task_count=0 / truth_mismatch_count=0`
- `/api/schedules`: `ok=true`
- `/api/runtime-upgrade/status`: `current=20260427-162745 / candidate=20260427-162745 / candidate_is_newer=false / request_pending=false / drain_active=false / ghost_running_detected=false / running_task_count=2`
- root sync: `ahead_dirty(in_progress) / ahead_count=0 / dirty_tracked_count=7 / untracked_count=1 / push_block_reason=DTS-00012 bugmate fix 正在运行，不能在 provider 活跃时抢先提交 / next_push_batch=DTS-00012 bugmate fix code batch`

## V12 逐项状态
| 需求点 | 状态 | 进度 | ETA | 超时 |
| --- | --- | --- | --- | --- |
| `V12-R1` | `activation_probe_bound_wait_active_followup` | `80%` | `2026-04-28` | 否 |
| `V12-R2` | `live_readback_ready_prod083036` | `92%` | `2026-04-28` | 否 |
| `V12-R3` | `dts00012_analyze_done_fix_running_regression_prehung` | `93%` | `2026-04-28` | 否 |
| `V12-R4` | `s2_owner_cards_retained_supported_refresh_done_method_gaps_remain` | `96%` | `2026-04-28` | 否 |
| `V12-R5` | `dts00012_fix_running_postfix_regression_prehung_no_ghost` | `96%` | `2026-04-28` | 否 |
| `V12-R6` | `dts00012_regression_gate_prehung_v13_blocked` | `80%` | `2026-04-29` | 否 |

## 下一动作
下一轮先消费 `dr-20260427-79ceb34024-fix / release`。若 release 成功，确认 `workflow_testmate dr-20260427-79ceb34024-regression-testmate` 是否自动进入 ready/running；若未接力，再走受支持 `dispatch-next`。若 fix 长时间无事件或被判 ghost，再走受支持 repair/settle。

## Warnings
- 本轮没有代码改动，未运行完整 workflow gate；验证以 live API、status-detail 和任务图真相为主。
- `pm/daily-execution-history/2026-04-27.md` 仍不存在；本轮未伪造每日学习报告。
- `../workflow_code` 与 `.repository/workflow_bugmate` 当前已有 DTS-00012 fix 运行中 dirty 批次；本轮不回滚、不抢先提交，下一轮消费 bugmate 终态后进入验证与根仓收口。
