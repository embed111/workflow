# Continuous Improvement Report

## 判断
- `version_transition_decision=stay(V8)`。
- 本轮真实推进项是 `工程质量探测 + 发布推进 + 工作区小伙伴维护`，不是重复上一轮的 assignment/dashboard latency baseline。
- 我已经把 `V8-R5` 的 workflow latency 基线读面补成正式代码与 gate 资产；当前不切版，因为 `V8-R2 / V8-R3 / V8-R5` 仍未退出，且 `V9.next_activation_ready=false`。

## 取舍
- 我没有继续重复 point sample，而是新增 `measure_workflow_latency_baseline.py / verify_workflow_latency_baseline.py`，让 `runtime_root/metrics` 的 live 样本和工作区 `metrics/` 的读面镜像能同时成立。
- 我把 gate 保持在 fixture 模式，把 live baseline 留给标准 `/api/sessions + /api/chat` 入口，不把真实模型依赖直接绑进 `workflow gate`。
- live 结果已经把 blocker 收窄：`prod=20260422-195204` 与 `test=20260422-205203` 的 legacy `/api/chat` sample 都返回 `real agent is not configured`，所以现在缺的不是“读面”，而是 `WORKFLOW_AGENT_*` 配置或替代测量入口。

## 下一动作
- 先判断 `V8-R5` 的 legacy `/api/chat` real-agent 缺口是补 `WORKFLOW_AGENT_BASE_URL / WORKFLOW_AGENT_API_KEY / WORKFLOW_AGENT_MODEL`，还是改走受支持的 task/assignment measurement path。
- 再补 `V8-R2` 的 project summary live regression，并判断 `V8-R3` 是否继续推进 `project-ops canonical header / workboard trim`。
- 当前 `prod` 仍是 `current=20260422-195204 / candidate=20260422-205203 / drain_active=true / running_task_count=1`，等待空窗升级；`test` 已是 `current=candidate=20260422-205203`。

## 证据
- `code_batch`: `pm-main/workflow_code=3277e44`
- `workflow_latency_probe`: `.repository/pm-main/scripts/acceptance/measure_workflow_latency_baseline.py`
- `workflow_latency_gate`: `.repository/pm-main/scripts/acceptance/verify_workflow_latency_baseline.py`
- `gate_report`: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260422-204953.md`
- `test_deploy`: `.running/control/logs/test/deploy-20260422-205203.json`
- `live_metrics_readback`: `metrics/cli-baseline-latency.json`、`metrics/workflow-latency-daily.json`
- `release_boundary`: `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=- / next_push_batch=先处理 V8-R5 real-agent 配置或替代 measurement path，再补 V8-R2 regression`
- `memory_ref`: `.codex/memory/2026-04/2026-04-22.md`
