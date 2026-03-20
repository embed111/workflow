# SQLite 辅助索引契约

## 1. 文档目的
本文档定义 `任务产物路径` 下可选的 SQLite 辅助索引层契约。它只解决“跨任务/跨会话/跨运行的查询加速与技术索引”问题，不改变现有按任务聚合、按文件落盘的事实源约束。

本文档口径受以下需求约束：
- `docs/workflow/overview/需求概述.md`
- `docs/workflow/requirements/需求详情-任务中心产物交付与路径管理.md`
- `docs/workflow/requirements/需求详情-任务中心真实执行化与执行链路可视化.md`

## 2. 角色定位
1. 文件目录仍是唯一明文事实源。
   - 任务中心事实源：`<任务产物路径>/tasks/<ticket_id>/...`
   - 工作记录事实源：`<任务产物路径>/records/...`
2. SQLite 只能是指定路径里的查询加速层 / 技术索引层。
3. `index.db` 丢失后，系统必须能仅根据指定路径里的文件完整重建。
4. 页面、调度恢复、其他 agent 查阅，都不能依赖 SQLite 才能工作。
5. 文件与 SQLite 不一致时，永远以文件为准，SQLite 只负责回建和加速，不得反向覆盖源文件。

## 3. 最终采用的落点
最终采用路径：`<任务产物路径>/.index/index.db`

当前本地配置示例：`C:/work/J-Agents/.output/.index/index.db`

选择该位置的原因：
1. `.index/` 与 `tasks/`、`records/` 并列，仍处于用户指定路径内部，不会回流到 `workflow/state/`、`workflow/.runtime/state/` 或 `workflow/logs/`。
2. `.index/` 是纯技术层目录，和面向用户浏览的业务目录隔离，不会污染 `tasks/`、`records/` 的目录语义。
3. 删除 `.index/` 可直接触发全量重建，不会误删真实任务文件或工作记录文件。
4. `index.db`、`index.db-wal`、`index.db-shm` 等 SQLite 附属文件都能被稳定约束在一个技术目录内。

## 4. 路径与回跳规则
1. SQLite 中的路径字段统一存储为“相对 `任务产物路径` 的相对路径”，不存绝对路径。
2. 命名统一使用 `*_relpath`。
3. 当源记录来自 JSONL 时，额外记录 `source_line_no`；回跳时使用：
   - 绝对路径 = `<任务产物路径>` + `source_relpath`
   - 锚点 = `source_line_no`
4. 当源记录来自单个 JSON 文件时，使用：
   - 绝对路径 = `<任务产物路径>` + `source_relpath`
   - 锚点 = 主键字段，如 `ticket_id`、`node_id`、`run_id`、`analysis_id`
5. 任何 `*_ref` 或结果引用若不在 `任务产物路径` 下，视为无效引用，不得作为 SQLite 正常索引值写入。

## 5. 明文复制边界
SQLite 中禁止保存以下完整明文副本：
1. 完整 `prompt.txt`
2. 完整 `stdout.txt`
3. 完整 `stderr.txt`
4. 完整 `result.json` / `result.md` 正文
5. 完整对话全文
6. 完整执行事件流明文

SQLite 允许保存的仅限：
1. 主键、状态、时间、枚举字段
2. 稳定查询键
3. 截断后的 `*_preview` 摘要字段
4. `*_relpath` / `source_line_no` 回跳锚点
5. `source_mtime_ns`、`source_size_bytes`、`content_hash` 这类技术校验字段

建议约束：
1. 所有 `*_preview` 字段只保留截断摘要，推荐不超过 `200` 个字符。
2. 若需要全文，一律回到源文件读取。

## 6. 表清单与字段职责

### 6.1 `index_meta`
主键：`meta_key`

常用查询字段：`meta_key`

摘要字段：`meta_value`

回跳字段：无

用途：
1. 保存索引层自身元数据，例如 `artifact_root`、`last_full_rebuild_at`。
2. 不保存任何任务正文、对话正文或执行正文。

### 6.2 `source_file_registry`
主键：`source_relpath`

常用查询字段：`record_kind`, `entity_type`, `entity_id`, `parent_id`, `source_mtime_ns`, `source_size_bytes`, `indexed_at`, `last_seen_at`, `is_deleted`

摘要字段：`content_hash`

回跳字段：`source_relpath`

