# 生产发布记录 20260326-171211

- topic: 缺陷优先级真相源与重复任务图收口发布复核
- started_at: 2026-03-26T16:48:17+08:00
- finished_at: 2026-03-26T16:58:13+08:00
- source_workspace: `C:\work\J-Agents\workflow`
- released_version: `20260326-164817`
- previous_prod_version: `20260326-144238`
- candidate_source: `test`

## 变更范围
- 缺陷 `process/review` 建单统一落到 `任务中心全局主图`，节点优先级直接复用缺陷 `task_priority`。
- 历史重复图收口不再依赖 `source_workflow=workflow-ui`，已有 `defect-center` / `defect-center-review` 旧图也纳入识别并标记失效。
- 验收脚本补齐生产同源旧数据场景，新增断言：历史旧图在修复后访问 `/api/assignments/<ticket_id>/graph` 返回 `404`。

## 执行动作
- `test` 候选：`C:\work\J-Agents\workflow\.running\control\logs\test\deploy-20260326-164817.json`
- `prod` 升级：`C:\work\J-Agents\workflow\.running\control\prod-last-action.json`
- 生产复核证据目录：`C:\work\J-Agents\workflow\logs\runs\evidence\prod-defect-priority-idempotency-20260326-165753`

## 生产复核结果
- `/api/defects?status=all&limit=50`
  - `DTS-00003` `task_priority=P0`
  - `DTS-00004` `task_priority=P0`
  - 队列摘要 `active_task_priority=P0`、`next_task_priority=P0`
- `/api/assignments/asg-20260326-122459-a50c6f/graph`
  - `dr-20260325-ca49dd19d9-analyze/fix/release` 均为 `priority_label=P0`
  - `dr-20260325-33d0f8fd52-review` 为 `priority_label=P0`
- `/api/assignments?external_request_id=defect:process:dr-20260325-ca49dd19d9`
  - `items=[]`
- 历史旧图接口
  - `asg-20260325-155330-bc6838` -> `404 assignment_graph_not_found`
  - `asg-20260325-155333-d270ba` -> `404 assignment_graph_not_found`
  - `asg-20260325-155336-3cac33` -> `404 assignment_graph_not_found`
  - `asg-20260325-132002-d119da` -> `404 assignment_graph_not_found`
- 任务中心截图
  - `C:\work\J-Agents\workflow\logs\runs\evidence\prod-defect-priority-idempotency-20260326-165753\10-task-center-global-graph.png`

## 当前收口策略
- 保留图：`asg-20260326-122459-a50c6f` 作为唯一有效总图。
- 缺陷详情引用：`DTS-00004` 的 3 条 `process` 引用分别指向同一总图里的 `analyze/fix/release` 节点；`DTS-00003` 的 `review` 引用指向同一总图里的 `review` 节点。
- 重复图处理：同一 `report_id + action_kind` 的旧图统一标记 `deleted` 并从任务中心列表隐藏；旧图 graph 接口返回 `404`，不再作为有效任务图暴露。

## 关键产物
- `src/workflow_app/server/services/defect_service_task_commands.py`
- `scripts/acceptance/run_acceptance_defect_priority_truth_and_idempotency.py`
- `C:\work\J-Agents\workflow\.running\control\reports\test-gate-20260326-164817.json`
- `C:\work\J-Agents\workflow\.running\control\logs\test\deploy-20260326-164817.json`
- `C:\work\J-Agents\workflow\.running\control\envs\prod.json`
- `C:\work\J-Agents\workflow\.running\control\prod-last-action.json`
- `C:\work\J-Agents\workflow\logs\runs\evidence\prod-defect-priority-idempotency-20260326-165753\01-defect-detail-process.json`
- `C:\work\J-Agents\workflow\logs\runs\evidence\prod-defect-priority-idempotency-20260326-165753\02-defect-detail-review.json`
- `C:\work\J-Agents\workflow\logs\runs\evidence\prod-defect-priority-idempotency-20260326-165753\08-canonical-global-graph.json`
- `C:\work\J-Agents\workflow\logs\runs\evidence\prod-defect-priority-idempotency-20260326-165753\10-task-center-global-graph.png`
