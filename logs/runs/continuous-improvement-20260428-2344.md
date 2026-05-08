# continuous-improvement 2026-04-28 23:44

- preference_ref: `state/user-preferences.md`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260428-55c95fe5`
- active_version: `V13`
- stage: `基于基线测试 -> 验收 -> 发布推进`
- lane: `工程质量探测 / 测试探测 / 发布推进`

## 判断
- 本轮不切版：`version_transition_decision=stay`。
- 最高价值动作是发布边界收口，而不是继续等待 `prod candidate=20260428-224726` apply。
- 原因：`pm-main` 存在 gate/acceptance 脏区，且该批次已经形成可验证的质量流水线扩展；如果不收口，会继续阻塞根仓同步与后续候选刷新。

## 推进性修改
- 提交并同步代码质量流水线扩展：
  - `b4ef538 feat(quality): 扩展坏味道流水线探测并补本地刷新钩子`
  - `6885be5 fix(quality): 修正质量流水线债务统计口径`
- 新增/收口能力：
  - `function_parameter_count`
  - `cyclomatic_complexity`
  - `install_code_quality_post_commit_hook.py`
  - `pm_schedule_signal.failure_count / warning_count` 全量债务统计
- 本机 `pm-main` 与 `../workflow_code/main` 均 clean@`6885be5`。

## 验证
- targeted session：`.repository/pm-main/.test/20260428-235140-053` PASS。
- 修正复测：`.repository/pm-main/.test/20260428-235506-748` PASS。
- workflow gate：`.repository/pm-main/.test/20260428-235739-214` PASS。
- gate report：`.repository/pm-main/.test/runs/workflow-gate-acceptance-20260429-000539.md`。
- test deploy：`.running/control/logs/test/deploy-20260429-000633.json`。
- PM snapshot 验证：`.test/20260429-001905-602` PASS。
- PM snapshot 收尾复核：`.test/20260429-002404-586` PASS。
- live recheck：
  - `/healthz ok`
  - `/api/status active_version=V13 / running_task_count=1 / truth_mismatch_count=0 / next_activation_ready=false`
  - `/api/schedules ok / schedule_count=12 / probe_schedule_count=0`
  - `/api/runtime-upgrade/status current=20260428-174913 / candidate=20260429-000633 / can_upgrade=false / ghost_running_detected=false / blocking_reason=存在运行中任务，暂不可升级`

## 发布边界
- root_sync_state: `clean_synced`
- ahead_count: `0` relative to local `../workflow_code/main`
- dirty_tracked_count: `0`
- untracked_count: `0`
- push_block_reason: `none_for_verified_batch`
- next_push_batch: `prod candidate 20260429-000633 apply -> post-apply live recheck -> R4/R5 next slice`

## 版本逐项状态
| 需求点 | 状态 | 进度 | ETA | 超时 |
| --- | --- | --- | --- | --- |
| `V13-R1` | `activation_technical_gate_bound` | `100%` | `2026-04-28` | `否` |
| `V13-R2` | `review_test_gate_passed_on_r4_fix1_candidate_refreshed` | `100%` | `2026-04-28` | `否` |
| `V13-R3` | `post_174913_live_recheck_supporting_r4_candidate_refreshed` | `97%` | `2026-04-29` | `否` |
| `V13-R4` | `mainchain_slice1_fix1_candidate_refreshed` | `98%` | `2026-04-30` | `否` |
| `V13-R5` | `quality_pipeline_gate_candidate_refreshed` | `12%` | `2026-05-01` | `否` |
| `V13-R6` | `planned_waiting_r4_projection_and_aar_scope_review` | `0%` | `2026-05-02` | `否` |
| `V13-R7` | `planned_waiting_r4_candidate_apply` | `0%` | `2026-05-03` | `否` |

## 下一步
- 等待 `prod candidate=20260429-000633` 空窗 apply。
- apply 后立即做 post-apply live recheck。
- 若 PASS，优先启动 V13-R5 首批质量债务整改；若 FAIL，冻结 candidate 并回派最小修复。

## 收尾一致性检查
- 我已将 `pm/versions/V13/需求台账.md`、`pm/versions/V13/阶段看板.md`、`pm/versions/V13/迭代甘特图.md` 中的前瞻性旧候选描述纠偏到 `candidate=20260429-000633`。
- `candidate=20260428-224726` 仅作为历史 evidence 保留，不能再作为下一步等待 apply 的执行目标。
- PM 快照一致性复核 `.test/20260429-002404-586` PASS，live 读面仍显示最新 candidate 因 `running_task_count=1` 暂不可升级。
