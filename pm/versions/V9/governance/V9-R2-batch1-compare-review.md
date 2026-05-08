# V9-R2 batch1 compare review

- version: `V9`
- requirement_id: `V9-R2`
- batch_id: `V9-R2-assignment-control-surface-batch1`
- reviewed_at: `2026-04-23T21:43:11+08:00`
- reviewer: `workflow(pm)`
- contract_ref: `pm/versions/V9/governance/V9-R5-质量判断合同-batch1.md`
- sample_requirement: `V9-R2`
- sample_surface_id: `platform.interfaces.list + platform.interfaces.detail self-readback quality surface`

## 1. Compare Review 字段
| field | verdict |
| --- | --- |
| `requirement_id` | `V9-R2` |
| `sample_surface_id` | `platform.interfaces.list + platform.interfaces.detail self-readback quality surface` |
| `frozen_at` | `2026-04-23T21:43:11+08:00` |
| `baseline_triplet` | `active_doc_baseline=prod=20260423-211631 / test_current=20260423-213946 / compare.baseline=20260423-213946` |
| `metadata_contract` | `pass`：`8092` 上 list/detail 都是 `metadata_status=complete` |
| `readability_contract` | `pass`：`/api/platform/interfaces/platform.interfaces.list` 与 `/api/platform/interfaces/platform.interfaces.detail` 都能稳定返回关键字段和 compare 读面 |
| `evidence_contract` | `pass`：`latest_evidence.status=ready`，`api_catalog_live_regression` 已绑定 version-matched artifact |
| `compare_contract` | `pass`：`compare.status=ready`，`baseline_version / compare_target_ref / per_probe_results` 均已对齐 `20260423-213946` |
| `metrics_contract` | `pass_with_debt`：`metrics.status=partial`，但 `reason / source_ref / sampled_at / baseline_version` 均可回读 |
| `version_doc_alignment` | `expected_split`：版本文档继续按 `prod=20260423-211631` 记 active baseline；本次 compare review 明确针对 `test/current=20260423-213946` 的候选验证，不算文档漂移 |
| `risk_route` | `good -> 主=P2 治理债务；次=P3 观察项`：batch1 已可作为 good 样本冻结，继续保留 `metrics.status=partial` 与 `prod` 等空窗升级的后续观察 |

## 2. 证据
- `workspace gate`: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260423-213827.md`
- `fallback regression session`: `.repository/pm-main/.test/20260423-212948-151/report.md`
- `test deploy`: `.running/control/logs/test/deploy-20260423-213946.json`
- `test gate`: `.running/control/reports/test-gate-20260423-213946.json`
- `live regression session`: `.repository/pm-main/.test/20260423-214025-160/report.md`
- `live regression summary`: `.repository/pm-main/.test/20260423-214025-160/artifacts/api-catalog-live-regression/summary.json`
- `live readback`: `http://127.0.0.1:8092/api/platform/interfaces/platform.interfaces.list`
- `live readback`: `http://127.0.0.1:8092/api/platform/interfaces/platform.interfaces.detail`

## 3. 当前结论
- 当前样本 verdict：`good`
- 当前风险层：`主=P2 治理债务；次=P3 观察项`
- 当前默认 owner：`workflow(pm)` 负责冻结版本真相并回写 batch1 good 样本；`workflow_devmate` 继续承接 `V9-R2` 的 batch2 覆盖扩面
- 当前不继续维持 `risky/reject` 的原因：这轮 `latest_evidence.status=ready`、`compare.status=ready`、`baseline triplet` 已一致，且 `report_refs` 同时带上了 version-matched live regression artifact 与 prod readback artifact，已经满足 `V9-R5` batch1 的 `good` 条件

## 4. 下一步
1. 把 batch1 的 `good` verdict 回写进 `V9-R2 / V9-R4 / V9-R5` 的正式版本真相，不再继续沿用 `reject` 旧叙述。
2. 以 `20260423-213946` 这组 compare ready 证据作为 frozen sample，继续推进 `V9-R2` batch2 覆盖扩面。
3. 继续保留 `metrics.status=partial` 和 `prod current=20260423-211631 / candidate=20260423-213946` 等空窗升级的观察，不把它们误报成 batch1 新 blocker。
