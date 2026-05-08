# V8-R5 关键路径性能与 workflow latency 方案评审

- version: `V8`
- requirement_id: `V8-R5`
- reviewed_at: `2026-04-22T22:36:00+08:00`
- owner: `workflow(pm)`
- collaborators: `workflow_devmate / workflow_testmate / workflow_qualitymate`

## 1. 背景
- `workflow latency baseline` 的 gate、fixture 和双环境镜像读面已经在 `3277e44` 成立，但 prod/test 的 live `/api/chat` 都稳定返回 `real agent is not configured`。
- 当前现场没有受支持的密钥注入链路，继续把 `WORKFLOW_AGENT_*` 当作本轮前提，只会让 `V8-R5` 卡在重复 point sample。

## 2. 方案判断
- gate 继续保持 `fixture -> verify_workflow_latency_baseline.py`，不把真实模型调用硬塞进 `workflow gate`。
- live baseline 改成 `auto` 双段决策：
  - 先对 legacy `/api/chat` 做一条探针，保留真实失败证据；
  - 若失败原因为 `real agent is not configured`，自动切到受支持的 `/api/tasks/execute` 路径收 `task_execute` baseline。
- `task_execute` 路径不会像 `/api/chat` 那样自动写 `workflow-latency-daily.json`，因此测量脚本必须手动 append sample，并把 `requested/effective_measurement_path` 与 `measurement_reason` 一起写回 runtime 与镜像读面。

## 3. 备选方案取舍
- 否决：直接在 prod/test 补 `WORKFLOW_AGENT_*`
  - 当前没有稳定的受支持密钥注入链路；强行补配置会把这轮从工程质量探测拖进高风险配置变更。
- 否决：把全失败 `/api/chat` 样本继续记成 ready
  - 这会破坏 fail-closed 语义，也会让 `V8-R5` 的完成定义变成假绿灯。

## 4. 风险与护栏
- 风险：`task_execute` baseline 比 legacy `/api/chat` 更长，且没有 first-token 指标。
- 护栏：
  - `mode` 显式写成 `task_execute`，不伪装成 `non_stream`。
  - `first_token_ms` 继续留空，只把 `total_ms / task_duration_ms` 当作当前稳定真相。
  - 保留 `path_probe`，让读面继续看见 legacy `/api/chat` 的真实失败原因。

## 5. 验证口径
- `python scripts/quality/check_workspace_line_budget.py --root .`
- `python scripts/acceptance/verify_workflow_latency_baseline.py`
- `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
- `python scripts/acceptance/measure_workflow_latency_baseline.py --measurement-path auto` on `8090/8092`

## 6. 评审结论
- `go`
- 这条方案允许我在不补 secrets 的前提下，把 `V8-R5` 从“卡在 legacy `/api/chat` 配置缺口”推进成“live baseline ready + fail-closed reason 可回读”。
