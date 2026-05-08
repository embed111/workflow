# 持续迭代报告

## 判断
- `version_transition_decision=stay(V5)`。`V6` 仍只有 backlog 骨架，`next_activation_ready=false`；当前切版 blocker 仍是 `controller cadence closure` 缺 live finalize 消费证据、`prod/live member task` 缺正向 `project_id/project_ref` 证据，以及 `Mandatory Gate=false`。
- 这轮我没有重复上一轮的 `index.html` partial split，而是直接处理新 surfaced blocker `graph_model_and_payloads.py`。这刀比回去重复 live 负向 proof 更值，因为它让 clean head 的 Mandatory Gate 从 `22` 降到 `21`，并把第三个首批冻结对象切换成 `index_training_center_role_creation.css`。
- 下一动作：继续切 `schedule_service.py / workflow_env_common.ps1 / index_training_center_role_creation.css`。只有 `line budget / workflow gate / runtime release gate` 进入下一阶段后，我才去部署 `test`、刷新 `prod candidate`，再重跑 supported live member-route 正向证据。

## 本轮推进
- 我新增 `assignment_execution_contract_runtime.py`，把 `graph_model_and_payloads.py` 里不属于“图模型”的执行提示词构建、结构化结果归一化、Codex 命令解析和 run process registry 全部抽成独立 runtime part。
- 我新增 `verify_assignment_graph_execution_contract_split.py` 并挂进 `workflow_gate_probe_registry.py`，把 `graph_model_and_payloads.py < 1000 行 + support 已进 manifest + moved function 全迁移` 锁成 dedicated split contract。
- 我把这批代码提交成 `pm-main@178f413 refactor(assignment): 拆分执行契约运行时以压低图模型 blocker`，随后用受支持的 `../workflow_code fetch + ff-only merge` 把本机代码根仓同步到同一提交，并让 `pm-main fetch origin` 追平 tracking。

## 验证
- `.repository/pm-main/.test/20260420-084054-730/report.md`：`verify_assignment_graph_execution_contract_split.py`
- `.repository/pm-main/.test/20260420-084105-075/report.md`：`verify_assignment_graph_node_surface_split.py`
- `.repository/pm-main/.test/20260420-084114-481/report.md`：`verify_assignment_self_iteration_plan_reference.py`
- `.repository/pm-main/.test/20260420-084123-563/report.md`：`verify_assignment_runtime_metrics_node_fallback.py`
- `.repository/pm-main/.test/20260420-084131-560/report.md`：`python -m py_compile ...`
- `.repository/pm-main/.test/20260420-084141-037/report.md`：`python scripts/quality/check_workspace_line_budget.py --root .`，预期 `fail-closed`
- 关键结果：`graph_model_and_payloads.py 1223 -> 782`，新 support part `assignment_execution_contract_runtime.py=454`；最新 `line budget` 为 `blocking_offender_count=21 / refactor_trigger=19 / guideline=2`

## 版本与边界
- 当前 lane 继续是 `工程质量探测 / 发布边界收口`，lifecycle_stage=`开发实现`，baseline 仍是 `prod=20260419-180446`。
- 当前 active 需求评估：`V5-R1=60% / 最近更新=2026-04-19T23:50:42+08:00 / eta=2026-04-21 / 未超时`；`V5-R2=35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`；`V5-R3=35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`；`V5-R4=96% / 最近更新=2026-04-19T23:50:42+08:00 / eta=2026-04-21 / 未超时`；`V5-R5=99% / 最近更新=2026-04-20T08:43:43+08:00 / eta=2026-04-21 / 未超时`。本轮没有新增 AAR。
- 当前发布边界真相：`root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=178f413 / push_block_reason=mandatory_gate_fail_closed / next_push_batch=schedule_service.py / workflow_env_common.ps1 / src/workflow_app/server/presentation/templates/index_training_center_role_creation.css split + gate/acceptance`
- 最新 first batch targets 已变成 `schedule_service.py / workflow_env_common.ps1 / index_training_center_role_creation.css`；`graph_model_and_payloads.py` 已退出首批冻结对象。
- live 仍不是升级空窗：`/api/status` 与 `/api/runtime-upgrade/status` 最新显示 `running_task_count=1`、`candidate_version=current_version=20260419-180446`、`candidate_is_newer=false`、`can_upgrade=false`、`ghost_running_detected=false`。
- helper 这轮继续不强派：`workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 的 developer workspace 还停在 `cec137`，落后 `code_root@178f413`；我先保证 pm-main verified batch 收口回根仓，下一轮若切 helper 先 refresh 目标工作区。

## 留痕
- warning: `candidate_version` 仍等于 `prod=20260419-180446`，这批能力尚未进入新的 `test / prod candidate`
- warning: `Mandatory Gate` 仍 fail-closed，下一批 blocker 是 `schedule_service.py / workflow_env_common.ps1 / index_training_center_role_creation.css`
- warning: `pm/daily-execution-history/2026-04-20.md` 仍缺失；今天的学习任务与真实学习报告尚未收口，我这轮不伪造 completed 记录
- preference_ref: `state/user-preferences.md`
- delta_observation: 这轮继续沿 Mandatory Gate 首批冻结对象推进时，`graph_model_and_payloads.py` 里最值钱的切片不是再拆 surface/payload，而是把 execution prompt/result/process helper 从“图模型”文件名里抽干净；dedicated split probe 再配 `self_iteration_plan_reference` 与 `runtime_metrics_node_fallback`，能更稳地兜住回归。
- delta_validation: 下一轮若继续处理 Mandatory Gate 大文件，优先先看当前超线文件里是否还混着“文件名语义之外的执行/交互/进程职责”；命中时继续按 `dedicated split probe + manifest + 关联 regression probe` 的组合先做 clean-slice 收口。
- memory_ref: `.codex/memory/2026-04/2026-04-20.md`
