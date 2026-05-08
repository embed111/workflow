# Continuous Improvement Report

- generated_at: `2026-04-14T22:17:05+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260414-eaaa2eb6`
- active_version: `V2`
- lane: `工程质量探测`
- lifecycle_stage: `开发实现`

## Summary
- 我把 `V2-R4 / V2-R7` 里一个会制造假通过的自迭代验收缺口收掉了：`.repository/pm-main/scripts/acceptance/run_acceptance_assignment_self_iteration_schedule.py` 不再用 `cmd.exe /c rem` 伪造 success，而是改成会吞掉 `stdin` 并回结构化结果的 success stub，同时把“原节点必须 `succeeded`”收成显式断言。
- 我把这批改动在 `.repository/pm-main` 提交为 `ed63521 test(持续唤醒): 修正自迭代验收stub并强制原节点成功`，并已 fast-forward 收口到本机 `../workflow_code`。
- 我停掉旧 `test` 环境后重跑部署，把新的 `test/prod candidate` 刷到 `20260414-220241`；live `prod` 仍保持 `20260414-185947`，当前由 idle watcher 在空窗接手升级。
- 我补跑了 `TC-PM-003`，确认 `pm/PM当前版本计划.md`、`pm/versions/V2/版本计划.md` 和 live `prod=20260414-185947` 的 baseline 已重新对齐。

## Evidence
- line budget: `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- self-iteration acceptance: `.repository/pm-main/.test/20260414-214752-568/report.md`
- PM awake pack wrapper: `.repository/pm-main/.test/20260414-214935-401/report.md`
- workflow gate: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260414-215515.md`
- current-version smoke: `.repository/pm-main/.test/20260414-221620-901/report.md`
- test deploy / prod candidate: `.running/control/logs/test/deploy-20260414-220241.json`

## Release Boundary
- `root_sync_state=clean_synced`
- `workspace_head=code_root_head=ed63521`
- `ahead_count=0 / dirty_tracked_count=0 / untracked_count=0`
- `.repository/pm-main` 相对 `origin/main ahead 4`、`../workflow_code` 相对 `origin/main ahead 58` 仅作上游镜像参考，不构成本机 release boundary 阻塞
- live `prod=current_version=20260414-185947 / candidate_version=20260414-220241 / candidate_is_newer=true / drain_active=true / running_task_count=1`

## Active Requirements
- `V2-R1`: `completed / 100% / ETA=已于 2026-04-14 完成 / 超时=-`
- `V2-R2`: `in_progress / 95% / ETA=2026-04-18 / 超时=未超时`
- `V2-R3`: `completed / 100% / ETA=已于 2026-04-14 完成 / 超时=-`
- `V2-R4`: `in_progress / 96% / ETA=2026-04-19 / 超时=未超时`
- `V2-R5`: `in_progress / 99% / ETA=2026-04-15 / 超时=未超时`
- `V2-R6`: `in_progress / 80% / ETA=2026-04-15 / 超时=未超时`
- `V2-R7`: `in_progress / 97% / ETA=2026-04-16 / 超时=未超时`
- `V2-R8`: `completed / 100% / ETA=已于 2026-04-13 完成 / 超时=-`
- 本轮无需求点超时，不触发新的 `pm/versions/V2/aar/*.md`

## Risks And Next
- 当前最高剩余风险不是自迭代验收假通过，而是 `20260414-220241` 仍在 `drain_active=true` 等待 idle window；主线还在 `running`，watcher 暂时不能升级。
- 下一步在 `220241` 切进 live 后，优先补一拍 `R4 / R7` 的新基线 current-version smoke，并把下一条高价值领域切片优先派给对应 helper 承接。

## Trace
- preference_ref: `state/user-preferences.md`
- memory_ref: `.codex/memory/2026-04/2026-04-14.md`
