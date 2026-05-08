# Continuous Improvement Report

- version_transition_decision: `stay(V8)`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- root_sync_state: `clean_synced`
- ahead_count: `0`
- dirty_tracked_count: `0`
- untracked_count: `0`
- push_block_reason: `-`
- next_push_batch: `无代码待推；下一批优先把 V8-R2 / V8-R5 的剩余 contract/probe 重新接进 gate，并判断 V8-R3 是否继续推进 project-ops canonical header / workboard trim`
- memory_ref: `.codex/memory/2026-04/2026-04-22.md`

## 判断

我继续保持 `stay(V8)`。这轮真正推进的是 `工程质量探测`：我先把 `verify_assignment_detail_contract_grouping.js` 扩成“功能 + gate 注册”双重约束的 targeted regression，拿到红灯后在 `pm-main` 提交并同步 `f79824d`，把 `V8-R3` 的 detail-contract grouping 正式接进 `workflow gate`。随后我跑通定向 probe、`workflow gate`、`test` 部署，并把 `test/current=candidate` 刷到 `20260422-173026`。

## 本轮推进

- 红绿链：`verify_assignment_detail_contract_grouping.js` 先因 `workflow_gate_probe_registry.py` 缺少 `assignment_detail_contract_grouping` 注册而失败；补 registry 后同一 probe 转绿。
- 门禁：`workflow gate` 通过，新 probe 现在跟随总门禁持续执行，不再只是散落的单点脚本。
- 发布推进：`pm-main@f79824d` 与本机 `workflow_code@f79824d` 已 clean_synced；`test/current=candidate` 与 `prod candidate` 已刷新到 `20260422-173026`。
- live 验证：我在 `8092` 对 `20260422-173026` 补跑了 exact `verify_api_catalog_live_regression.py`，确认新 candidate 在 test 侧可读；`prod` 仍是 `current=20260422-165858 / candidate=20260422-173026 / drain_active=true / running_task_count=1`，等待空窗升级。

## 版本更新

- `V8-R1=in_progress/90%/最近更新=2026-04-22T12:45:44+08:00/eta=2026-04-23/未超时`
- `V8-R2=in_progress/55%/最近更新=2026-04-22T12:45:44+08:00/eta=2026-04-23/未超时`
- `V8-R3=in_progress/90%/最近更新=2026-04-22T17:30:41+08:00/eta=2026-04-24/未超时`
- `V8-R4=completed/100%/最近更新=2026-04-22T12:45:44+08:00/eta=已完成/未超时`
- `V8-R5=in_progress/75%/最近更新=2026-04-22T12:45:44+08:00/eta=2026-04-24/未超时`
- `V8-R6=completed/100%/最近更新=2026-04-22T17:00:39+08:00/eta=已完成/未超时`

## 切版判断

- `switch_blockers=V8-R2 / V8-R3 / V8-R5`
- `recheck_trigger=优先把 V8-R2 / V8-R5 的剩余 contract/probe 重新接进 gate，并判断 V8-R3 是否继续推进 project-ops canonical header / workboard trim`
- `next_activation_candidate=V9 / next_activation_ready=false`

## 证据

- `.repository/pm-main/.test/20260422-172330-562/report.md`
- `.repository/pm-main/.test/20260422-172359-074/report.md`
- `.repository/pm-main/.test/20260422-172412-546/report.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260422-172847.md`
- `.running/control/logs/test/deploy-20260422-173026.json`
- `.repository/pm-main/.test/20260422-173210-816/report.md`

## Warnings

- `pm/daily-execution-history/2026-04-20.md` 仍缺失，`pm/daily-execution-history/2026-04-21.md` 与 `pm/daily-execution-history/2026-04-22.md` 仍未补齐。
- `pm/daily-learning-reports/2026-04-22/` 仍未补齐。
- `workflow_devmate` developer workspace 仍是 `ahead_dirty@52e2efb`。
- `workflow_bugmate / workflow_testmate / workflow_qualitymate / workflow_ucdmate` 仍落后 `f79824d`，但当前未脏，不构成本轮发布边界阻塞。

## Snapshot Addendum

- preference_ref: `state/user-preferences.md`
- delta_observation: 这轮我把 `V8-R3` 的 targeted regression 从“已有脚本”推进成了 `workflow gate` 的正式资产，并同步把新 candidate 刷到 `20260422-173026`。
- delta_validation: 下一轮优先把 `V8-R2 / V8-R5` 的剩余 contract/probe 重新接进 gate，再判断 `V8-R3` 是否继续推进 `project-ops` canonical header 与 workboard trim。
