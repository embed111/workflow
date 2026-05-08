# V8-R5 performance baseline 测试设计评审

- version: `V8`
- requirement_id: `V8-R5`
- reviewed_at: `2026-04-22T22:36:00+08:00`
- owner: `workflow(pm)`

## 1. 测试目标
- 证明 `workflow latency baseline` 在 gate、isolated runtime 和 live prod/test 三层都可回读。
- 证明当 legacy `/api/chat` 缺少真实 agent 配置时，脚本会自动切到 `task_execute`，而不是继续把失败样本误报成 ready。

## 2. 用例分层
- fixture/contract：
  - `verify_workflow_latency_baseline.py`
  - 断言 fixture mode 下 prod/test summary 仍可稳定生成，镜像双环境字段齐全。
- isolated gate：
  - `run_acceptance_workflow_gate.py`
  - 通过 `WORKFLOW_GATE_PROBE_*` 环境，额外执行一条 `task_execute` 路径 probe，证明 fallback 在隔离 runtime 里真能跑通。
- live baseline：
  - `measure_workflow_latency_baseline.py --measurement-path auto`
  - `8092`：`current=candidate=20260422-223441`
  - `8090`：`current=20260422-205203 / candidate=20260422-223441`
- 发布验证：
  - `deploy_test_workflow_env.ps1`
  - `deploy-20260422-223441.json`

## 3. 关键断言
- `cli-baseline-latency.json.status=ready`
- `effective_measurement_path=task_execute`
- `measurement_reason=legacy_chat_real_agent_unconfigured`
- `path_probe.reply_preview` 明确保留 legacy `/api/chat` 的配置失败真相
- `workflow-latency-daily.json` 至少有一条 `mode=task_execute/status=success`

## 4. 不覆盖项
- 不把真实 `WORKFLOW_AGENT_*` 注入当成本轮测试前提。
- 不在本轮扩成多轮长时压测或 first-token streaming 指标治理。

## 5. 评审结论
- `pass`
- 当前测试设计足以支撑 `V8-R5` 的完成定义；后续更高阶压测与 streaming 指标进入 `V9` 再扩。
