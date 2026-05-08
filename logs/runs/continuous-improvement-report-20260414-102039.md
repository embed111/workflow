# Continuous Improvement Report - 2026-04-14 10:37:04

- preference_ref: `state/user-preferences.md`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260414-459eff53`
- focus: `发布推进 / helper workspace 治理`

## Summary
- 我修复了 developer workspace bootstrap/refresh 的 remote 策略，让它默认绑定本机 `../workflow_code`，不再继承 GitHub `origin`。
- 我补强了 workflow gate fixture，显式构造“source repo 自带上游镜像 remote”的现场，并断言 bootstrap 后的 workspace remote 仍然必须等于本地 code root。
- 我给 `.repository/workflow_devmate` 留下 `backup/pre-local-root-refresh-20260414-1009` 后，把它从 `1b62726 / 6b8a3e3` 刷回 `c9571af`，`remote.origin.url` 也改回 `D:/code/AI/J-Agents/workflow_code`。
- 我在 `.repository/pm-main` 提交 `c9571af fix(workspace): 开发工作区refresh默认绑定本机代码根仓`，同步 `../workflow_code=c9571af`，并刷新 `test/prod candidate=20260414-101552`。

## Validation
- line budget: `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- workflow gate: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260414-100519.md`
- deploy report: `.running/control/logs/test/deploy-20260414-101552.json`
- workspace registry: `state/developer-workspaces.json`
- live API:
  - `/api/status` => `baseline=prod=20260414-093304 / running_task_count=1 / queued_task_count=2`
  - `/api/runtime-upgrade/status` => `current_version=20260414-093304 / candidate_version=20260414-101552 / candidate_is_newer=true / drain_active=true`

## Release Boundary
- `root_sync_state=clean_synced`
- `ahead_count=0 / dirty_tracked_count=0 / untracked_count=0`
- `workspace_head=code_root_head=c9571af`
- `push_block_reason=- / next_push_batch=待切批`
- `workflow_devmate` 已从 stale base 收口到 `c9571af`；其余 helper registry 仍保留旧 GitHub remote 记录，但当前不构成本轮 blocker

## V2 Evaluation
- `V2-R1`: `completed / 100% / 已于 2026-04-14 完成 / -`
- `V2-R2`: `in_progress / 93% / 2026-04-18 / 未超时`
- `V2-R3`: `in_progress / 99% / 2026-04-19 / 未超时`
- `V2-R4`: `in_progress / 56% / 2026-04-19 / 未超时`
- `V2-R5`: `in_progress / 96% / 2026-04-15 / 未超时`
- `V2-R6`: `in_progress / 80% / 2026-04-15 / 未超时`
- `V2-R7`: `in_progress / 82% / 2026-04-16 / 未超时`
- `V2-R8`: `completed / 100% / 已于 2026-04-13 完成 / -`
- 本轮无新超时项，不触发 AAR

## Next
- 等 idle watcher 在空窗把 `20260414-101552` 切进 `prod`
- 继续围绕 `R2 / R5` 判断是否还需要独立版本详情页
- 按需把同一条 local-root remote 口径推广到其他 helper workspace
