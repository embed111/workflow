# 持续迭代报告 2026-04-15 00:33

- preference_ref: state/user-preferences.md
- delta_observation: live `prod=20260414-230303` 的 `/api/schedules` 只会动态替换 baseline，不会自动把旧 mainline/patrol 文案补到最新 `version_transition_decision` 合同；此外 `workflow_testmate` 的 candidate smoke 在 `test=8092` 又暴露出 `role_creation_session_not_found`
- delta_validation: 等 `20260415-003013` 切进 `prod` 后，用 `workflow_testmate` 补 1 轮 prod current-version smoke；若仍需先跑 test smoke，先补 role creation session 缺口

## 摘要

- lane: `工程质量探测`
- lifecycle_stage: `开发实现`
- active_version: `V2`
- version_transition_decision: `stay`
- baseline: `prod=20260414-230303`
- candidate: `20260415-003013`
- root_sync_state: `clean_synced`
- workspace_head: `597f26f`
- code_root_head: `597f26f`
- memory_ref: `.codex/memory/2026-04/2026-04-15.md`

## 关键动作

1. 扩展 `.repository/pm-main/scripts/acceptance/collect_v2_r4_r5_current_version_smoke.ps1`，新增 `document_baseline` 与 mainline/patrol prompt sync 断言。
2. 修复 `.repository/pm-main/src/workflow_app/server/services/schedule_text_repair.py` 与 `.repository/pm-main/src/workflow_app/server/services/schedule_service.py`，把旧 schedule repair / backup schedule create 一并补到最新版本切换合同。
3. 新增 `.repository/pm-main/scripts/acceptance/verify_schedule_prompt_contract_repair.py`，并让 `.repository/pm-main/scripts/acceptance/verify_pm_awake_tc_pack.py` 继续通过。
4. 收口 `.repository/pm-main` 到 `f80064c / 597f26f`，并通过 `../workflow_code <- .repository/pm-main` 的 `fetch + ff-only merge` 把根仓同步到 `597f26f`。
5. 刷新 `pm-main / workflow_testmate` developer workspace，并把 `test/prod candidate` 刷到 `20260415-003013`。

## 验证

- `.repository/pm-main/.test/20260415-001646-858/report.md`
- `.repository/pm-main/.test/20260415-002027-778/report.md`
- `.repository/pm-main/.test/20260415-002500-035/report.md`
- `.repository/pm-main/.test/20260415-002240-621/report.md`
- `.running/control/logs/test/deploy-20260415-003013.json`
- `.repository/workflow_testmate/.test/20260415-003043-738/report.md`

## Warning

- `workflow_testmate` 对 `test=8092` 的 candidate smoke 目前失败在 `role_creation_session_not_found`；这条 warning 已冻结，不把它误记成 candidate 已验证通过。