用途：
1. 记录每个源文件的最后一次索引状态。
2. 支撑增量更新、脏检查、孤儿行清理和全量重建校验。
3. 这是技术表，不作为页面直接展示入口。

### 6.3 `task_index`
主键：`ticket_id`

常用查询字段：`scheduler_state`, `graph_name`, `source_workflow`, `is_test_data`, `created_at`, `updated_at`

摘要字段：`summary_preview`, `node_count`, `running_node_count`, `success_node_count`, `failed_node_count`, `blocked_node_count`

回跳字段：`task_relpath`, `task_structure_relpath`

用途：
1. 索引 `tasks/<ticket_id>/task.json`。
2. 用于任务列表、按状态过滤、按更新时间排序。
3. 这里只保存任务级摘要，不复制完整任务图明文。

### 6.4 `task_node_index`
主键：`ticket_id`, `node_id`

常用查询字段：`ticket_id`, `status`, `assigned_agent_id`, `delivery_mode`, `artifact_delivery_status`, `priority`, `created_at`, `updated_at`, `completed_at`

摘要字段：`node_name`, `assigned_agent_name`, `expected_artifact_preview`, `success_reason_preview`, `failure_reason_preview`, `result_ref_relpath`, `upstream_count`, `downstream_count`, `artifact_count`

回跳字段：`node_relpath`, `artifact_output_dir_relpath`, `artifact_delivery_dir_relpath`

用途：
1. 索引 `tasks/<ticket_id>/nodes/<node_id>.json`。
2. 用于某任务下的节点筛选、失败节点定位、交付状态查询。
3. 不在 SQLite 中重复存储完整 `node_goal` 或完整节点正文。

### 6.5 `assignment_run_index`
主键：`run_id`

常用查询字段：`ticket_id`, `node_id`, `provider`, `status`, `workspace_path`, `started_at`, `finished_at`, `created_at`, `updated_at`

摘要字段：`command_summary`, `latest_event`, `result_summary`, `exit_code`

回跳字段：`run_relpath`, `prompt_relpath`, `stdout_relpath`, `stderr_relpath`, `result_json_relpath`, `result_md_relpath`, `events_relpath`

用途：
1. 索引 `tasks/<ticket_id>/runs/<run_id>/run.json` 以及同目录下的运行证据文件。
2. 用于按节点查最近运行、按状态查活动运行、按时间窗口查失败运行。
3. SQLite 只保留命令摘要和结果摘要，不保存完整 `prompt/stdout/stderr/result` 正文。

### 6.6 `task_run_index`
主键：`task_id`

常用查询字段：`session_id`, `agent_name`, `status`, `created_at`, `updated_at`, `start_at`, `end_at`, `duration_ms`

摘要字段：`summary_preview`

回跳字段：`run_relpath`, `stdout_relpath`, `stderr_relpath`, `trace_relpath`, `events_relpath`, `summary_relpath`

用途：
1. 索引 `records/runs/<task_id>/run.json` 以及对应的 `stdout/stderr/trace/events/summary` 文件。
2. 用于会话运行记录列表、按 agent / 状态回看运行、排查命令执行失败。
3. 这里只保留运行摘要和回跳路径，不复制完整运行正文。

### 6.7 `session_index`
主键：`session_id`

常用查询字段：`status`, `agent_name`, `agents_version`, `is_test_data`, `created_at`, `updated_at`, `last_message_at`, `message_count`, `work_record_count`

摘要字段：`last_message_preview`

回跳字段：`session_relpath`, `messages_relpath`

用途：
1. 索引 `records/sessions/<session_id>/session.json`。
2. 用于会话列表、按最近消息排序、按工作记录数量过滤。
3. 不在 SQLite 中重复存储完整 `role_profile`、`session_goal`、`duty_constraints` 或整段会话内容。

### 6.8 `conversation_message_index`
主键：`session_id`, `message_id`

常用查询字段：`session_id`, `role`, `created_at`, `analysis_state`, `analysis_run_id`, `analysis_updated_at`

摘要字段：`content_preview`, `content_length`

回跳字段：`source_relpath`, `source_line_no`

用途：
1. 索引 `records/sessions/<session_id>/messages.jsonl`。
2. 用于按角色、分析状态、分析批次快速过滤消息。
3. 不保存完整 `content`，只保存短预览和长度；要看全文必须回读 `messages.jsonl`。

