# 7x24 workflow 主线终态 trigger 断链恢复

- created_at: `2026-04-28T13:13:00+08:00`
- operator: `pm-main`
- preference_ref: `state/user-preferences.md`
- scope: `[持续迭代] workflow`

## 结论
- 根因：`_resume_pending_schedule_triggers()` 能把已经终态的 trigger / plan 修回 `succeeded`，但没有同步回填 `assignment_mainline_handoffs`。如果 finalize 当时没有成功记录 durable handoff，就会出现“上一棒成功，但 `[持续迭代] workflow` 没有下一棒”的断链。
- 本次 live 断点：`node-sti-20260428-e5a821de / arun-20260428-063136-5398cb` 已在 `2026-04-28T07:01:45+08:00` 成功终态，但没有 handoff。
- 处置：已用当前 runtime 回填 live handoff，并把修复做成代码路径：终态 trigger 恢复时自动寻找最新 terminal run，补 durable handoff 并 drain 到下一次主线 schedule。

## 红灯
- session: `.repository/pm-main/.test/20260428-122917-361/report.md`
- command: `python scripts/acceptance/verify_schedule_terminal_trigger_progress_recovery.py`
- 失败点：终态 trigger 被恢复为 `succeeded` 后，`assignment_mainline_handoffs` 仍为空。

## 绿灯
- targeted recovery: `.repository/pm-main/.test/20260428-123452-134/report.md`
- related handoff outbox: `.repository/pm-main/.test/20260428-123143-871/report.md`
- finalize exception backfill: `.repository/pm-main/.test/20260428-123156-064/report.md`
- py_compile: `.repository/pm-main/.test/20260428-123501-983/report.md`
- line budget: `.repository/pm-main/.test/20260428-123513-485/report.md`
- full workflow gate: `.repository/pm-main/.test/20260428-125652-181/report.md`
- gate report: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260428-130436.md`

## 代码与发布
- commit: `cf38fc8 fix(schedule): 终态 trigger 恢复时回填主线 handoff`
- code root: `../workflow_code/main` 已 fast-forward 到 `cf38fc8`
- test stop: `.repository/pm-main/.test/20260428-130840-984/report.md`
- test deploy: `.repository/pm-main/.test/20260428-130855-235/report.md`
- deploy report: `.running/control/logs/test/deploy-20260428-130858.json`
- candidate: `prod candidate=20260428-130858`
- prod: 未做覆盖式升级；当前 `prod=20260428-065217`，等待空窗或手动升级。

## Live 复核
- `/healthz`: ok
- `[持续迭代] workflow`: `last_trigger_at=2026-04-28T12:52:00+08:00`，`last_result_status=running`，`node=node-sti-20260428-529c29b0`
- workflow run: `arun-20260428-125232-63a54a`，`execution_truth=live_execution`，`provider_pid=44648`，`latest_event_at=2026-04-28T13:10:16+08:00`
- `[持续迭代] novel_project_pm`: `next_trigger_at=2026-04-28T14:14:00+08:00`
- `Comics Bootstrap Smoke / project-comics-smoke`: 保持退役，不恢复 active。

## 增量观察
- delta_observation: 本轮完整 gate 初次红灯不是本次代码修复引起，而是 PM 当前版本快照、V13 矩阵和 V14 planned/not_ready 文档形态不再满足既有治理探针。
- delta_validation: 已通过文档对齐把相关 PM 探针转绿；后续如果 `V14` 仍未准备激活，应保持 `backlog`，不要标成 `planned`。
