# [持续迭代] workflow / 2026-04-28 21:45

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260428-e449e661`
- active_version: `V13`
- version_transition_decision: `stay`
- phase: `基于基线测试 -> 验收 -> 发布推进`
- lane: `工程质量探测 / 架构优化 / 测试探测 / 发布推进`
- preference_ref: `state/user-preferences.md`
- memory_ref: `.codex/memory/2026-04/2026-04-28.md#2026-04-28T23:10:00+08:00`

## 判断与取舍
- 不切 V14。V13-R4 fix1 已完成 review/test/workflow gate/test deploy 并刷新 `prod candidate=20260428-224726`，但 prod apply 与 post-apply live recheck 尚未完成；R5-R7 也未启动。
- 不由本轮主线直接 apply prod。当前 `prod current=20260428-174913 / candidate=20260428-224726 / candidate_is_newer=true`，但 `running_task_count=2`，升级门禁返回 `can_upgrade=false`。
- 不新增 helper。testmate 已 GO，当前下一动作依赖 idle watcher 或用户明确升级窗口 apply candidate。

## 推进性修改
- 消费 `workflow_reviewmate` 复审产物：verdict=`approve`。
- 消费 `workflow_testmate node-20260428-v13r4-testmate-mainchain-slice1-fix1-focused-gate / arun-20260428-221132-07e8e9`：verdict=`GO`。
- 修复 `pm/versions/V13/版本计划.md` 的 UTF-8 BOM，解除 PM snapshot alignment gate 红灯。
- 复跑 PM snapshot alignment 与 `TC-PM-003` 单探针，通过；复跑完整 workflow gate，通过。
- 停止旧 test 环境并执行 test deploy，刷新 `prod candidate=20260428-224726`。
- 收尾复核发现 AI 小说 writer 节点留下 `running_node_projected_terminal` ghost；调用受支持 `repair-ghost-running` 后客户端超时，但二次回读已 settle 为 `ghost_running_detected=false / ghost_running_count=0`。

## 关键证据
- review artifact: `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/artifacts/node-20260428-v13r4-reviewmate-mainchain-slice1-fix1-rereview/output/v13-r4-mainchain-slice1-fix1-rereview-reviewmate.md`
- testmate artifact: `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/artifacts/node-20260428-v13r4-testmate-mainchain-slice1-fix1-focused-gate/output/v13-r4-mainchain-slice1-fix1-focused-gate-testmate.md`
- line budget: `.repository/pm-main/.test/20260428-222633-534` PASS
- focused rerun after BOM fix: `.repository/pm-main/.test/20260428-223801-322` PASS；`.repository/pm-main/.test/20260428-223801-339` PASS
- final snapshot verification after documentation writeback: `.repository/pm-main/.test/20260428-230717-359` PASS；`.repository/pm-main/.test/20260428-230718-060` PASS；`.repository/pm-main/.test/20260428-231202-162` PASS
- workflow gate: `.repository/pm-main/.test/20260428-223832-815` PASS；report `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260428-224640.md`
- test deploy: `.running/control/logs/test/deploy-20260428-224726.json`
- `/healthz`: `ok=true`
- `/api/status`: `active_version=V13 / running_task_count=2 / queued_task_count=0 / truth_mismatch_count=0`
- `/api/runtime-upgrade/status`: `current=20260428-174913 / candidate=20260428-224726 / candidate_is_newer=true / request_pending=false / drain_active=false / ghost_running_detected=false / ghost_running_count=0 / running_task_count=2 / can_upgrade=false / blocking_reason=存在运行中任务，暂不可升级`