### 6.9 `analysis_index`
主键：`analysis_id`

常用查询字段：`session_id`, `status`, `decision`, `workflow_status`, `training_status`, `created_at`, `updated_at`

摘要字段：`decision_reason_preview`, `analysis_summary_preview`, `analysis_recommendation_preview`, `latest_analysis_run_id`, `train_result_summary`

回跳字段：`analysis_relpath`, `workflow_relpath`, `training_relpath`, `workflow_events_relpath`

用途：
1. 聚合索引 `analysis.json`、`workflow.json`、`training.json`。
2. 用于分析任务总览、决策态筛选、训练状态联查。
3. 不把完整 `plan_json`、`selected_plan_json`、完整建议正文复制进 SQLite。

### 6.10 `analysis_run_index`
主键：`analysis_run_id`

常用查询字段：`analysis_id`, `workflow_id`, `session_id`, `status`, `created_at`, `updated_at`

摘要字段：`plan_item_count`, `context_message_count`, `target_message_count`, `no_value_reason`, `error_text_preview`

回跳字段：`analysis_run_relpath`

用途：
1. 索引 `records/analysis/<analysis_id>/runs/<analysis_run_id>.json`。
2. 用于定位某次分析运行、排查失败、统计计划项数量。
3. 不复制完整 `plan_items` 列表，只保留数量和必要摘要。

### 6.11 `audit_index`
主键：`audit_key`

常用查询字段：`audit_type`, `session_id`, `analysis_id`, `ticket_id`, `node_id`, `action`, `status`, `operator`, `created_at`

摘要字段：`reason_preview`, `manual_fallback`, `ref_relpath`

回跳字段：`source_relpath`, `source_line_no`

用途：
1. 统一索引以下审计对象：
   - `records/audit/message-delete.jsonl`
   - `records/audit/policy-confirmation.jsonl`
   - `records/audit/policy-patch-tasks/*.json`
2. 让后续 agent 能按 `session_id`、`ticket_id`、`action` 快速追溯审计链路。
3. `policy_patch_task` 这类单文件 JSON 记录的 `source_line_no` 为空。

### 6.12 `event_index`
主键：`event_key`

常用查询字段：`stream_type`, `ticket_id`, `node_id`, `run_id`, `session_id`, `analysis_id`, `workflow_id`, `event_type`, `level`, `created_at`

摘要字段：`message_preview`, `detail_preview`, `related_status`

回跳字段：`source_relpath`, `source_line_no`, `run_relpath`

用途：
1. 统一索引以下事件流：
   - `tasks/<ticket_id>/runs/<run_id>/events.log`
   - `records/analysis/<analysis_id>/workflow-events.jsonl`
   - `records/system/workflow-events.jsonl`
   - `records/system/reconcile-runs.jsonl`
2. 用于全局事件检索、按任务/会话/分析快速聚合事件。
3. 不把完整事件 `detail` 再复制一份，只保留短摘要和回跳锚点。

## 7. 标准读取顺序
后续其他 agent 查阅时，按以下顺序执行：

1. 先读结构说明文件。
   - 任务中心：`<任务产物路径>/TASKS_STRUCTURE.md`
   - 工作记录：`<任务产物路径>/WORKFLOW_RECORDS_STRUCTURE.md`
2. 如果你已经知道明确的 `ticket_id`、`node_id`、`run_id`、`session_id` 或 `analysis_id`，优先直接读源文件，不先查 SQLite。
3. 只有在以下场景，才优先查 SQLite：
   - 需要跨多个任务或会话做过滤、排序、统计
   - 需要快速定位“最近失败任务 / 最近运行 / 待分析会话 / 某 agent 下所有节点”
   - 需要在大量 `events.log` / `jsonl` 中先缩小范围
4. 查到 SQLite 结果后，必须使用 `*_relpath` 和 `source_line_no` 回跳到源文件，再读取完整内容。
5. 若 `index.db` 不存在、损坏或怀疑过期，直接退回文件扫描，不得因此阻塞页面或 agent 工作。

可执行的简化规则：
1. 看结构：先看 `*.md`
2. 看正文：直接看文件
3. 做筛选：先查 SQLite
4. 查到结果：回跳文件确认

