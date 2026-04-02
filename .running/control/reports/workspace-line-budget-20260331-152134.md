# WORKSPACE_LINE_BUDGET_REPORT

- generated_at: 2026-03-31T15:21:36+08:00
- root: C:/work/J-Agents/workflow/.running/test
- report_path: C:/work/J-Agents/workflow/.running/control/reports/workspace-line-budget-20260331-152134.md
- json_report_path: C:/work/J-Agents/workflow/.running/control/reports/workspace-line-budget-20260331-152134.json
- scan_scope: maintained_source_and_automation_files
- refactor_trigger_lines: 1000
- hard_gate_pass: true
- refactor_triggered: true
- guideline_triggered: true
- trigger_action: trigger_refactor_skill

## Exclusions

| rule | reason |
|---|---|
| `runtime_artifacts` | 运行态、审计和测试产物不纳入工程重构预算。 |
| `workflow_docs` | 需求、设计、报告和截图文档不纳入代码体量门禁。 |

## Hard Gate

| rule | file | limit | lines | pass | reason |
|---|---|---:|---:|---|---|
| `workflow_web_server_main` | `src/workflow_app/workflow_web_server.py` | 3000 | 11 | pass | 工程化重构硬门禁：主入口必须瘦身到 3000 行以内。 |
| `legacy_api_entry` | `src/workflow_app/server/api/legacy.py` | 1000 | 6 | pass | 工程化重构硬门禁：legacy API 入口必须控制在 1000 行以内。 |

## Refactor Trigger Gate

- note: 该门槛用于发现 `> 1000` 行的维护中代码文件，并触发 `trigger_refactor_skill`。

| file | lines | threshold | action |
|---|---:|---:|---|
| `src/workflow_app/server/services/schedule_service.py` | 1556 | 1000 | `trigger_refactor_skill` |
| `src/workflow_app/server/services/defect_service.py` | 1294 | 1000 | `trigger_refactor_skill` |
| `scripts/acceptance/run_acceptance_role_creation_browser.py` | 1277 | 1000 | `trigger_refactor_skill` |
| `src/workflow_app/server/services/assignment_service_parts/task_artifact_store_core.py` | 1226 | 1000 | `trigger_refactor_skill` |
| `src/workflow_app/web_client/training_center_role_creation.js` | 1197 | 1000 | `trigger_refactor_skill` |
| `src/workflow_app/server/services/defect_service_task_commands.py` | 1183 | 1000 | `trigger_refactor_skill` |
| `src/workflow_app/server/services/assignment_service_parts/task_artifact_store_queries.py` | 1178 | 1000 | `trigger_refactor_skill` |
| `src/workflow_app/server/presentation/templates/index_training_loop_overview.css` | 1169 | 1000 | `trigger_refactor_skill` |
| `src/workflow_app/server/services/training_loop_service_parts/loop_round_runtime.py` | 1160 | 1000 | `trigger_refactor_skill` |
| `src/workflow_app/server/presentation/templates/index.html` | 1155 | 1000 | `trigger_refactor_skill` |
| `src/workflow_app/web_client/training_center_loop_views.js` | 1109 | 1000 | `trigger_refactor_skill` |
| `src/workflow_app/web_client/policy_confirm_and_interactions.js` | 1104 | 1000 | `trigger_refactor_skill` |
| `src/workflow_app/server/services/role_creation_service_parts/session_commands.py` | 1074 | 1000 | `trigger_refactor_skill` |
| `src/workflow_app/server/presentation/templates/index_training_center_role_creation.css` | 1069 | 1000 | `trigger_refactor_skill` |
| `src/workflow_app/server/services/assignment_service_parts/workspace_state_and_metrics.py` | 1063 | 1000 | `trigger_refactor_skill` |
| `src/workflow_app/server/presentation/templates/index_training_center_layout.css` | 1047 | 1000 | `trigger_refactor_skill` |
| `scripts/acceptance/run_acceptance_schedule_center_browser.py` | 1041 | 1000 | `trigger_refactor_skill` |
| `src/workflow_app/server/services/assignment_service_parts/task_artifact_store_run_runtime.py` | 1034 | 1000 | `trigger_refactor_skill` |
| `src/workflow_app/web_client/assignment_center_state_helpers.js` | 1029 | 1000 | `trigger_refactor_skill` |
| `src/workflow_app/server/services/assignment_service_parts/task_artifact_store_actions.py` | 1004 | 1000 | `trigger_refactor_skill` |

## Guideline Gate

- note: 该部分用于输出拆分计划义务，不直接决定默认发布链路的退出码。

| rule | limit | action | reason |
|---|---:|---|---|
| `backend_core_advisory` | 1500 | `provide_split_plan` | 后端核心业务文件建议 <= 1500 行，超出需给拆分计划。 |
| `frontend_core_advisory` | 1200 | `provide_split_plan` | 前端核心业务文件建议 <= 1200 行，超出需给拆分计划。 |

### Guideline Offenders

| file | lines | threshold | rule | action |
|---|---:|---:|---|---|
| `src/workflow_app/server/services/schedule_service.py` | 1556 | 1500 | `backend_core_advisory` | `provide_split_plan` |

## Notes

- 默认退出码仅由 `Hard Gate` 决定；`Refactor Trigger Gate` 与 `Guideline Gate` 用于提示后续重构动作。
- 若 `Refactor Trigger Gate` 命中，说明本轮需求完成后应补一轮设计模式/职责拆分重构。

