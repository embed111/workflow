# workflow-pm-wake-summary 2026-04-15 08:00

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260415-a4602422`
- generated_at: `2026-04-15T09:01:03+08:00`

## 结果
- 08:00 巡检期间，主链未断：`patrol node-sti-20260415-a4602422 / running`，`mainline node-sti-20260415-7b4bda97 / queued`，且下一条 patrol future=`2026-04-15T09:00:00+08:00`
- 我这轮没有停在观察；先收掉了 `pm-main` 的 dirty batch，再把“升级后自动刷新 PM 当前版本快照”的链路补齐到可回归状态
- 当前 live `prod=20260415-080936`，新 `candidate=20260415-085343`，`candidate_is_newer=true / drain_active=true / running_task_count=1 / can_upgrade=false`

## 本轮推进性修改
- 代码修复：`scripts/apply_prod_candidate_when_idle.py` 在升级完成后会等待切版结果，并自动调用 `scripts/bin/refresh_pm_current_version_snapshot.py` 追平 `pm/PM当前版本计划.md` 与 `pm/versions/V2/版本计划.md`
- 验收收口：我新增了 `scripts/acceptance/verify_pm_current_version_snapshot_refresh.py`，并把 `verify_apply_prod_candidate_when_idle.py`、`verify_prod_auto_upgrade_single_check_helper.py`、`verify_runtime_upgrade_drain_hit_single_check.py` 对齐到新 watcher 合同
- 发布推进：`.repository/pm-main` 已提交 `7c2990c`，`../workflow_code` 已通过 `fetch + ff-only merge` 快进到同一提交，`test/prod candidate` 已刷新到 `20260415-085343`

## 版本判断
- lifecycle_stage: `开发实现`
- lane: `工程质量探测`
- version_transition_decision: `stay(V2)`
- next_activation_candidate: `V3`
- next_activation_ready: `true`
- switch_blockers: `R2 / R4 / R6 / R7`
- AAR: 本轮无新增 AAR；`V2-R6` ETA 仍是 `2026-04-15`，若到今日结束前仍未收口，下一轮必须先重设 ETA 或补 AAR

## Active 需求评估
- `V2-R1`: `completed / 100% / ETA=已于 2026-04-14 完成 / 未超时`
- `V2-R2`: `in_progress / 95% / ETA=2026-04-18 / 未超时`
- `V2-R3`: `completed / 100% / ETA=已于 2026-04-14 完成 / 未超时`
- `V2-R4`: `in_progress / 99% / ETA=2026-04-19 / 未超时`
- `V2-R5`: `completed / 100% / ETA=已于 2026-04-15 完成 / 未超时`
- `V2-R6`: `in_progress / 80% / ETA=2026-04-15 / 未超时`
- `V2-R7`: `in_progress / 99% / ETA=2026-04-16 / 未超时`
- `V2-R8`: `completed / 100% / ETA=已于 2026-04-13 完成 / 未超时`

## 发布边界
- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0 / untracked_count=0`
- `workspace_head=code_root_head=7c2990c`
- `push_block_reason=- / next_push_batch=R2/R6/R7 收口`

## 验证
- `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- `.repository/pm-main/.test/20260415-083327-454/report.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260415-085031.md`
- `.repository/pm-main/.test/20260415-090019-170/report.md`
- `.running/control/logs/test/deploy-20260415-085343.json`
- `Invoke-RestMethod http://127.0.0.1:8090/api/status`
- `Invoke-RestMethod http://127.0.0.1:8090/api/runtime-upgrade/status`

## 下一步
- 等 idle watcher 在空窗把 `20260415-085343` 切进 `prod`
- 切版后优先补一拍 `R4 / R7` current-version smoke
- 继续把 `R2 / R6 / R7` 压到可切版阈值
- memory_ref: `.codex/memory/2026-04/2026-04-15.md`
