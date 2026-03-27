# 生产发布记录 20260326-144438

- topic: 缺陷优先级真相源、重复建单收口与浏览器门禁修复发布生产
- started_at: 2026-03-26T14:42:38+08:00
- finished_at: 2026-03-26T14:43:52+08:00
- source_workspace: `C:\work\J-Agents\workflow`
- released_version: `20260326-144238`
- previous_prod_version: `20260326-113135`
- candidate_source: `test`

## 变更范围
- 显式 `P0/P1/P2/P3` 优先级解析统一为缺陷记录、队列摘要与任务中心节点的真相源。
- 同一缺陷 `process/review` 动作统一收口到任务中心总图，历史重复图标记为 `deleted` 并从列表隐藏。
- 修复浏览器门禁首次建缺陷时的超时问题：历史重复图修复扫描改走轻量路径，隔离运行态改用独立 `runtime/artifacts`。

## 执行动作
- 停止占用部署口的 `test` 运行实例（PID `31560`）。
- 执行 `scripts/deploy_workflow_env.ps1 -Environment test`，生成候选版本 `20260326-144238`。
- 调用 `POST http://127.0.0.1:8090/api/runtime-upgrade/apply`，由正式环境升级机制将 `prod` 从 `20260326-113135` 切换到 `20260326-144238`。

## 验证结果
- `C:\work\J-Agents\workflow\.running\control\reports\test-gate-20260326-144238.json`
  - `result=passed`
- `C:\work\J-Agents\workflow\.running\control\logs\test\deploy-20260326-144238.json`
  - `result=success`
- `http://127.0.0.1:8090/healthz`
  - `ok=true`
- `C:\work\J-Agents\workflow\.running\control\envs\prod.json`
  - `current_version=20260326-144238`
  - `deploy_status=deployed`
- `C:\work\J-Agents\workflow\.running\control\prod-last-action.json`
  - `status=success`
  - `previous_version=20260326-113135`

## 关键产物
- `src/workflow_app/server/services/defect_service.py`
- `src/workflow_app/server/services/defect_service_record_commands.py`
- `src/workflow_app/server/services/defect_service_task_commands.py`
- `src/workflow_app/server/services/assignment_service_parts/task_artifact_store_queries.py`
- `scripts/acceptance/run_acceptance_defect_priority_truth_and_idempotency.py`
- `scripts/acceptance/run_acceptance_defect_center_browser.py`
- `C:\work\J-Agents\workflow\.test\evidence\defect-priority-truth-and-idempotency\summary.json`
- `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\summary.json`
- `C:\work\J-Agents\workflow\.running\control\reports\test-gate-20260326-144238.json`
