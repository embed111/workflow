# Run Log

- topic: test data environment policy and toggle removal
- recorded_at: 2026-03-18T22:28:17+08:00
- preference_ref: state/user-preferences.md
- workspace: `D:\code\AI\J-Agents\workflow`
- prompt: `docs/workflow/prompts/执行提示词-测试数据环境策略与开关下线开工-20260318.md`
- live_prod_url: `http://127.0.0.1:8090`
- evidence_root: `logs/runs/test-data-env-policy-prod-20260318-222327`
- verification: `.test/20260318-222046-586/report.md`

## Changed Files

- `src/workflow_app/server/bootstrap/web_server_runtime_parts/runtime_paths_and_config.py`
- `.running/prod/src/workflow_app/server/bootstrap/web_server_runtime_parts/runtime_paths_and_config.py`
- `scripts/acceptance/assignment_test_data_toggle_probe.py`
- `scripts/acceptance/run_acceptance_assignment_center_browser.py`
- `src/workflow_app/server/bootstrap/web_server_runtime_parts/event_persistence_and_flags.py`
- `src/workflow_app/server/api/config.py`
- `src/workflow_app/server/api/legacy_task_config_handlers.py`
- `src/workflow_app/server/api/chat.py`
- `src/workflow_app/server/api/dashboard.py`
- `src/workflow_app/server/api/training.py`
- `src/workflow_app/server/api/assignments.py`
- `src/workflow_app/server/presentation/templates/index.html`
- `src/workflow_app/web_client/app_status_and_icon_utils.js`
- `src/workflow_app/web_client/app_runtime_state_helpers.js`
- `src/workflow_app/web_client/policy_confirm_and_interactions.js`
- `src/workflow_app/web_client/policy_session_gate_state.js`
- `src/workflow_app/web_client/app_navigation_and_event_binding.js`
- `src/workflow_app/web_client/app_runtime_controls.js`
- `scripts/deploy_workflow_env.ps1`
- `scripts/acceptance/run_acceptance_runtime_release_gate.py`
- `scripts/acceptance/README.md`

## Evidence

- settings screenshot: `logs/runs/test-data-env-policy-prod-20260318-222327/screenshots/settings-no-toggle.png`
- session entry screenshot: `logs/runs/test-data-env-policy-prod-20260318-222327/screenshots/session-entry-prod-hidden.png`
- training/dashboard screenshot: `logs/runs/test-data-env-policy-prod-20260318-222327/screenshots/training-dashboard-policy.png`
- sessions/queue screenshot: `logs/runs/test-data-env-policy-prod-20260318-222327/screenshots/sessions-queue-policy.png`
- task center screenshot: `logs/runs/test-data-env-policy-prod-20260318-222327/screenshots/task-center-prod-hidden.png`
- settings probe: `logs/runs/test-data-env-policy-prod-20260318-222327/probes/settings-no-toggle.probe.json`
- session probe: `logs/runs/test-data-env-policy-prod-20260318-222327/probes/session-entry-prod-hidden.probe.json`
- training/dashboard probe: `logs/runs/test-data-env-policy-prod-20260318-222327/probes/training-dashboard-policy.probe.json`
- task center probe: `logs/runs/test-data-env-policy-prod-20260318-222327/probes/task-center-prod-hidden.probe.json`
- GET policy API: `logs/runs/test-data-env-policy-prod-20260318-222327/api/show_test_data_get.json`
- POST removed API: `logs/runs/test-data-env-policy-prod-20260318-222327/api/show_test_data_post_removed.json`
- status API: `logs/runs/test-data-env-policy-prod-20260318-222327/api/status.json`
- dashboard API: `logs/runs/test-data-env-policy-prod-20260318-222327/api/dashboard.json`
- training agents API: `logs/runs/test-data-env-policy-prod-20260318-222327/api/training_agents.json`
- chat sessions API: `logs/runs/test-data-env-policy-prod-20260318-222327/api/chat_sessions.json`
- assignments API: `logs/runs/test-data-env-policy-prod-20260318-222327/api/assignments.json`
- runtime config copy: `logs/runs/test-data-env-policy-prod-20260318-222327/config/runtime-config.json`
- prod instance copy: `logs/runs/test-data-env-policy-prod-20260318-222327/config/prod.json`
- prod pid copy: `logs/runs/test-data-env-policy-prod-20260318-222327/config/prod.pid`

## AC Mapping

- `docs/workflow/overview/需求概述.md`: 已完成；对齐第 38 节“测试数据展示改为环境策略并下线设置开关”，`prod` 由环境策略只读隐藏测试数据，页面不再提供用户覆盖入口。证据见 `logs/runs/test-data-env-policy-prod-20260318-222327/summary.json` 与上述截图/API。
- `docs/workflow/requirements/需求详情-测试数据展示全局开关统一.md`: 已完成；FR-TD-01/02/03/05/06/07/08/09 已在 live prod 取证，`GET /api/config/show-test-data` 为只读环境口径，`POST /api/config/show-test-data` 返回 `410 show_test_data_toggle_removed`，设置页/会话入口/训练中心/任务中心 probe 全部 `pass=true`。AC-TD-07 的代码补充了 `runtime-config invalid_json` 启动告警与 `prod fail-closed`，本轮未对 live prod 主实例主动注入坏配置。
- `docs/workflow/requirements/需求详情-统一入口与训练优化模块.md`: 已完成；旧 `include_test_data` 用户开关语义不再作为真实控制源，统一由后端环境策略决定，训练中心与会话列表回包均带 `environment/show_test_data/show_test_data_source`，前端仅作只读消费。
- `docs/workflow/design/详细设计-测试数据展示全局开关统一.md`: 已完成；后端环境策略解析、旧写接口废弃返回、前端只读元信息、历史本地缓存清理、prod fail-closed 告警以及任务中心相关验收脚本迁移均已落地。

## Notes

- live prod 当前 PID: `50156`
- live prod 当前策略: `environment=prod`, `show_test_data=false`, `show_test_data_source=environment_policy`
- 仍存在若干历史验收脚本保留 `include_test_data` 兼容查询参数，但运行时 `withTestDataQuery(...)` 已退化为 no-op，后端 `resolve_include_test_data(...)` 已忽略用户级 query override，不再影响真实行为
