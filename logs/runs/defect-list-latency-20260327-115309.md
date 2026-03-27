# 缺陷列表加载性能修复 20260327-115309

- topic: 缺陷列表与详情读取性能收口
- started_at: 2026-03-27T10:20:00+08:00
- finished_at: 2026-03-27T11:53:09+08:00
- workspace: `C:\work\J-Agents\workflow`
- candidate_version: `20260327-115245`

## 根因
- 缺陷读路径每次都会经过 `_ensure_defect_tables()`，而该函数此前会同步调用 `repair_defect_assignment_state()`。
- `repair_defect_assignment_state()` 在生产运行态冷启动下会做历史缺陷图修复扫描，直测约 `52.4s`；即使热态命中，也仍有约 `9ms` 的检查开销。
- 更严重的是线上旧版本的 HTTP 读链路中，这段检查在同一次 `/api/defects` / `/api/defects/{id}` 请求里会被多次命中，叠加后把 7 条缺陷的列表和详情都拖到了 `1.8s~2.0s`。
- `list_defect_reports()` 还存在“先全量读出、再在 Python 内排序分页”的实现，导致 `limit=20` 与 `limit=100` 的耗时几乎没有差别。

## 修复
- 从缺陷列表/详情读路径移除自动 `repair_defect_assignment_state()` 触发：
  - `src/workflow_app/server/services/defect_service.py`
- 保留显式修复能力，并在幂等/重复图验收脚本中改为显式调用修复：
  - `scripts/acceptance/run_acceptance_defect_priority_truth_and_idempotency.py`
- 优化修复逻辑自身，增加快速签名缓存，并把“按 group 重复全量回扫任务目录”改为“单次扫描后按 group 聚合”：
  - `src/workflow_app/server/services/defect_service_task_commands.py`
- 将缺陷列表改为数据库级排序分页，只统计总数并查询当前页，不再全量读出后再切片：
  - `src/workflow_app/server/services/defect_service.py`
- 将前端缺陷列表默认首屏条数从 `100` 收口到 `20`：
  - `src/workflow_app/web_client/app_status_and_icon_utils.js`

## 前后对比
### 旧版 8090 线上实测
- `GET /api/defects?status=all&limit=100`：约 `2016ms`
- `GET /api/defects?status=all&limit=20`：约 `1822ms`
- `GET /api/defects/dr-20260325-8e8f1de370`：约 `1803ms`

### 新版源码 + 同一份生产运行态数据直测
- 函数直测（`C:\work\J-Agents\workflow\.running\control\runtime\prod`）：
  - `list_defect_reports(...limit=20)`：`11.9ms / 6.2ms / 8.7ms`
  - `get_defect_detail(...)`：`5.9ms / 5.0ms / 7.3ms`
- 临时 `8098` HTTP 实测（同一份生产运行态数据）：
  - `GET /api/defects?status=all&limit=20`：`64.9ms`
  - `GET /api/defects/dr-20260325-8e8f1de370`：`88.6ms`

## 验证
- `python -m py_compile src/workflow_app/server/services/defect_service.py src/workflow_app/server/services/defect_service_task_commands.py scripts/acceptance/run_acceptance_defect_priority_truth_and_idempotency.py src/workflow_app/server/api/defects.py`
- `python scripts/acceptance/run_acceptance_defect_center_browser.py --root .`
- `python scripts/acceptance/run_acceptance_defect_priority_truth_and_idempotency.py --root .`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/deploy_workflow_env.ps1 -Environment test`

## 证据
- 浏览器回归：
  - `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\summary.json`
- 优先级/幂等回归：
  - `C:\work\J-Agents\workflow\.test\evidence\defect-priority-truth-and-idempotency\summary.json`
- 临时 HTTP 探针日志：
  - `C:\work\J-Agents\workflow\.test\runtime\defect-latency-probe.stdout.log`
  - `C:\work\J-Agents\workflow\.test\runtime\defect-latency-probe.stderr.log`
- `test` 候选：
  - `C:\work\J-Agents\workflow\.running\control\logs\test\deploy-20260327-115245.json`
  - `C:\work\J-Agents\workflow\.running\control\reports\test-gate-20260327-115245.json`

## 备注
- 当前 `8090` 线上实例尚未切到本次修复；要在 `8090` 生效，需要后续把候选 `20260327-115245` 升级到 `prod`。
