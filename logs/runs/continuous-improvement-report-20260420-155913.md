# Continuous Improvement Report

判断：`version_transition_decision=stay(V5)`。这轮仍处在 `工程质量探测 / 发布边界收口 / 开发实现`，因为 `V5-R5` 的 Mandatory Gate 还没转绿，`V6` 也仍只是 backlog 骨架，不满足切版条件。

取舍：我没有继续重复上一轮的 training center layout css split，也没有在当前 live running 窗口硬插同一条 prod member-route 复验，而是直接处理 clean head 的新第三个 blocker `run_acceptance_workflow_gate.py`。我把 API 请求、session fallback、line-budget gate helper 和 script-probe bridge 从主 runner 抽到 `workflow_gate_acceptance_support.py`，补上 `verify_workflow_gate_acceptance_split.py` 并接进 `workflow_gate_probe_registry.py`。随后我又把 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 的 developer workspace 全部 refresh 到 `b66992c`，拿掉了下一轮并行派发前的 workspace drift。

下一动作：继续优先压 `schedule_service.py / workflow_env_common.ps1 / developer_workspace_service.py`。现在 helper developer workspace 都已经 `clean_synced@b66992c`，下一轮可以把这三块按边界切给 `workflow_devmate` 等角色并行承接。由于 Mandatory Gate 仍 fail-closed，我这轮不部署 `test`，也不刷新 `prod candidate`。

证据：
- 代码批次：`pm-main@b66992c / workflow_code@b66992c`
- 提交信息：`refactor(gate): 拆分 workflow gate 验收 support 以压低门禁 blocker`
- `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=mandatory_gate_fail_closed / next_push_batch=schedule_service.py / workflow_env_common.ps1 / src/workflow_app/server/services/developer_workspace_service.py split + gate/acceptance`
- `.repository/pm-main/.test/20260420-155313-480/report.md`：`HEAD` 红灯，证明旧 `run_acceptance_workflow_gate.py` 仍是 `1012` 行，且 support/import 还不存在
- `.repository/pm-main/.test/20260420-155331-182/report.md`：working tree 绿灯，证明 split probe 已通过，runner 主文件降到 `788` 行
- `.repository/pm-main/.test/20260420-155343-175/report.md`：`verify_workspace_line_budget_mandatory_gate.py` 继续通过，证明 line-budget helper 仍能透过 runner 绑定被旧验收合同调用
- `.repository/pm-main/.test/20260420-155354-140/report.md`：最新 `line budget` 仍 fail-closed，但 `blocking_offender_count=4`
- 当前首批冻结对象：`schedule_service.py / workflow_env_common.ps1 / developer_workspace_service.py`
- helper 维护：`workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 已全部 `clean_synced@b66992c`
- live 现状：`running_task_count=1 / queued_task_count=1 / active_agent_count=1`
- runtime upgrade：`current_version=candidate_version=20260419-180446 / candidate_is_newer=false / can_upgrade=false / blocking_reason=存在运行中任务，暂不可升级`

风险与保留：
- `candidate_version` 仍等于 `prod=20260419-180446`；这批能力尚未进入新的 `test/prod candidate`
- `pm/daily-execution-history/2026-04-20.md` 仍缺失，因为今天的每日学习任务与真实学习报告还没收口
- `controller cadence closure` 和 `prod/live member task project_id/project_ref` 的正向证据仍未补齐，所以 `V5` 不能切到 `V6`

memory_ref: `.codex/memory/2026-04/2026-04-20.md`
