# Continuous Improvement 2026-04-28 13:15

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260428-529c29b0`
- active_version: `V13`
- preference_ref: `state/user-preferences.md`

## 判断
- version_transition_decision: `stay`
- 当前不切 `V14`：`V13-R3` 已完成 `prod=20260428-065217` live recheck，但本轮新收口的 schedule terminal handoff recovery 仍只是 `prod candidate=20260428-131038`，还未 apply；`V13-R4/R5/R6/R7` 也未完成。
- 本轮最高价值动作是发布边界收口：先把既有 `pm-main` dirty 代码批验证、根仓同步、test 部署和候选刷新闭环，而不是继续扩新功能。

## 推进性修改
- 已收口代码批：`cf38fc8 fix(schedule): 终态 trigger 恢复时回填主线 handoff`
- 已确认 `.repository/pm-main` 与本机 `../workflow_code/main` 对齐到 `cf38fc8`。
- 已停止旧 `test` 环境并执行 `deploy_test_workflow_env.ps1`，刷新 `test/prod candidate=20260428-131038`。

## 验证
- line budget + terminal trigger recovery + py_compile: `.repository/pm-main/.test/20260428-130021-013/report.md`
- workflow gate fail-closed: `.repository/pm-main/.test/20260428-130056-016/report.md`（`8098` 被占用，未误指 live）
- workflow gate pass: `.repository/pm-main/.test/20260428-130128-773/report.md`
- workflow gate report: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260428-130924.md`
- deploy blocked evidence: `.repository/pm-main/.test/20260428-131012-670/report.md`（旧 test 进程仍在）
- test deploy pass: `.repository/pm-main/.test/20260428-131035-837/report.md`
- deploy report: `.running/control/logs/test/deploy-20260428-131038.json`
- prod live recheck: `.repository/pm-main/.test/20260428-131346-889/report.md`

## Live 真相
- `/api/status`: `active_version=V13 / running_task_count=1 / next_activation_ready=false`
- `/api/runtime-upgrade/status`: `current=20260428-065217 / candidate=20260428-131038 / candidate_is_newer=true / truth_owner=assignment_schedule_runtime_truth / ghost_running_detected=false / can_upgrade=false`
- `/api/schedules`: `[持续迭代] workflow` 当前 `last_result_status=running`

## 发布边界
- root_sync_state: `clean_synced_for_code_workspaces`
- ahead_count: `0`（pm-main 相对本机 `../workflow_code`）
- dirty_tracked_count: `32`（PM 根仓既有治理脏文件）
- untracked_count: `530`
- push_block_reason: `代码批已推本机根仓、workflow gate 已通过、candidate 已刷新；阻塞只剩 prod apply 与 post-candidate live recheck`
- next_push_batch: `prod candidate 20260428-131038 空窗升级后做 schedule handoff recovery live recheck`

## 下一步
- 不手工覆盖 prod；等待 supervisor 空窗或用户明确要求 apply。
- `20260428-131038` 升级后先做 schedule handoff recovery live recheck。
- live recheck 通过后再决定进入 `V13-R3` 下一 slice 或 `V13-R4`。
