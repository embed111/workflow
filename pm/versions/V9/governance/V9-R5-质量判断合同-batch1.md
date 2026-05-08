# V9-R5 质量判断合同 batch1

- version: `V9`
- requirement_id: `V9-R5`
- batch_id: `V9-R5-quality-judgment-batch1`
- frozen_at: `2026-04-23T13:22:31+08:00`
- source_artifact: `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/artifacts/node-20260423-074942-a95478/output/v9-r5-quality-contract-batch1.md`
- updated_at: `2026-04-24T09:34:41+08:00`

## 1. 样本面
| field | value |
| --- | --- |
| sample_requirement | `V9-R2` |
| sample_surface_id | `platform.interfaces.list + platform.interfaces.detail self-readback quality surface` |
| current_sample_verdict | `good` |
| current_risk_layer | `主=P2 治理债务；次=P3 观察项` |
| formal_defect_threshold_now | `未达到` |
| default_owner_now | `workflow(pm)` 回写版本真相，`workflow_devmate` 承接后续目录扩面 |
| regression_requirement_now | 若后续改动 read-model 或 interface-center UI，必须先重读 `8090` 的 list/detail，再复核 `verify_api_catalog_contract.py` 与 `verify_api_catalog_live_regression.py` 的最新 artifact |

## 2. 判断档位
| band | minimum rule | risk_route |
| --- | --- | --- |
| `good` | `metadata_status=complete`、`latest_evidence.status=ready`、`compare.status=ready`、baseline triplet 一致；`report_refs` 至少同时包含 live regression artifact 和 prod readback artifact；`metrics.status` 若为 `partial`，必须同时给出 `reason + source_ref + sampled_at` | 记为受控治理债务或观察项，不新开缺陷 |
| `risky` | 虽已 `complete`，但 `latest_evidence.status` 或 `compare.status` 仍只是 `bound/partial`，或 baseline/document/live 之间不一致，或 `report_refs` 只剩脚本名、没有真实 artifact，或 `metrics.status` 缺 `reason/source_ref` | 冻结成 `P1` active blocker 或 `P2` 治理债务，禁止只写“继续观察” |
| `reject` | `metadata_status!=complete`，或 list/detail 返回 `404/5xx`，或 `compare.status=blocked`，或 `missing_probe_keys / stale_probe_keys` 非空，或 contract 字段不可读 | 走正式缺陷路由：`workflow_qualitymate -> workflow_bugmate -> workflow_testmate` |

## 3. Compare Review 必填字段
- `requirement_id`
- `sample_surface_id`
- `frozen_at`
- `baseline_triplet`
- `metadata_contract`
- `readability_contract`
- `evidence_contract`
- `compare_contract`
- `metrics_contract`
- `version_doc_alignment`
- `risk_route`

## 4. 当前批次排除项
- 不把 `V9-R1 / V9-R3 / V9-R4` 直接纳入同一批判断面。
- 不把 `metrics.status=ready` 或 `24h` 聚合作为 batch1 必达条件。
- 不把 `workflow_bugmate / workflow_ucdmate` 的完整专业合同前置强行塞进本批。

## 5. 样本后果回写格式
- `sample_id`
- `sample_requirement`
- `sample_surface_id`
- `initial_judgment`
- `initial_route`
- `actual_outcome`
- `consequence_writeback`
- `next_surface_decision`
- `evidence_refs`

## 6. 当前完成面
1. `V9-R2` batch1 的 `good` compare review 已冻结在 `pm/versions/V9/governance/V9-R2-batch1-compare-review.md`。
2. `scheduler-control-trio` 的首条闭环样本后果回写已正式落到 `pm/versions/V9/governance/V9-R5-scheduler-control-trio-样本后果回写.md`。
3. `V9` 内不再继续扩第二条同义质量判断 surface；下一条专业判断 surface 正式移交给 `V10-R2` 的 `project_task_summary + project_ops_live_regression residual quality surface`。
