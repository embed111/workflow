# Continuous Improvement Report

- generated_at: `2026-04-18T20:23:53+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260418-e1b0b0ea`
- active_version: `V4`
- focus_lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- requirement_focus: `V4-R3`
- preference_ref: `state/user-preferences.md`
- memory_ref: `.codex/memory/2026-04/2026-04-18.md`

## 本轮推进
- 我把 `status-detail` 默认详情 fallback 收成 `.repository/pm-main@7274f90 / ../workflow_code@7274f90`。
- `_assignment_default_selected_node()` 现在会在没有 `running / workflow mainline / workflow patrol / ready` 焦点时，优先回到最近 terminal node，不再把默认详情落到 generic blocked/pending。
- 我把 `verify_assignment_status_detail_default_node.py` 扩成了 mixed graph 红绿合同：`node-mixed-succeeded` 与 blocked `node-mixed-pending` 并存时，默认详情必须选回 terminal，且 `latest_run` 跟着对齐。
- 我随后部署 `test`、刷新出 `prod candidate=20260418-202109`，再把 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 全部 refresh 到 `clean_synced@7274f90`。

## 验证
- 红灯：`.repository/pm-main/.test/20260418-201334-450/report.md`
- 绿灯：`.repository/pm-main/.test/20260418-201405-415/report.md`
- `line budget`：`.repository/pm-main/.test/20260418-201420-541/report.md`
- `workflow gate`：`.repository/pm-main/.test/runs/workflow-gate-acceptance-20260418-201836.md`
- `test / prod candidate`：`.running/control/logs/test/deploy-20260418-202109.json`
- `test` live `status-detail` 默认详情已从原型图的 pending 尾部回到 terminal：`selected_node_id=T9 / status=failed / completed_at=2026-04-18T20:21:23+08:00`，不再落到 `T15 pending`
- `manage_developer_workspace.py --root .running/control/runtime/prod status` 当前为 `developer_workspace_count=6 / clean_synced=6`

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
- `workspace_head=code_root_head=7274f90`
- `git -C .repository/pm-main status --short --branch` 当前为 `## main...origin/main [ahead 5]`
- 这条 `ahead 5` 只指向 GitHub tracking 参考，不构成本机 `workspace -> ../workflow_code` 的阻塞。
- `next_push_batch=等待 prod 空窗切到 20260418-202109 后复核 current-version smoke 与 status-detail 默认 terminal fallback`

## Live 真相
- `prod /api/runtime-upgrade/status`: `current_version=20260418-194111 / candidate=20260418-202109 / candidate_is_newer=true / running_task_count=1 / can_upgrade=false / ghost_running_detected=false / supervisor_pid=20500`
- `prod /api/status`: `active_version=V4 / lane=工程质量探测 / lifecycle_stage=基于基线测试 / baseline=prod=20260418-194111 / running_task_count=1 / queued_task_count=2`
- 当前主线是 `node-sti-20260418-e1b0b0ea / running`，当前 patrol 是 `node-sti-20260418-54ddd663 / ready`，下一条 mainline 是 `node-sti-20260418-9c6daa2b / ready`
- `test /api/runtime-upgrade/status`: `current_version=20260418-202109 / candidate=20260418-202109 / running_task_count=0 / ghost_running_detected=false`

## 下步
- 等 idle watcher 在空窗把 `candidate=20260418-202109` 切进 `prod`
- 切版后第一优先复跑 `collect_v4_r1_r4_current_version_smoke.py`，并复核默认 `status-detail` 的 terminal fallback 在 live 上没有回退
- 如果 `202109` live 后仍暴露“terminal 已选中但 `latest_run_id` 为空”的 case，我下一轮继续沿 `V4-R3` 把这条细分问题再切小，不回到泛化的 detail family
