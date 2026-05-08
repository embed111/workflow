# Continuous Improvement Report

判断：`version_transition_decision=stay(V5)`。这轮仍处在 `工程质量探测 / 发布边界收口 / 开发实现`，因为 `V5-R5` 的 Mandatory Gate 还没转绿，`V6` 也仍只是 backlog 骨架，不满足切版条件。

取舍：我没有回去重复上一轮的 schedule center browser acceptance split，也没有在当前 live running 窗口硬插同一条 prod member-route 复验，而是直接处理 clean head 的新第三个 blocker `index_training_center_layout.css`。我把 training center agent skill card / detail summary 这簇样式从 `index_training_center_layout.css` 抽到 `index_training_center_cards.css`，补上 `verify_training_center_layout_css_split.py` 并接进 `workflow_gate_probe_registry.py`。这刀把主 layout 从 `1047` 行压到 `958` 行，`blocking_offender_count` 从 `6` 降到 `5`，新的首批冻结对象切成了 `schedule_service.py / workflow_env_common.ps1 / scripts/acceptance/run_acceptance_workflow_gate.py`。

下一动作：继续优先压 `schedule_service.py / workflow_env_common.ps1 / scripts/acceptance/run_acceptance_workflow_gate.py`，先把 clean head 的 Mandatory Gate 再往下收；在 `line budget / workflow gate / runtime release gate` 过线前，我不刷新 `test/prod candidate`，也不重复跑同一条 prod member-route 正向证据。

证据：
- `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=mandatory_gate_fail_closed / next_push_batch=schedule_service.py / workflow_env_common.ps1 / scripts/acceptance/run_acceptance_workflow_gate.py split + gate/acceptance`
- `pm-main/workflow_code=71ab7da refactor(training): 抽离训练中心技能卡样式以压低门禁 blocker`
- live 现状：`running_task_count=1 / queued_task_count=2 / active_agent_count=1 / next_activation_ready=false`
- runtime upgrade：`current_version=candidate_version=20260419-180446 / candidate_is_newer=false / can_upgrade=false / blocking_reason=running_tasks_present`
- `.repository/pm-main/.test/20260420-152708-658/report.md`：`HEAD` 红灯，证明旧 `index_training_center_layout.css` 仍是 `1047` 行，且 moved selectors 还留在主文件
- `.repository/pm-main/.test/20260420-152716-572/report.md`：working tree 绿灯，证明 split probe 已通过，layout 主文件降到 `958` 行
- `.repository/pm-main/.test/20260420-152547-463/report.md`：最新 `line budget` 仍 fail-closed，但 `blocking_offender_count=5`

风险与保留：
- `pm/daily-execution-history/2026-04-20.md` 仍缺失，因为今天的每日学习任务与真实学习报告还没收口
- `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 的 developer workspace 仍停在 `cec137`，相对 `code_root@71ab7da` 仍是 `diverged_or_unknown`

memory_ref: `.codex/memory/2026-04/2026-04-20.md`
