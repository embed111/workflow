# Continuous Improvement Report

## 判断
- version_transition_decision: `stay(V8)`
- current_lane: `发布推进`
- lifecycle_stage: `验收`
- baseline: `prod=20260423-032918`
- stay_reason: `V9-R1` 的 startup-readiness consumer gap 已在 `pm-main@7cd49f9` 与 `workflow_code@fd9aad2` 收口到产品读面，并已通过 `workflow gate` 与 `test/current=candidate=20260423-044105`；当前仍不切 `V9`，因为 `V9-R3` 的项目创建入口 / 项目产出图表达还缺产品实现、浏览器 probe 与 live regression，`/api/status` 仍为 `next_activation_candidate=V9 / next_activation_ready=false`。

## 推进
- 我先把 `pm-main` refresh 到 `workflow_code@abd6bf9`，再在 `project_task_summary_service.py`、`project_ops_center.js`、`assignment_center_workboard_sections.js` 接入 `startup_ready / startup_readiness / blocking_items` 的消费链，同时保留 quiet-ready / proof 与 active signal 的原有优先级。
- 我补了 `verify_project_creation_contract_startup_readiness.py`、`verify_project_ops_module_ui.js`、`verify_assignment_workboard_project_entry.js` 和 `verify_project_ops_live_regression.py` 的回归断言，并把最后一条 probe 兼容到新的 `项目启动准入已就绪` 文案。
- 我跑过 `workspace line budget`、三条定向 probe、完整 `workflow gate`，随后把本地发布边界收成 `pm-main=workflow_code=clean_synced@fd9aad2`，并把 `test/current=candidate` 刷到 `20260423-044105`；`prod` 当前仍是 `20260423-032918`，新的 candidate `20260423-044105` 正在等空窗升级。

## 证据
- `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- `.repository/pm-main/.test/20260423-041613-629/report.md`
- `.repository/pm-main/.test/20260423-041613-656/report.md`
- `.repository/pm-main/.test/20260423-041613-661/report.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260423-043448.md`
- `.running/control/logs/test/deploy-20260423-044105.json`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `http://127.0.0.1:8092/api/runtime-upgrade/status`

## Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: 用户更看重我先把 active/next 版本的真实 blocker 收成产品动作和发布动作，不接受只停在 helper 本地边界或状态播报。
- delta_validation: 下一轮优先让 `V9-R3` 进入 `pm-main` 的真实产品实现与 browser/live regression，再重检 `switch(V9)`。

- memory_ref: `.codex/memory/2026-04/2026-04-23.md`
