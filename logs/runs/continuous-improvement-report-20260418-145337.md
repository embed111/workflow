# Continuous Improvement Report

- generated_at: `2026-04-18T14:53:37+08:00`
- active_version: `V4`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- change_batch: `.repository/pm-main@f55e422 / ../workflow_code@f55e422`

## 本轮推进

- 我把 `V4-R3` 的 `detail/archive truth drift` 收成了新的正式批次：`dashboard._workboard_payload()` 现在会继续保留失败池节点的 `completed_at / result_ref / failure_reason / success_reason / artifact_delivery_status`，不再让 workboard 聚合层把终态字段压没。
- 我先按 TDD 把红灯打出来：`verify_assignment_workboard_recent_failure_pool.py` 和 `collect_v4_r1_r4_current_version_smoke.py` 新增了 `recent_failure_pool_completed_at_present` 合同，红灯先明确暴露出失败池 `completed_at` 全空。
- 我随后跑通了 `line budget`、定向 probe 和完整 `workflow gate`，并把这批改动提交为 `f55e422 fix(task-center): 保留失败池终态字段避免detail真相漂移`。
- 我再把 `../workflow_code` fast-forward 到同一 head，部署 `test` 并刷新出 `prod candidate=20260418-145016`；`deploy-20260418-145016.json` 已自动记录 `post_deploy_ghost_running.repaired_count=1 / ghost_running_count_before=1 / ghost_running_count_after=0`。
- 候选刷新后我又用受支持的 developer workspace bootstrap/refresh，把 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 全部拉回 `clean_synced@f55e422`，没有把 helper drift 留给下一轮。

## 验证

- 红灯：`.repository/pm-main/.test/20260418-144026-823/report.md`
  失败池 probe 稳定报出 `completed_at_missing=node-failed-e,node-failed-d,node-failed-c,node-failed-b`。
- 红灯：`.repository/pm-main/.test/20260418-144026-893/report.md`
  live current-version smoke 新合同命中 `recent_failure_pool_completed_at_present=false`；同轮还因为本地 workspace dirty 与浏览器截图侧效应带出辅助红点。
- 绿灯：`.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- 绿灯：`.repository/pm-main/.test/20260418-144517-312/report.md`
  失败池 probe 已确认 `completed_at / result_ref / failure_reason` 全部保留。
- 绿灯：`.repository/pm-main/.test/runs/workflow-gate-acceptance-20260418-144836.md`
- 发布：`.running/control/logs/test/deploy-20260418-145016.json`

## 当前真相

- `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0`
- `workspace_head=code_root_head=f55e422`
- `prod.current_version=20260418-141234 / candidate_version=20260418-145016 / candidate_is_newer=true / drain_active=true / running_task_count=1`
- `test.current_version=20260418-145016 / candidate_version=20260418-145016 / ghost_running_detected=false / running_task_count=0`
- `/api/status` 当前为 `running_task_count=1 / queued_task_count=2 / schedule_total=2`
- live mainline=`node-sti-20260418-1c7465d6`
- next mainline=`node-sti-20260418-106de7c3`
- patrol ready=`node-sti-20260418-70aec033 / next_trigger_at=2026-04-18T15:00:00+08:00`
- 5 个 helper developer workspaces 当前均为 `clean_synced@f55e422`

## 版本判断

- `V4-R1`: `in_progress / 90% / eta=2026-04-19 / 未超时`
- `V4-R2`: `in_progress / 60% / eta=2026-04-20 / 未超时`
- `V4-R3`: `in_progress / 99% / eta=2026-04-20 / 未超时`
- `V4-R4`: `completed / 100% / eta=2026-04-17 / 未超时`
- `version_transition_decision=stay(V4)`
- `next_activation_candidate=- / next_activation_ready=false`
- `switch_blockers=V5 仍保持 backlog activation_readiness=draft`

## 下一步

- 等 idle watcher 在空窗把 `candidate=20260418-145016` 切进 `prod`。
- 切版后第一优先复跑 `collect_v4_r1_r4_current_version_smoke.py --expected-version 20260418-145016`，确认新增的 `recent_failure_pool_completed_at_present` 合同在 live `prod` 也转绿。
- 若 live `145016` 仍有红点，我下一轮优先继续吃 `detail/archive truth drift family` 的剩余 formal route，而不是回到纯观察。

- preference_ref: `state/user-preferences.md`
- delta_observation: 用户要求我以 `workflow` 本人的身份持续推进版本，不接受把 live 风险冻结成“观察中”；一旦命中 helper drift 或发布边界异常，我要在当轮直接收口。
- delta_validation: 等 `prod` 空窗切到 `20260418-145016` 后，按新增 `recent_failure_pool_completed_at_present` 合同复跑 live smoke，并确认 5 个 helper developer workspaces 仍保持 `clean_synced@f55e422`。
- memory_ref: `.codex/memory/2026-04/2026-04-18.md`
