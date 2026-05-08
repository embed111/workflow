# V13 governance readiness check

- created_at: `2026-04-25T12:33:21+08:00`
- operator: `workflow(pm)`
- preference_ref: `state/user-preferences.md`

## 结论
- 全仓“逻辑太散 / 冗余实现偏重”尚未完成根治；当前完成的是 `V13` 治理基线、版本计划、review 门禁和生产创建的 review 小伙伴。
- `V13` activation readiness schema 已修正并复核通过，`warning_versions=[]`，`row_issue_count=0`。
- `workflow_reviewmate` 已能从生产 DB、`/api/training/agents` 和 `state/developer-workspaces.json` 回读，当前 `training_gate_state=trainable / runtime_status=idle`。
- `V12` 仍是 `next_activation_candidate`，但 `next_activation_ready=false`；`V13` 不能越过 `V11/V12` 的 blocker 直接 active。

## 验证
- `python .repository/pm-main/scripts/acceptance/verify_planned_version_activation_readiness.py`
  - report: `.test/20260425-123034-498/report.md`
  - result: `ok=true`
- `python .repository/pm-main/scripts/acceptance/verify_pm_version_board_view.py`
  - report: `.test/20260425-123238-266/report.md`
  - result: `ok=true`
  - note: `next_activation_ready=false`，符合当前 `V12` planned with blockers 状态。
- `python scripts/quality/check_workspace_line_budget.py --root .`
  - root: `.repository/pm-main`
  - report: `.repository/pm-main/.test/20260425-123238-339/report.md`
  - summary: `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- live prod role checks:
  - `agent_registry.workflow_reviewmate`: `pre_release / trainable / idle`
  - `role_creation_task_refs`: `6`
  - `/api/training/agents`: `workflow_reviewmate` found
  - `state/developer-workspaces.json`: `workflow_reviewmate` registered and `clean_synced`
  - `/api/runtime-upgrade/status`: `current_version=20260425-113551 / candidate_version=20260425-113551 / running_task_count=0 / ghost_running_detected=false`

## 仍未关闭
- `/api/training/role-creation/sessions/rcs-20260425-114824-0c06b3` detail 读面超时问题仍未根治，继续归入 `V12-R1`。
- `V13` 仍是 planned；真正代码级全仓重构要等 `V11/V12` blocker 收口后，先从 `V13-R1` 架构地图与删除清单开始。