## V13 逐项状态
| 需求点 | 状态 | 进度 | 最近更新 | ETA | 超时/AAR |
| --- | --- | --- | --- | --- | --- |
| `V13-R1` | `activation_technical_gate_bound` | `100%` | `2026-04-28T22:54:00+08:00` | `2026-04-28` | `未超时 / 无 AAR` |
| `V13-R2` | `review_test_gate_passed_on_r4_fix1_candidate_refreshed` | `100%` | `2026-04-28T22:54:00+08:00` | `2026-04-28` | `未超时 / 无 AAR` |
| `V13-R3` | `post_174913_live_recheck_supporting_r4_candidate_refreshed` | `97%` | `2026-04-28T22:54:00+08:00` | `2026-04-29` | `未超时 / 无 AAR` |
| `V13-R4` | `mainchain_slice1_fix1_candidate_refreshed` | `98%` | `2026-04-28T22:54:00+08:00` | `2026-04-30` | `未超时 / 无 AAR` |
| `V13-R5` | `planned_waiting_r4_candidate_apply` | `0%` | `2026-04-28T22:54:00+08:00` | `2026-05-01` | `未超时 / 无 AAR` |
| `V13-R6` | `planned_waiting_r4_projection_and_aar_scope_review` | `0%` | `2026-04-28T22:54:00+08:00` | `2026-05-02` | `未超时 / V11/V12 AAR 已补，待消费` |
| `V13-R7` | `planned_waiting_r4_candidate_apply` | `0%` | `2026-04-28T22:54:00+08:00` | `2026-05-03` | `未超时 / 无 AAR` |

## 发布边界
- root_sync_state: `candidate_20260428-224726_refreshed_at_a7fb40c__pm-main_dirty_after_final_probe`
- ahead_count: `0`（相对本机 `../workflow_code`；`../workflow_code main...origin/main [ahead 339]` 仅为外部镜像差异）
- dirty_tracked_count: `4`（仅 `.repository/pm-main`：`scripts/README.md`、`scripts/acceptance/workflow_gate_probe_registry.py`、`scripts/acceptance/workflow_gate_probe_registry_v13.py`、`src/workflow_app/server/services/self_iteration_prompt_templates.py`；不在本轮 candidate / workflow_code 中）
- untracked_count: `2`（仅 `.repository/pm-main`：`scripts/acceptance/verify_code_quality_pipeline_contract.py`、`scripts/quality/run_code_quality_pipeline.py`；不在本轮 candidate / workflow_code 中）
- push_block_reason: `当前 candidate 已刷新；prod apply 等待 idle watcher 或用户明确升级窗口；后续代码批次前需先确认、验证、提交或清理 pm-main 的 code-quality pipeline 草稿`
- next_push_batch: `prod candidate 20260428-224726 apply -> post-apply live recheck -> PASS 后继续 R4 下一小批或 R5/R6/R7；FAIL 则冻结 candidate 并回派 workflow_devmate 最小修复`

## helper 判断
- active_helper_tasks: `none_after_testmate_succeeded`
- parallel_candidate_count: `0`
- parallel_dispatched_count: `0`
- parallel_peak_count: `2(workflow + workflow_testmate)`
- helper_dispatch_effect: `review approve 后进入测试门禁链，testmate GO 后触发 gate 与 candidate 刷新`

## 下一动作
- 等待 `prod candidate=20260428-224726` 在空窗由 supervisor idle watcher 或用户明确动作 apply。
- apply 后立即做 post-apply live recheck；PASS 后推进 R4 下一小批或 R5/R6/R7，FAIL 则冻结 candidate 并回派 `workflow_devmate` 最小修复。
- R4 空窗之后，优先启动 `V13-R6` AAR scope review，把扁平化页面清单和 UI focused smoke 固化下来。

## Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: 本轮从 review/test 门禁继续推进到 workflow gate 与 test deploy，`candidate=20260428-224726` 已刷新；版本仍不能切，因为 prod apply 与 post-apply live recheck未完成。
- delta_validation: 下一轮先重检 runtime upgrade 状态；若 `current_version=20260428-224726`，立即执行 post-apply live recheck，否则继续等待安全升级空窗。
