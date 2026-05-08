# Continuous Improvement Report

- generated_at: `2026-04-18T11:58:18+08:00`
- active_version: `V4`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- preference_ref: `state/user-preferences.md`
- delta_observation: `当 current-version smoke 继续硬编码旧 lane 或不覆盖 live recent failure pool 时，post-upgrade 验收会出现假红灯或漏掉真实 workboard 回退。`
- delta_validation: `等待 prod 空窗切到 20260418-115555 后，优先复跑 current-version smoke / recent-failure 合同，并继续观察 test 部署后的 T9 ghost 是否还会复现。`

## Summary

- 我把 `.repository/pm-main@3188351 test(smoke): 让V4 current-version验收跟随PM真相并锁住失败池排序` 收成正式批次：`collect_v4_r1_r4_current_version_smoke.py` 现在默认从 PM 版本真相解析 `active_version / lane / lifecycle_stage`，同时新增 live `recent failure pool` 的 recent-first / top4 合同。
- 我按默认发布约束跑通了 `line budget`、定向 live smoke 和完整 `workflow gate`，再把 `.repository/pm-main` 受支持地 fast-forward 收口到本机 `../workflow_code@3188351`。
- 我通过受支持的 developer workspace bootstrap/refresh 把 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 全部刷回 `clean_synced@3188351`，随后部署 `test / prod candidate=20260418-115555`，并再次执行 `repair-ghost-running` 把 `T9` 拉回 `failed`，让 `8092` 恢复到 `running_task_count=0 / ghost_running_detected=false`。

## Validation

- `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/20260418-114418-158/report.md`
- `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/runs/workflow-gate-acceptance-20260418-115122.md`
- `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/20260418-115226-404/report.md`
- `D:/code/AI/J-Agents/workflow/.running/control/logs/test/deploy-20260418-115555.json`
- `POST http://127.0.0.1:8092/api/runtime-upgrade/repair-ghost-running`
- `GET http://127.0.0.1:8090/api/status`
- `GET http://127.0.0.1:8090/api/runtime-upgrade/status`
- `GET http://127.0.0.1:8092/api/status`
- `GET http://127.0.0.1:8092/api/runtime-upgrade/status`

## Version Assessment

- `V4-R1`: `in_progress / 90% / eta=2026-04-19 / 未超时`
- `V4-R2`: `in_progress / 60% / eta=2026-04-20 / 未超时`
- `V4-R3`: `in_progress / 90% / eta=2026-04-20 / 未超时`
- `V4-R4`: `completed / 100% / eta=2026-04-17 / 未超时`
- `version_transition_decision=stay(V4)`；`next_activation_candidate=-`；`next_activation_ready=false`；本轮无新增 AAR

## Release Boundary

- `root_sync_state=clean_synced`
- `workspace_head=code_root_head=3188351`
- `ahead_count=0 / dirty_tracked_count=0 / untracked_count=0`
- `git -C .repository/pm-main status --short --branch = ## main...origin/main [ahead 4]`
- `git -C ../workflow_code status --short --branch = ## main...origin/main [ahead 134]`
- 上述 `ahead` 仅是本地 tracking ref 相对 GitHub 的参考视图，不构成当前 `workspace -> code_root` 阻塞

## Live Status

- `prod`: `current_version=20260418-111312 / candidate_version=20260418-115555 / candidate_is_newer=true / running_task_count=1 / can_upgrade=false / blocking_reason=存在运行中任务，暂不可升级`
- `test`: `current_version=20260418-115555 / candidate_version=20260418-115555 / running_task_count=0 / ghost_running_detected=false`
- `developer_workspaces`: `pm-main / workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate = clean_synced@3188351`
- `current-version smoke`: `lane_match=true / recent_failure_pool_sorted_recent_first=true / recent_failure_pool_limited_to_top4=true / browser_regression_passed=true`

## Next

- 等 `prod` idle watcher 在空窗把 `20260418-115555` apply 到 live
- 切版后复跑 `current-version smoke / recent-failure` 合同，确认 `3188351` 已进入 `prod`
- 继续观察 `test` 每次部署后的 `T9` ghost 是否还会复现，必要时把 post-deploy repair 再沉成更正式的 deploy contract
- memory_ref: `.codex/memory/2026-04/2026-04-18.md`
