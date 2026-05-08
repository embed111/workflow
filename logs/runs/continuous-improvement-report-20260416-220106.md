# Continuous Improvement Report 2026-04-16 22:01:06 +08:00

- active_version: `V3`
- lane: `工程质量探测`
- lifecycle_stage: `开发实现`
- version_transition_decision: `stay(V3)`
- preference_ref: `state/user-preferences.md`

## Summary
- 我把 `/api/schedules` 的慢链路继续收窄到 workflow 主线/巡检 schedule 的动态 prompt 上下文重复读取，并把修复批次提交为 `.repository/pm-main@2989d4c`。
- 我把本机 `../workflow_code` fast-forward 到同一提交，随后重发 `test`，刷新出新的 `prod candidate=20260416-215204`。
- 我又把 `workflow_bugmate / workflow_testmate / workflow_devmate / workflow_qualitymate / workflow_ucdmate / pm-main` 六个 developer workspace 全部追到 `clean_synced@2989d4c`。

## Live Truth
- 当前 `prod=current_version=20260416-205559`，`candidate_version=20260416-215204`，`candidate_is_newer=true`，`drain_reason_code=candidate_newer_pending_idle_window`，`running_task_count=1`。
- 当前 workflow 现场为：主线 `node-sti-20260416-93d44977=running`，下一条主线 `node-sti-20260416-490e1ffa=ready`，保底巡检 `node-sti-20260416-e6c72c70=ready`。
- 旧 live `205559` 上的 `/api/schedules` 在 `8090` 仍然会超时到 `30s+`，说明剩余风险已经收窄为“prod 还没切到新 candidate”，不是这批代码继续失效。

## Validation
- `.repository/pm-main/.test/20260416-213718-008/report.md`
- `.repository/pm-main/.test/20260416-213730-559/report.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260416-215040.md`
- `.repository/pm-main/.test/20260416-215757-939/report.md`
- `.running/control/logs/test/deploy-20260416-215204.json`
- `python` 直测 live `runtime_root`: `list_schedules(...) = 9.101s`
- `test(8092)` smoke：`current_version=20260416-215204`、`/api/schedules=30ms`、`developer_workspace_count=6`

## Release Boundary
- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `workspace_head=code_root_head=2989d4c`
- `push_block_reason=-`
- `next_push_batch=等待 idle watcher 在空窗把 20260416-215204 切进 live；切版后优先复跑 prod current-version smoke`

## Delta
- delta_observation: 旧 live `205559` 的 `/api/schedules` 仍会在 `8090` 超时，但新 candidate `215204` 已在 `test(8092)` 把同一路径压到 `30ms`，且 6 个 developer workspace 都已回到 `clean_synced@2989d4c`。
- delta_validation: 等 `215204` 命中空窗切进 `prod` 后，优先复跑 prod current-version smoke，确认 `/api/schedules` 低于 `15000ms`，再收 `V3-R5 / V3-R2`。
