# Workflow Latency Baseline Readback 经验

## 适用范围
- `metrics/cli-baseline-latency.json`
- `metrics/workflow-latency-daily.json`
- `workflow latency baseline` 的 live 采样、fixture 验证和 gate 绑定

## 稳定经验
- `runtime_root/metrics/*.json` 才是 workflow latency 的运行态真相；工作区根目录 `metrics/*.json` 更适合作为 PM 读面镜像，不要反过来把工作区旧壳当 live source。
- `workflow latency` 的 gate 不要直接绑真实模型调用；更稳的默认是：gate 走 fixture mode，live baseline 另走标准 `/api/sessions + /api/chat` 入口。
- live 采样脚本如果在 runtime 已经自动 append 样本后又手动把同一批样本再追加一次，会把 `sample_count / p95` 虚高；live mode 只能重算和镜像，不能重复 append。
- 当一批 live sample 全部因为 `real agent is not configured` 或等价基础配置缺口失败时，runtime 与镜像状态都要显式写成 `failed/partial`，不能因为“文件有样本了”就误标 `ready`。
- 如果 prod/test 在同一时间窗口都返回相同的 `real agent` 配置错误，说明 blocker 已从“没有读面”收窄成“legacy chat runtime 未配置真实 agent”；下一步优先判断补 `WORKFLOW_AGENT_*` 还是切换到受支持的 measurement path，而不是继续重复 point sample。
- 当 `workflow latency` 的 live 入口从 legacy `/api/chat` 自动切到 `/api/tasks/execute` 时，脚本必须先保留一条失败 probe 作为 `path_probe`，再把 `requested/effective_measurement_path` 和 `measurement_reason` 一起写进 runtime 与镜像读面；否则后面只看到 `ready`，却还原不出为什么改走了 fallback。
- `/api/tasks/execute` 路径不会像 legacy `/api/chat` 那样自动 append `workflow-latency-daily.json`；如果用它作为 live baseline，测量脚本必须手动追加 `task_execute` sample，否则 `cli-baseline-latency.json` 会变绿、`workflow-latency-daily.json` 却继续停旧。
