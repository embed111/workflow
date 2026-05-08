# continuous-improvement 2026-05-05 18:45

- topic: `05:05-05:45` token 未消耗根因复核
- conclusion: 这段不是“执行很慢”，而是 `schedule -> node -> dispatch_requested` 之后没有真正进入 provider start，节点停在 `ready`，所以 token 没消耗。
- evidence:
  - `05:20` watchdog 先报 `ghost_running_detected=true/count=1`
  - `05:37` fast-path 只到 `dispatch_requested`
  - `node-sti-20260505-575b8c10` 没有 `run.json` / `provider_start` / token 迹象
  - `.running/prod/.runtime/state/workflow.db` 为空
- next:
  - 后续优先查 `dispatch_requested -> provider_start` 的断点，不再把 queue 当 run。
