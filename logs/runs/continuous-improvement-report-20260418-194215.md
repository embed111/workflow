# Continuous Improvement Report

- generated_at: `2026-04-18T19:43:17+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260418-75628156`
- active_version: `V4`
- focus_lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- requirement_focus: `V4-R3`
- preference_ref: `state/user-preferences.md`

## 本轮推进
- 我把 `/api/status` 的 workboard 失败池长 `failure_reason / success_reason` 预览收成 `.repository/pm-main@a2eb29b / ../workflow_code@a2eb29b`。
- `dashboard._workboard_payload()` 现在只返回 `160` 字理由预览，`completed_at / result_ref / artifact_delivery_status` 继续保真，不再把整段结构化失败结果和旧提示词直接塞进状态面板。
- 我新增 `scripts/acceptance/verify_assignment_workboard_reason_preview_compaction.py`，并把它接进 `workflow gate`。
- 我把 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 全部 refresh 回 `clean_synced@a2eb29b`，没有把 helper drift 留给下一轮。

## 验证
- 定向红灯：`.repository/pm-main/.test/20260418-193353-093/report.md`
- 定向绿灯：`.repository/pm-main/.test/20260418-193500-884/report.md`
- `line budget`：`.repository/pm-main/.test/20260418-193509-413/report.md`
- `workflow gate`：`.repository/pm-main/.test/runs/workflow-gate-acceptance-20260418-193944.md`
- 部署与 candidate：`.running/control/logs/test/deploy-20260418-194111.json`
- live runtime upgrade：`http://127.0.0.1:8090/api/runtime-upgrade/status` 当前为 `prod=20260418-190547 / candidate=20260418-194111 / running_task_count=1 / can_upgrade=false / ghost_running_detected=false`
- test runtime upgrade：`http://127.0.0.1:8092/api/runtime-upgrade/status` 当前为 `test=20260418-194111 / candidate_is_newer=false / running_task_count=0 / ghost_running_detected=false`

## 版本判断
- `V4-R1=status=in_progress / progress=90% / eta=2026-04-19 / timeout=未超时`
- `V4-R2=status=in_progress / progress=60% / eta=2026-04-20 / timeout=未超时`
- `V4-R3=status=in_progress / progress=99% / eta=2026-04-20 / timeout=未超时`
- `V4-R4=status=completed / progress=100% / eta=2026-04-17 / timeout=未超时`
- `version_transition_decision=stay(V4) / next_activation_candidate=- / next_activation_ready=false / switch_blockers=V4-R1 / V4-R2 / V4-R3`
- 本轮没有需求点超时，不新增 AAR。

## 发布边界
- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0 / untracked_count=0`
- `workspace_head=code_root_head=a2eb29b`
- `git -C .repository/pm-main status --short --branch` 当前为 `## main...origin/main [ahead 4]`
- 这条 `ahead 4` 只指向 GitHub tracking 参考，不构成本机 `workspace -> ../workflow_code` 的阻塞。
- `manage_developer_workspace.py --root .running/control/runtime/prod status` 当前为 `developer_workspace_count=6 / clean_synced=6`

## 下步
- 等 idle watcher 在空窗把 `20260418-194111` 切进 `prod`。
- 切版后第一优先复核 live `/api/status` 的 workboard 失败池，确认 `failure_reason` 预览已压缩且 `result_ref / completed_at` 继续保真。
- 如果 `194111` live 后仍有红点，我下一轮继续沿 `V4-R3` 的 formal route 往下切，不回到纯观察。
