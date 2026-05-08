# Continuous Improvement Report

## 判断

- `version_transition_decision=stay(V5)`。
- 我这轮没有继续重复 `V5-R3` 的本地 contract 说明，而是直接让 `workflow_qualitymate` 在 prod 上做了一条 `P0` live 节点 `node-20260421-022724-f9c0c9`，把 `V5-R2` 的 active/next/backlog 路由真相冻结成可追溯产物。
- 这条 live helper 同时把 `V5-R3` 的 prod 断口钉死了：当前 prod 还是 `20260420-235142`，live 节点和 prompt 都没有 `problem_type / method_card_id / return_contract`，所以这轮不能把 `972311b` 的 score-writeback 逻辑误报成已经在 prod 上闭环。

## 取舍

- 我这轮优先切 `V5-R2`，因为它比再补一轮 `V5-R3` 本地说明更值钱：一条真实 helper run 同时解决了两件事，一是把 `switch go-no-go -> active/V5-R2` 与 `member route expansion -> next/V5-R1` 冻成了 prod/live 证据，二是证明当前 prod baseline 还吃不到 `972311b` 的新合同字段。
- helper run 中途卡成 `running_finalize_stall`，随后又停在 `running_node_projected_terminal`；我没有把 ghost running 原样滚到下一轮，而是两次走 supported `repair-ghost-running`，把 run 与 node 一起收回终态。现在 `/api/runtime-upgrade/status` 已恢复为 `ghost_running_detected=false / running_task_count=1`。

## 下一步

- 先在 `.repository/pm-main@972311b` 上重跑完整 `workflow gate`，并刷新 `test/prod candidate`，把 `V5-R3` 的 contract/writeback 逻辑真正推到可验证 baseline。
- 等新 baseline 可用后，再让真实 helper 重跑一轮带合同字段的 score-writeback proof；在那之前，不再拿旧 prod 反复证明“它还没有这批代码”。

## 证据

- helper live node: `node-20260421-022724-f9c0c9`
- helper live run: `arun-20260421-022750-587666`
- helper artifact: `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/artifacts/node-20260421-022724-f9c0c9/output/v5-r2-demand-routing-live-proof.md`
- root sync: `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=972311b`
- push boundary: `push_block_reason=972311b 这批 V5-R3 改动尚未重跑完整 workflow gate / test candidate refresh；prod 仍停在 20260420-235142 / next_push_batch=待切 972311b 的 workflow gate / test candidate 批`
- live exits:
  - mainline running: `node-sti-20260421-081f2c56`
  - next mainline ready: `node-sti-20260421-f6d1feb1 / planned_trigger_at=2026-04-21T02:26:00+08:00`
  - patrol ready: `node-sti-20260421-901a1a81 / planned_trigger_at=2026-04-21T02:40:00+08:00`
