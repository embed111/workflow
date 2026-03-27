# 生产推送记录 20260326-113332

- topic: 缺陷列表筛选栏单行收口推送生产
- started_at: 2026-03-26T11:27:36+08:00
- finished_at: 2026-03-26T11:33:00+08:00
- source_workspace: `C:\work\J-Agents\workflow`
- released_version: `20260326-113135`
- previous_prod_version: `20260325-164619`
- candidate_source: `test`

## 变更范围
- 缺陷列表筛选栏改为桌面端单行布局，状态筛选和搜索框同一行。
- 修复旧运行态 SQLite 在 `defect_reports` 缺失 `task_priority/reported_at/dts_sequence` 列时，建索引提前触发导致启动失败的问题。

## 执行动作
- 首次执行 `scripts/deploy_workflow_env.ps1 -Environment test` 失败，定位到 `test gate` 启动运行态时报 `sqlite3.OperationalError: no such column: task_priority`。
- 调整 `src/workflow_app/server/infra/db/migrations.py` 与 `src/workflow_app/server/services/defect_service.py`，将 `defect_reports` 补列前置到索引创建之前。
- 重新执行 `scripts/deploy_workflow_env.ps1 -Environment test`，通过 `test gate` 并生成新的 `prod candidate`。
- 调用 `POST /api/runtime-upgrade/apply`，由正式环境升级机制将 `prod` 从 `20260325-164619` 切换到 `20260326-113135`。

## 验证结果
- `C:\work\J-Agents\workflow\.running\control\reports\test-gate-20260326-113135.json`
  - `result=passed`
- `C:\work\J-Agents\workflow\.running\control\logs\test\deploy-20260326-113135.json`
  - `result=success`
- `C:\work\J-Agents\workflow\.running\control\prod-candidate.json`
  - `version=20260326-113135`
- `http://127.0.0.1:8090/healthz`
  - `ok=true`
- `C:\work\J-Agents\workflow\.running\control\envs\prod.json`
  - `current_version=20260326-113135`
- `C:\work\J-Agents\workflow\.running\control\prod-last-action.json`
  - `status=success`

## 关键产物
- `src/workflow_app/server/presentation/templates/index.html`
- `src/workflow_app/server/presentation/templates/index_defect_center.css`
- `src/workflow_app/server/infra/db/migrations.py`
- `src/workflow_app/server/services/defect_service.py`
- `C:\work\J-Agents\workflow\.running\control\reports\test-gate-20260326-113135.json`
- `C:\work\J-Agents\workflow\.running\control\envs\prod.json`
