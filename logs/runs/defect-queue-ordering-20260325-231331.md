# 缺陷排序与按顺序建单闭环 - 2026-03-25 23:13:31

## 背景
- 用户要求按 `docs/workflow/prompts/执行提示词-需求与缺陷模块排序与顺序建单开工-20260325.md` 完成增量实现。
- 本轮只收口两件事：缺陷默认排序改为 `P0 -> P1 -> P2 -> P3` 且同优先级按 `reported_at` 升序；缺陷页新增“按顺序创建任务”总开关，并把自动建单、主动处理位、任务中心优先级继承做成真实闭环。

## 代码改动
- `src/workflow_app/server/services/defect_service.py`
  - 为缺陷记录补齐 `task_priority`、`reported_at`、顺序建单设置表、队列状态计算、自动顺序建单推进和手动建单门禁。
  - `list_defect_reports` 改为先筛选再按优先级/上报时间稳定排序，并返回全局 `queue` 摘要。
- `src/workflow_app/server/services/defect_service_record_commands.py`
  - 缺陷创建与状态写回链路正式落盘 `task_priority`、`reported_at`，并给历史缺失值保留回填口径。
- `src/workflow_app/server/services/defect_service_task_commands.py`
  - 处理/复核建单统一继承缺陷优先级，顺序建单开启时对人工建单加门禁，并记录 `auto_queue` 历史。
- `src/workflow_app/server/api/defects.py`
  - 所有缺陷 GET/POST 入口在读写后自动触发顺序建单推进，新增 `/api/defects/queue-mode`。
- `src/workflow_app/server/infra/db/migrations.py`
  - 补充 `defect_reports.task_priority`、`defect_reports.reported_at`、`defect_queue_settings` 及队列排序索引。
- `src/workflow_app/web_client/defect_center_state_helpers.js`
  - 补齐队列摘要归一化、列表项的 `task_priority`/`reported_at`/`queue_mode` 字段。
- `src/workflow_app/web_client/defect_center_render_runtime.js`
  - 缺陷列表和详情显式展示任务优先级、上报时间、当前排队状态；新增页头总开关、当前主动处理缺陷、下一条待建单缺陷摘要。
- `src/workflow_app/web_client/defect_center_events.js`
  - 浏览器探针增加 `queue_off`/`queue_on`/`queue_active`/`queue_advanced` 场景，校验新队列行为。
- `src/workflow_app/server/presentation/templates/index.html`
  - 缺陷页头增加“按顺序创建任务”条带、主动处理位摘要和总开关按钮。
- `src/workflow_app/server/presentation/templates/index_defect_center.css`
  - 新增队列摘要条、优先级徽标、排队徽标、详情徽标行和响应式样式。
- `src/workflow_app/server/services/assignment_service_parts/task_artifact_store_core.py`
  - 修复任务中心节点优先级落盘时把 `0` 误当成 false 回退为 `1` 的问题，确保 `P0` 真正继承到任务中心。
- `scripts/acceptance/run_acceptance_defect_center_browser.py`
  - 重写浏览器验收脚本，新增排序、总开关、自动推进、人工门禁、任务中心优先级继承和 `dispute` 复核建单场景。

## 验证
- 前端 bundle 与 Python 语法检查通过：`.test/20260325-230935-041/report.md`
- 顺序建单浏览器验收通过：`.test/20260325-231159-661/report.md`
- 浏览器验收总结：`.test/20260325-231159-661/artifacts/defect-center-browser/summary.json`
- 截图证据：
  - `.test/20260325-231159-661/artifacts/defect-center-browser/screenshots/queue-off.png`
  - `.test/20260325-231159-661/artifacts/defect-center-browser/screenshots/queue-on.png`
  - `.test/20260325-231159-661/artifacts/defect-center-browser/screenshots/queue-active.png`
  - `.test/20260325-231159-661/artifacts/defect-center-browser/screenshots/queue-advanced.png`
- 接口与行为证据：
  - 列表返回 `task_priority / reported_at` 且默认排序正确：`.test/20260325-231159-661/artifacts/defect-center-browser/api/list-off-all.json`
  - 搜索后仍保持默认排序：`.test/20260325-231159-661/artifacts/defect-center-browser/api/list-search-stable.json`
  - 状态筛选后仍保持默认排序：`.test/20260325-231159-661/artifacts/defect-center-browser/api/list-status-stable.json`
  - 总开关关闭时不自动建单：`.test/20260325-231159-661/artifacts/defect-center-browser/api/list-off-all.json`
  - 总开关开启且主动处理位空闲时自动建单：`.test/20260325-231159-661/artifacts/defect-center-browser/api/queue-mode-on.json`
  - 当前主动处理缺陷未解决时人工建单被门禁阻断：`.test/20260325-231159-661/artifacts/defect-center-browser/api/manual-process-blocked.json`
  - 上一条进入已解决后下一条自动建单：`.test/20260325-231159-661/artifacts/defect-center-browser/api/resolve-head.json` 与 `.test/20260325-231159-661/artifacts/defect-center-browser/api/second-detail-active.json`
  - 自动创建任务与任务中心引用一致：`.test/20260325-231159-661/artifacts/defect-center-browser/api/head-detail-active.json`、`.test/20260325-231159-661/artifacts/defect-center-browser/api/head-assignment-graph.json`
  - 自动创建任务继承缺陷优先级：`.test/20260325-231159-661/artifacts/defect-center-browser/api/head-assignment-graph.json`、`.test/20260325-231159-661/artifacts/defect-center-browser/api/second-assignment-graph.json`、`.test/20260325-231159-661/artifacts/defect-center-browser/api/dispute-assignment-graph.json`
  - `dispute` 记录进入顺序建单并自动创建复核任务：`.test/20260325-231159-661/artifacts/defect-center-browser/api/dispute-detail-active.json`

## 风险与边界
- 历史数据回填策略：
  - `reported_at` 缺失时回填为 `created_at`
  - `task_priority` 缺失时按历史文本/结论关键词推断，无法判定时落到默认口径
- 防重边界：
  - 自动/人工建单共用按 `report_id + action_kind` 固定生成的 `external_request_id`
  - `defect_task_refs` 通过 `(report_id, ticket_id, focus_node_id, external_request_id)` 去重
  - 任务中心图创建也复用 `external_request_id` 做幂等
  - 若后续新增绕过这些服务层的建单入口，或手工改库破坏 `external_request_id` 约束，仍可能出现重复建单
- 本轮未发布 `test`/`prod`，只完成开发态实现与本地验收留痕。

## Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: 用户对缺陷模块要求“真实闭环优先于前端展示”，并要求证据必须覆盖排序、门禁、自动推进、任务中心一致性。
- delta_validation: 后续若用户继续推进，优先在 `test` 环境复核四张截图和 `list-off-all / queue-mode-on / second-detail-active / dispute-assignment-graph` 这几组核心证据，再决定是否发布。
