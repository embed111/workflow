# Continuous Improvement Report - 2026-04-14 12:58:09

- preference_ref: `state/user-preferences.md`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260414-10cdec57`
- focus: `工程质量探测 / 发布推进`

## Summary
- 我把 `dashboard -> schedule_workboard_preview` 改成 compact 读链：`/api/status` 的任务看板预览只保留 `schedule_name / next_trigger / last_result_*` 等工作面字段，不再回传整段 `launch_summary / execution_checklist / done_definition`，同时只走 `_assignment_runtime_status_from_task_files()` 的快路径。
- 我把 `verify_dashboard_schedule_preview.py` 扩成门禁约束，并把它纳入 `workflow gate`。
- 我在 `.repository/pm-main` 提交 `11e66f1 fix(status): 压缩任务看板定时预览并纳入门禁`，同步 `../workflow_code=11e66f1`，再刷新 `test/prod candidate=20260414-125438`。
- 我用当前工作区的新代码直接测了 `prod` runtime 根：`workboard_payload=266.74ms`、`list_assignments=150.58ms`，说明慢点已经被压到 workboard 可接受量级；当前 `prod(8090)` 仍运行旧版 `101552`，要等 idle watcher 把 `125438` 切进 live 才会真正吃到这次 compact preview。

## Validation
- line budget: `.repository/pm-main/.test/20260414-125033-607/report.md`
- dashboard schedule preview probe: `.repository/pm-main/.test/20260414-125049-643/report.md`
- workflow gate: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260414-125234.md`
- latency measurement: `.repository/pm-main/.test/20260414-125622-102/report.md`
- deploy report: `.running/control/logs/test/deploy-20260414-125438.json`
- live API:
  - `/api/status` => `baseline=prod=20260414-101552 / running_task_count=1 / queued_task_count=2 / workflow_mainline_starvation_state=mitigated`
  - `/api/schedules` => `mainline_last=node-sti-20260414-530e47ac / queued`，`patrol_last=node-sti-20260414-32523778 / queued`，`patrol_next=2026-04-14T13:00:00+08:00`
  - `/api/runtime-upgrade/status` => `current_version=20260414-101552 / candidate_version=20260414-125438 / candidate_is_newer=true / drain_active=true / running_task_count=1`

## Release Boundary
- `root_sync_state=clean_synced`
- `ahead_count=0 / dirty_tracked_count=0 / untracked_count=0`
- `workspace_head=code_root_head=11e66f1`
- `push_block_reason=- / next_push_batch=待切批`
- `.repository/pm-main` 相对 `origin/main` 为 `ahead 1`、`../workflow_code` 相对 `origin/main` 为 `ahead 51`，仅作上游镜像参考，不构成本轮 release boundary 异常

## V2 Evaluation
- `V2-R1`: `completed / 100% / 已于 2026-04-14 完成 / -`
- `V2-R2`: `in_progress / 93% / 2026-04-18 / 未超时`
- `V2-R3`: `in_progress / 99% / 2026-04-19 / 未超时`
- `V2-R4`: `in_progress / 68% / 2026-04-19 / 未超时`
- `V2-R5`: `in_progress / 96% / 2026-04-15 / 未超时`
- `V2-R6`: `in_progress / 80% / 2026-04-15 / 未超时`
- `V2-R7`: `in_progress / 82% / 2026-04-16 / 未超时`
- `V2-R8`: `completed / 100% / 已于 2026-04-13 完成 / -`
- 本轮无新超时项，不触发 AAR

## Next
- 等 idle watcher 在空窗把 `20260414-125438` 切进 `prod`，随后优先复核 `8090 /api/status` 是否已经切到 compact schedule preview
- 继续围绕 `V2-R4` 固化编号化治理证据，再把窗口切回 `R5 / R2`
- 当前最近 mainline 节点为 `node-sti-20260414-530e47ac / queued`，保底下一拍为 `2026-04-14T13:00:00+08:00`
