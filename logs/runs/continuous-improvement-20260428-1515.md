# V13-R4 首个最小 scope/probe 实现批派发

- ticket_id: `asg-20260327-223335-b79f27`
- current_node: `node-sti-20260428-df146322`
- active_version: `V13`
- stage: `开发实现`
- lane: `工程质量探测 / 架构优化 / 当前需求开发`

## 判断
- `version_transition_decision=stay`
- 取舍：上一轮已经完成 R4 scope-freeze；本轮不重复冻结 owner map，而是把交付转成 `workflow_devmate` 的最小 read-only owner/projection scope probe 实现批。
- 下一动作：消费 `node-20260428-v13r4-devmate-scope-probe-batch1`；若代码批绿并同步根仓，接 `workflow_reviewmate -> workflow_testmate -> workflow gate -> test/prod candidate`。

## 推进性修改
- 创建 `workflow_devmate node-20260428-v13r4-devmate-scope-probe-batch1`。
- 显式绑定 `project_id=workflow`，上游依赖 `node-20260428-v13r4-devmate-scope-freeze`。
- 节点目标限制为新增 `verify_v13_r4_role_project_governance_scope.py`、注册 V13 gate、只修红灯暴露的 owner projection；禁止 broad migration、legacy/fallback 删除、project auto-ignite 写链和前端 UI 改动。
- `dispatch-next` 客户端超时后未重发，回读确认 run=`arun-20260428-150943-201110` 已进入 `live_execution / provider_pid=61652`。

## 证据
- `/healthz`: `ok=true`
- `/api/status`: `active_version=V13`
- `/api/schedules`: `[持续迭代] workflow` 当前节点为 `node-sti-20260428-df146322 / running`
- `/api/runtime-upgrade/status`: `current=candidate=20260428-131038 / candidate_is_newer=false / request_pending=false / drain_active=false / ghost_running_detected=false / truth_owner=assignment_schedule_runtime_truth`
- `status-detail`: `node-20260428-v13r4-devmate-scope-probe-batch1 / status=running / run_status=running / execution_truth=live_execution`

## V13 逐项状态
| 需求点 | 状态 | 进度 | 最近更新 | ETA | 超时 |
| --- | --- | --- | --- | --- | --- |
| `V13-R1` | `activation_technical_gate_bound` | `100%` | `2026-04-28T15:15:00+08:00` | `2026-04-28` | `未超时 / 无 AAR` |
| `V13-R2` | `review_gate_enforced_on_r3_slice1` | `100%` | `2026-04-28T15:15:00+08:00` | `2026-04-28` | `未超时 / 无 AAR` |
| `V13-R3` | `post_candidate_131038_live_recheck_passed` | `90%` | `2026-04-28T15:15:00+08:00` | `2026-04-29` | `未超时 / 无 AAR` |
| `V13-R4` | `scope_probe_batch1_running` | `45%` | `2026-04-28T15:15:00+08:00` | `2026-04-30` | `未超时 / 无 AAR` |
| `V13-R5` | `planned` | `0%` | `2026-04-28T15:15:00+08:00` | `2026-05-01` | `未超时 / 无 AAR` |
| `V13-R6` | `planned` | `0%` | `2026-04-28T15:15:00+08:00` | `2026-05-02` | `未超时 / 无 AAR` |
| `V13-R7` | `planned` | `0%` | `2026-04-28T15:15:00+08:00` | `2026-05-03` | `未超时 / 无 AAR` |

## 发布边界
- root_sync_state: `clean_synced_for_code_workspaces`
- ahead_count: `0`（pm-main 相对本机 `../workflow_code`）
- dirty_tracked_count: `32`（PM 根仓既有脏文件）
- untracked_count: `502`
- push_block_reason: `当前没有已验证未推代码；R4 batch1 正在由 workflow_devmate 形成可验证代码切片`
- next_push_batch: `消费 workflow_devmate R4 batch1；若形成可验证代码切片，按 reviewmate -> testmate -> gate -> test/prod candidate 推进`

## 留痕
- history: `pm/versions/V13/history/2026-04/2026-04-28.md#15:15`
- memory_ref: `.codex/memory/2026-04/2026-04-28.md#2026-04-28T15:15:00+08:00`
- 当前不创建 `pm/daily-execution-history/2026-04-28.md`：D2 仍要求 helper 自己的真实学习报告，PM 不代写空壳日报。
