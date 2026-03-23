# Schedule Center Browser Acceptance 20260324-001036

- time: `2026-03-24T00:10:36.4532712+08:00`
- scope: `定时任务模块 + 日历视图 + 任务中心联动`
- prompt: `docs/workflow/prompts/执行提示词-定时任务模块与日历视图开工-20260323.md`
- source_root: `D:\code\AI\J-Agents\workflow`
- environment: `test`
- version: `20260324-000613`
- preference_ref: `state/user-preferences.md`
- delta_observation: 用户继续要求按提示词直执行，并把真实浏览器验收、`test` 发布与证据路径作为最低交付。
- delta_validation: 后续涉及任务中心或训练中心主流程改动时，继续优先交付浏览器 probe、截图与 API/DB/日志证据，不以静态页面或服务级 smoke 替代。

## Result

- `test` 发布成功，版本 `20260324-000613`；gate 结果 `passed`。
- 真实浏览器验收通过，执行对象为 `.running/test`，隔离 runtime session 为 `.test/20260324-000626-894`。
- 已覆盖列表默认态、列表详情态、编辑态、日历月视图、切月视图、命中后显示真实等待或运行结果的详情态。
- 已捕获计划新增、编辑、启用、停用、同分钟去重、命中建单、请求调度、任务中心实时状态与审计留痕证据。
- `terminal_status_observed=false`；本轮以已观测到的真实 `starting/running` 状态以及去重、来源字段和联动留痕证据作为通过依据。

## Code Landing

- 页面入口与样式：`src/workflow_app/server/presentation/templates/index.html`、`src/workflow_app/server/presentation/templates/index_schedule_center.css`、`src/workflow_app/web_client/app_navigation_and_event_binding.js`
- 计划 CRUD 与列表/日历交互：`src/workflow_app/web_client/schedule_center_events.js`、`src/workflow_app/web_client/schedule_center_render_runtime.js`、`src/workflow_app/web_client/schedule_center_state_helpers.js`
- 后端接口、命中扫描、同分钟去重与任务中心联动：`src/workflow_app/server/api/schedules.py`、`src/workflow_app/server/services/schedule_service.py`
- 验收与 probe：`src/workflow_app/web_client/app_runtime_controls.js`、`scripts/acceptance/run_acceptance_schedule_center_browser.py`

## Evidence

- 语法与 bundle 预检：`.test/20260324-000559-902/report.md`
- deploy 报告：`.running/control/logs/test/deploy-20260324-000613.json`
- gate 报告：`.running/control/reports/test-gate-20260324-000613.json`
- 浏览器验收 session：`.test/20260324-000626-894/report.md`
- 浏览器验收摘要：`.test/20260324-000626-894/artifacts/schedule-center-browser/summary.json`
- 浏览器验收报告：`.test/20260324-000626-894/artifacts/schedule-center-browser/acceptance-report.md`
- 截图：`.test/20260324-000626-894/artifacts/schedule-center-browser/screenshots/list_default.png`、`.test/20260324-000626-894/artifacts/schedule-center-browser/screenshots/list_detail.png`、`.test/20260324-000626-894/artifacts/schedule-center-browser/screenshots/editor_edit.png`、`.test/20260324-000626-894/artifacts/schedule-center-browser/screenshots/calendar_month.png`、`.test/20260324-000626-894/artifacts/schedule-center-browser/screenshots/calendar_shifted.png`、`.test/20260324-000626-894/artifacts/schedule-center-browser/screenshots/result_detail.png`
- CRUD 与启停接口：`.test/20260324-000626-894/artifacts/schedule-center-browser/api/create_response.json`、`.test/20260324-000626-894/artifacts/schedule-center-browser/api/edit_response.json`、`.test/20260324-000626-894/artifacts/schedule-center-browser/api/disable_response.json`、`.test/20260324-000626-894/artifacts/schedule-center-browser/api/enable_response.json`
- 去重与联动接口：`.test/20260324-000626-894/artifacts/schedule-center-browser/api/scan_create_response.json`、`.test/20260324-000626-894/artifacts/schedule-center-browser/api/scan_dedupe_response.json`、`.test/20260324-000626-894/artifacts/schedule-center-browser/api/schedule_detail_after_scan.json`
- 任务中心状态读取：`.test/20260324-000626-894/artifacts/schedule-center-browser/api/assignment_status_live.json`、`.test/20260324-000626-894/artifacts/schedule-center-browser/api/assignment_status_terminal.json`
- 日志与数据留痕：`.test/20260324-000626-894/artifacts/schedule-center-browser/logs/schedule_events.json`、`.test/20260324-000626-894/artifacts/schedule-center-browser/db/schedule_trigger_instances.json`、`.test/20260324-000626-894/artifacts/schedule-center-browser/db/schedule_audit_log.json`、`.test/20260324-000626-894/artifacts/schedule-center-browser/db/assignment_nodes.json`、`.test/20260324-000626-894/artifacts/schedule-center-browser/assignment_node.json`

## Key Observations

- 定时任务到任务中心的建单/调度联动没有独立公开 HTTP 接口；本轮以 `/api/schedules/scan` 返回、`schedule_audit_log`、`logs/events/schedules.jsonl` 留痕和任务中心 `status-detail` 组合作为联动证据。
- 浏览器 probe 已修复切月后的刷新竞态；切到 `2026-04` 时，月份标题、日期格事件数量和右侧详情上下文都能同步刷新。
- 验收强制把 `agent_search_root` 设为 `D:\code\AI\J-Agents`，并把 `artifact_root`、`task_artifact_root` 隔离到 session 产物目录，避免污染正式运行态。
- 隔离 runtime 的 SQLite 中可能不存在 `assignment_nodes` 表；验收脚本已容忍该场景，并回退到 `assignment_node.json` 作为节点证据。
- 本轮未触碰 `.running/prod`。

## Risks And Next

- `src/workflow_app/server/services/schedule_service.py` 当前 `1556` 行，已触发行数 advisory；后续应拆分 CRUD、scan/dedupe 和 audit/serialization 子模块。
- 终态 `succeeded/failed` 未在当前等待窗口内稳定出现；若要补齐完整闭环，可追加更长等待或恢复式跟踪脚本。
