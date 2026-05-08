# continuous-improvement-report-20260423-134616

- preference_ref: `state/user-preferences.md`
- delta_observation: 这轮我没有继续停在 `workflow_devmate` 的已验证 batch1 根仓收口，而是把 `pm-main@28cbbe5` 刷到了 `test/current=candidate=20260423-133937`，随后按 `V9-R5` batch1 合同正式回收 `V9-R2` compare review；真实结果是 `compare.status=blocked`，阻断点已收窄成 `api_catalog_live_regression` 在 `host-root` 截图 90 秒超时。
- delta_validation: 下一轮先修 `verify_api_catalog_live_regression.py` 的 `host-root` harness 断点，再重跑 `20260423-133937` 的 compare review；若 compare 回到 `ready`，再重判 `V9-R2` 的风险档位并决定是否继续派 helper。

## 判断
- `version_transition_decision=stay(V9)`。
- 当前轮次归类：`发布推进 + 测试探测`；当前最高价值泳道：`测试探测`；生命周期阶段：`基于基线测试`。
- `prod current=20260423-054953 / candidate=20260423-133937 / candidate_is_newer=true / running_task_count=1 / request_pending=false / ghost_running_detected=false`；主线仍健康接力，不需要补链。

## 已完成动作
- 用受支持脚本停止旧 `test`，再部署 `pm-main@28cbbe5` 到 `test/current=candidate=20260423-133937`。
- 部署后自动修掉 `test` 的历史 ghost running，`ghost_running_count` 从 `1 -> 0`。
- 用 `test-session-manager` 跑 `verify_api_catalog_live_regression.py --base-url http://127.0.0.1:8092 --expected-version 20260423-133937`，拿到 `.repository/pm-main/.test/20260423-134040-223/` 会话。
- 直接回读 `8092` 的 `platform.interfaces.list/detail`，按 `V9-R5` batch1 合同冻结 compare review，并新增 [`pm/versions/V9/governance/V9-R2-batch1-compare-review.md`](D:\code\AI\J-Agents\workflow\pm\versions\V9\governance\V9-R2-batch1-compare-review.md)。

## 结论
- `V9-R2` 当前不能判 `good`。虽然 `metadata_status=complete`、`metrics.status=partial` 且 `baseline=20260423-133937` 已追平，但 `latest_evidence.status=partial`、`compare.status=blocked`、`stale_probe_keys=api_catalog_live_regression`，按合同只能记 `reject`。
- `V9-R4` 的剩余风险也更具体了：不再是泛化的 gate 尾噪音，而是 `verify_api_catalog_live_regression.py` 对 `8092 /` 的 `host-root` 截图超时。
- 当前发布边界保持 `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=-`；代码没有新的待推批次，下一批优先是 harness 修复而不是再刷一次同义部署。

## 关键证据
- `.running/control/logs/test/deploy-20260423-133937.json`
- `.running/control/reports/test-gate-20260423-133937.json`
- `.repository/pm-main/.test/20260423-134040-223/report.md`
- `.repository/pm-main/.test/20260423-134040-223/artifacts/api-catalog-live-regression/summary.json`
- `http://127.0.0.1:8092/api/platform/interfaces/platform.interfaces.list`
- `http://127.0.0.1:8092/api/platform/interfaces/platform.interfaces.detail`
- `memory_ref: .codex/memory/2026-04/2026-04-23.md`

## 下一步
1. 修掉 `verify_api_catalog_live_regression.py` 的 `host-root` 截图超时。
2. 重跑 `20260423-133937` 的 live regression，让 `api_catalog_live_regression` 真正落到新 baseline。
3. 再按 `V9-R5` batch1 合同重判 `V9-R2` compare review，并决定是解除 blocker、维持 `risky`，还是继续 `reject` 路由。
