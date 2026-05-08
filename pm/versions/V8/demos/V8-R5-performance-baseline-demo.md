# V8-R5 performance baseline demo

- version: `V8`
- requirement_id: `V8-R5`
- demo_at: `2026-04-22T22:36:00+08:00`
- owner: `workflow(pm)`

## 1. Demo 结论
- 我已经把 `workflow latency baseline` 从“只会在 legacy `/api/chat` 上失败”推进成“自动保留失败探针，再切到受支持的 `task_execute` baseline”。
- 当前双环境镜像读面已经都是 `ready`：
  - `test current=candidate=20260422-223441`
  - `prod current=20260422-205203 / candidate=20260422-223441`

## 2. 现场证据
- gate：
  - `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260422-222950.md`
- deploy：
  - `.running/control/logs/test/deploy-20260422-223441.json`
- live baseline：
  - `.repository/pm-main/.test/20260422-223525-646/report.md`
  - `.repository/pm-main/.test/20260422-223110-915/report.md`
  - `metrics/cli-baseline-latency.json`
  - `metrics/workflow-latency-daily.json`

## 3. 关键读面
- `test`
  - `current_version=20260422-223441`
  - `effective_measurement_path=task_execute`
  - `measurement_reason=legacy_chat_real_agent_unconfigured`
- `prod`
  - `current_version=20260422-205203`
  - `candidate_version=20260422-223441`
  - `effective_measurement_path=task_execute`
  - `measurement_reason=legacy_chat_real_agent_unconfigured`

## 4. Demo 准入结论
- `demo_passed`
- `V8-R5` 不再以 legacy `/api/chat` 配置缺口作为 blocker；后续只剩 `prod` 空窗升级和 `V8-R2 / V8-R3` 的版本退出项。
