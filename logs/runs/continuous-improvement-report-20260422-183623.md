# Continuous Improvement Report

- version_transition_decision: `stay(V8)`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- root_sync_state: `clean_synced`
- ahead_count: `0`
- dirty_tracked_count: `0`
- untracked_count: `0`
- push_block_reason: `-`
- next_push_batch: `无代码待推；下一批优先处理 V8-R5 的 self-readback / latency 剩余合同，并决定 workflow_devmate ahead_dirty@52e2efb 是并入主线还是废弃刷新，再补 V8-R2 的更多 live regression。`
- memory_ref: `.codex/memory/2026-04/2026-04-22.md`

## 判断

我继续保持 `stay(V8)`。这轮我没有复读上一拍的 `V8-R2` contract，而是把 `V8-R5` 的 `verify_project_ops_live_regression.py` 收成正式 `workflow gate` 资产：probe 现在会先校验自身已注册到 `workflow_gate_probe_registry.py`，在 gate 场景下自动吃 `WORKFLOW_GATE_PROBE_HOST/PORT`，并允许 isolated runtime 自举 quiet project fixture；随后我把它接进 registry 和 gate runner，形成从红灯到绿灯再到发布的完整链路。

## 本轮推进

- 红灯：我先只改 `verify_project_ops_live_regression.py`，不补 registry，让 `.repository/pm-main/.test/20260422-182714-093/report.md` 在 `8092` 上稳定失败，明确报出“probe 还没接进 workflow gate”。
- 绿灯：补上 `workflow_gate_probe_registry.py` 的 `project_ops_live_regression` 注册，再在 `.repository/pm-main/.test/20260422-182757-163/report.md` 把同一条 probe 跑回绿灯。
- gate：我同时在 `run_acceptance_workflow_gate.py` 给 script probe 传入 isolated `WORKFLOW_GATE_PROBE_HOST/PORT` 和 fixture bootstrap 开关，随后 `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260422-183246.md` 全量转绿，证明这条 live regression 真会在 gate 里持续执行，而不是只会在手工 `8092` 上跑。
- 发布推进：我把代码提交成 `e05d3d9`，并用本机 `ff-only` 把 `workflow_code` 收口到同一提交；随后停掉旧 `test`，刷新出 `test/current=candidate=20260422-183414`。
- live 验证：`.repository/pm-main/.test/20260422-183440-284/report.md` 已在 `8092` 对 `20260422-183414` 跑通；quiet project 继续默认落在 `overview`，`workflow` 项目默认落在 `version`，新 candidate 的项目运营读面保持正常。`prod` 当前为 `current=20260422-180245 / candidate=20260422-183414 / candidate_is_newer=true / drain_active=true / running_task_count=1`，继续等待空窗升级。

## 版本更新

- `V8-R1=in_progress/90%/最近更新=2026-04-22T12:45:44+08:00/eta=2026-04-23/未超时`
- `V8-R2=in_progress/75%/最近更新=2026-04-22T18:04:12+08:00/eta=2026-04-23/未超时`
- `V8-R3=in_progress/90%/最近更新=2026-04-22T17:30:41+08:00/eta=2026-04-24/未超时`
- `V8-R4=completed/100%/最近更新=2026-04-22T12:45:44+08:00/eta=已完成/未超时`
- `V8-R5=in_progress/85%/最近更新=2026-04-22T18:36:23+08:00/eta=2026-04-24/未超时`
- `V8-R6=completed/100%/最近更新=2026-04-22T17:00:39+08:00/eta=已完成/未超时`

## 切版判断

- `switch_blockers=V8-R2 / V8-R3 / V8-R5`
- `recheck_trigger=优先处理 workflow_devmate ahead_dirty@52e2efb 的 V8-R5 self-readback / latency 差异，确认是并入主线还是废弃刷新；随后补 V8-R2 的 project summary live regression，再判断 V8-R3 是否继续推进 project-ops canonical header / workboard trim`
- `next_activation_candidate=V9 / next_activation_ready=false`

## 证据

- `.repository/pm-main/.test/20260422-182714-093/report.md`
- `.repository/pm-main/.test/20260422-182757-163/report.md`
- `.repository/pm-main/.test/20260422-182808-314/report.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260422-183246.md`
- `.running/control/logs/test/deploy-20260422-183414.json`
- `.repository/pm-main/.test/20260422-183440-284/report.md`

## Warnings

- `pm/daily-execution-history/2026-04-20.md` 仍缺失，`pm/daily-execution-history/2026-04-21.md` 与 `pm/daily-execution-history/2026-04-22.md` 仍未补齐。
- `pm/daily-learning-reports/2026-04-22/` 仍未补齐。
- `workflow_devmate` developer workspace 仍是 `ahead_dirty@52e2efb`。
- `workflow_bugmate / workflow_testmate / workflow_qualitymate / workflow_ucdmate` 仍停在 `3ac8be0` 的 clean lag，尚未 refresh 到 `e05d3d9`。
- `prod` 当前仍是 `current=20260422-180245 / candidate=20260422-183414 / drain_active=true / running_task_count=1`，需要继续等空窗升级。

## Snapshot Addendum

- preference_ref: `state/user-preferences.md`
- delta_observation: 这轮我把 `verify_project_ops_live_regression.py` 从 runtime release gate 的单点脚本推进成了 `workflow gate` 的正式资产，并同步把 `test/current=candidate` 刷到 `20260422-183414`。
- delta_validation: 下一轮优先处理 `workflow_devmate ahead_dirty@52e2efb` 对应的 `V8-R5` self-readback / latency 差异，再补 `V8-R2` 的更多 live regression。