## 8. 一致性与重建规则
### 8.1 初始化
1. 只有在用户指定的 `任务产物路径` 下才允许创建 `.index/index.db`。
2. 首次初始化时先扫描 `tasks/` 和 `records/`，再写入 SQLite。
3. 初始化失败不得影响源文件读取；最多表现为“没有辅助索引”。

### 8.2 增量更新
1. 先成功写入源文件，再更新 SQLite。
2. 每次只更新被触达对象对应的索引行和 `source_file_registry`。
3. JSONL 文件更新时，应按行号重建对应对象索引，而不是把全文缓存进 SQLite。

### 8.3 全量重建
1. 全量重建输入只有 `任务产物路径` 下的文件。
2. 全量重建过程不得依赖 `workflow/state/`、`workflow/.runtime/state/` 或 `workflow/logs/`。
3. 删除 `.index/index.db` 后，系统必须仍可通过重新扫描文件恢复全部索引。
4. 全量重建完成后，应刷新 `index_meta.last_full_rebuild_at` 和 `source_file_registry`。

### 8.4 冲突处理
1. 文件缺失但 SQLite 仍有记录：删除该索引行。
2. 文件变更但 SQLite 未更新：以文件内容重建该索引行。
3. SQLite 中的状态、摘要、路径与源文件不一致：以文件为准。
4. 严禁把 SQLite 中的数据反向写回源文件作为“修复”手段。

## 9. 给页面和其他 agent 的工作准则
1. 页面恢复时可以先查 SQLite 缩小查询范围，但最终详情必须从文件读取。
2. 其他 agent 做工作记录分析时，禁止把 SQLite 结果当成最终证据。
3. 若要引用证据，引用路径应指向源文件，例如：
   - `tasks/<ticket_id>/task.json`
   - `tasks/<ticket_id>/nodes/<node_id>.json`
   - `tasks/<ticket_id>/runs/<run_id>/events.log`
   - `records/sessions/<session_id>/messages.jsonl`
   - `records/analysis/<analysis_id>/workflow-events.jsonl`
4. 如果一个查询只在 SQLite 找到、却无法回跳到源文件，该结果应视为无效。

## 10. 常用查询示例
以下示例仅用于“先缩小范围，再回跳文件”。

### 10.1 查最近更新的任务
```sql
SELECT
  ticket_id,
  graph_name,
  scheduler_state,
  updated_at,
  task_relpath
FROM task_index
ORDER BY updated_at DESC
LIMIT 20;
```

### 10.2 查某任务下的节点与交付状态
```sql
SELECT
  node_id,
  node_name,
  status,
  artifact_delivery_status,
  assigned_agent_id,
  node_relpath
FROM task_node_index
WHERE ticket_id = :ticket_id
ORDER BY priority DESC, updated_at DESC;
```

### 10.3 查某节点最近一次任务中心运行并回跳到运行证据
```sql
SELECT
  run_id,
  status,
  started_at,
  finished_at,
  result_summary,
  prompt_relpath,
  stdout_relpath,
  stderr_relpath,
  result_json_relpath,
  events_relpath
FROM assignment_run_index
WHERE ticket_id = :ticket_id
  AND node_id = :node_id
ORDER BY created_at DESC
LIMIT 1;
```

### 10.4 查需要继续分析的会话
```sql
SELECT
  session_id,
  status,
  last_message_at,
  message_count,
  work_record_count,
  session_relpath,
  messages_relpath
FROM session_index
WHERE work_record_count > 0
ORDER BY last_message_at DESC
LIMIT 50;
```

### 10.5 按会话追事件与审计
```sql
SELECT
  event_type,
  created_at,
  message_preview,
  source_relpath,
  source_line_no
FROM event_index
WHERE session_id = :session_id
ORDER BY created_at DESC
LIMIT 100;
```

```sql
SELECT
  audit_type,
  action,
  operator,
  created_at,
  source_relpath,
  source_line_no,
  ref_relpath
FROM audit_index
WHERE session_id = :session_id
ORDER BY created_at DESC;
```

## 11. 最终结论
1. SQLite 可以加，但只能加在 `任务产物路径` 内。
2. 最终采用路径是：`<任务产物路径>/.index/index.db`
3. 文件目录是唯一明文事实源。
4. `index.db` 只是辅助索引层，丢失可重建，过期可丢弃，不得反向主导页面和 agent 的读取逻辑。
