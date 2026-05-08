# Continuous Improvement Report

## 判断

- `version_transition_decision=stay(V8)`。
- 这轮真正推进的是 `工程质量探测 + 发布推进`。
- 我没有重复上一轮的 `R6` stale 叙事；这轮直接把 live 双 listener 风险推进成 candidate 里的跨进程 dispatch claim，并把现网 stray `8098` listener 清掉。

## 取舍

- 我没有继续新派 helper；当前更高价值的是消费 `workflow_bugmate` 已冻结的根因，在 `pm-main` 直接改 dispatch core、过 gate、刷新发布链。
- 我把补丁收在最小面：只补跨进程 claim、release 链和 dedicated probe，不顺手扩大 UI 或版本功能面。
- 当前 `prod` 还没升到 `111915`，所以我先清掉旧 `8098` 脱管 listener，避免在升级空窗前继续暴露双 listener 风险。

## 本轮推进

- 新增 `assignment_dispatch_claim_runtime.py`，把 dispatch 互斥从进程内 `RLock` 补成文件级原子 claim。
- `dispatch_assignment_next` 与 `override -> running` 现在会先 claim，再建 run；`finalize / stale recovery / cancel / rerun / delete` 会释放 claim。
- 新增 `verify_assignment_cross_process_dispatch_claim.py`，并接入 `workflow_gate_probe_registry.py`。
- `line budget`、`verify_assignment_dispatch_lock.py`、`verify_assignment_cross_process_dispatch_claim.py` 与完整 `workflow gate@8102` 已全部通过。
- 代码已提交为 `6fed81f fix(assignment): 增加跨进程 dispatch claim 防止双派发`，并同步到本机 `workflow_code@6fed81f`。
- 发布边界当前为：`root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=-`。
- `pm-main=clean_synced@6fed81f`，`workflow_code=clean_synced@6fed81f`；`next_push_batch=无代码待推；下一批若继续推进 V8-R6，就切 current-baseline live regression evidence 或 coverage batch。`
- 我已刷新出 `test=current=candidate=20260422-111915`，并生成 `prod candidate=20260422-111915`。
- 当前 live 为：`prod current=20260422-103706 / candidate=20260422-111915 / candidate_is_newer=true / drain_active=true / running_task_count=1 / ghost_running_detected=false`。
- 共享 `prod` runtime root 的 stray `8098` listener 树（`3224/9628`）已清理；当前 authoritative listener 只剩 `8090`。

## 当前版本状态

- `V8-R1=in_progress / 90% / updated=2026-04-22T11:20:28+08:00 / eta=2026-04-23 / overdue=no`
- `V8-R2=in_progress / 55% / updated=2026-04-22T11:20:28+08:00 / eta=2026-04-23 / overdue=no`
- `V8-R3=in_progress / 50% / updated=2026-04-22T11:20:28+08:00 / eta=2026-04-24 / overdue=no`
- `V8-R4=completed / 100% / updated=2026-04-22T11:20:28+08:00 / eta=已完成 / overdue=no`
- `V8-R5=in_progress / 70% / updated=2026-04-22T11:20:28+08:00 / eta=2026-04-24 / overdue=no`
- `V8-R6=in_progress / 45% / updated=2026-04-22T11:20:28+08:00 / eta=2026-04-24 / overdue=no`
- 本轮没有需求超时，所以没有新增 AAR。

## 下一步

- 我下一步先等 `prod candidate=20260422-111915` 的 idle watcher 空窗升级；如果 `running_task_count` 长时间不降，我就继续按升级读链查主线为什么没有释放空窗。
- 一旦 `prod` 升到 `111915`，我就优先复核“只有 `8090` authoritative listener + cross-process claim”下的主线 handoff，再决定是否把 `workflow_testmate` 接回 `V8-R6` current-baseline live regression evidence。
- `pm/daily-execution-history/2026-04-20.md`、`2026-04-21.md`、`2026-04-22.md` 与 `pm/daily-learning-reports/2026-04-22/` 仍未补齐；这轮继续保留 warning，不伪造 daily 完成态。
- `memory_ref=.codex/memory/2026-04/2026-04-22.md`

## Snapshot Addendum

- preference_ref: `state/user-preferences.md`
- delta_observation: 你更在意我先把 live 风险降下来、再补状态与证据，而不是先铺长段播报。
- delta_validation: 下一轮继续优先按“判断 / 取舍 / 下一动作”顺序交付，并在命中现网风险时先做受支持收口。
