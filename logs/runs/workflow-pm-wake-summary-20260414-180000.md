# workflow-pm-wake-summary-20260414-180000

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260414-3254c77a`
- task_name: `pm持续唤醒 - workflow 主线巡检 / 2026-04-14 17:40:00`
- executed_at: `2026-04-14T18:24:06+08:00`
- lane: `工程质量探测`
- lifecycle_stage: `开发实现`
- root_sync_state: `clean_synced`
- ahead_count: `0`
- dirty_tracked_count: `0`
- untracked_count: `0`
- push_block_reason: `-`
- next_push_batch: `待切批`

## Live Check

- `/healthz`: `ok=true`
- `/api/status`: `active_version=V2 / running_task_count=1 / queued_task_count=2 / workflow_mainline_starvation_state=mitigated / baseline=prod=20260414-172833`
- `/api/runtime-upgrade/status`: `current_version=20260414-172833 / candidate_version=20260414-181645 / candidate_is_newer=true / drain_active=true / can_upgrade=false / blocking_reason=running_tasks_present`
- `/api/schedules`: `mainline_last=node-sti-20260414-319104c6 / 待开始`；`patrol_last=node-sti-20260414-e59832de / 待开始`；`patrol_next=2026-04-14T18:20:00+08:00`
- assignment workboard: `workflow patrol running=node-sti-20260414-3254c77a`；`workflow mainline ready=node-sti-20260414-319104c6`；`workflow patrol ready=node-sti-20260414-e59832de`

## Forward Change

- 我新增了 `docs/workflow/testing/PM治理专项用例编号.md` 中的 `TC-PM-003`，把 `R4` 的 current-version 证据正式拉回 PM 侧编号体系。
- 我新增了 `.repository/pm-main/scripts/acceptance/verify_pm_current_version_tc_pm_003.py`，并把它接进 `.repository/pm-main/scripts/acceptance/workflow_gate_probe_registry.py`。
- 我在 `.repository/pm-main` 提交 `0f1a72c test(pm治理): 补齐TC-PM-003当前版治理回归`，随后用本机 `../workflow_code <- .repository/pm-main` 执行 `fetch + ff-only merge` 收口根仓。
- 我按默认发布约束先停掉旧 `test`，再把 `test/prod candidate` 刷到 `20260414-181645`，不直接触碰 `prod apply`。

## Validation

- line budget: `.repository/pm-main/.test/20260414-181246-740/report.md`
- py_compile: `.repository/pm-main/.test/20260414-181246-754/report.md`
- `TC-PM-003`: `.repository/pm-main/.test/20260414-182405-115/report.md`
- workflow gate: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260414-181444.md`
- live smoke: `.repository/pm-main/.test/20260414-181722-602/report.md`
- deploy test/candidate: `.running/control/logs/test/deploy-20260414-181645.json`

## Version Assessment

- `V2-R1`: `completed / 100% / ETA=已于 2026-04-14 完成 / 未超时`
- `V2-R2`: `in_progress / 95% / ETA=2026-04-18 / 未超时`
- `V2-R3`: `completed / 100% / ETA=已于 2026-04-14 完成 / 未超时`
- `V2-R4`: `in_progress / 90% / ETA=2026-04-19 / 未超时`
- `V2-R5`: `in_progress / 99% / ETA=2026-04-15 / 未超时`
- `V2-R6`: `in_progress / 80% / ETA=2026-04-15 / 未超时`
- `V2-R7`: `in_progress / 94% / ETA=2026-04-16 / 未超时`
- `V2-R8`: `completed / 100% / ETA=已于 2026-04-13 完成 / 未超时`
- 本轮没有需求点超时，因此未新增 `pm/versions/V2/aar/`。

## Next

- 当前最高优先级继续保持 `V2-R4`，下一步把 `TC-AWAKE-*` 的 PM 侧专项归档补齐。
- `V2-R5` 继续沿 `workflow_ucdmate` 的 `creating / workspace_init_status=completed` 现场沉淀正式编号化证据。
- `prod` 的下一次正式升级继续由 idle watcher 在 `running_task_count=0 && can_upgrade=true` 的空窗触发；我本轮不调用 `/api/runtime-upgrade/apply`。

- preference_ref: `state/user-preferences.md`
- delta_observation: `当 helper smoke 已稳定落成测试资产后，PM 侧仍需要补一条自己的 wrapper probe 和编号，否则 R4/R7 会长期停在“只有 helper 证据”的半收口状态。`
- delta_validation: `下一轮继续检查 `TC-AWAKE-*` 是否也需要像 `TC-PM-003` 一样折回 PM 侧编号与 gate。`
- memory_ref: `.codex/memory/2026-04/2026-04-14.md`
