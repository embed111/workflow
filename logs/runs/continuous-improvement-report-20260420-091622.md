# Continuous Improvement Report

- generated_at: `2026-04-20T09:16:22+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260420-f55d8c7d`
- preference_ref: `state/user-preferences.md`
- delta_observation: `你更重视版本真的前进，而不是重复播报；这轮我继续保持“先判断、再取舍、再给下一动作”的交付顺序。`
- delta_validation: `下一轮继续先选最高价值 blocker 切片，再用同样顺序交付，不回到状态墙。`

## 判断

- `version_transition_decision=stay(V5)`。
- 本轮推进项明确记为 `工程质量探测 / 发布边界收口 / V5-R5`。
- 我没有重复上一轮的 `graph_model_and_payloads.py` split，而是改切新的双门禁 blocker `index_training_center_role_creation.css`。

## 取舍

- 我优先处理 `role creation` 的 detail/stage/profile/hover-float CSS surface，因为它同时命中 `refactor_trigger_gate + guideline_gate`，而且比回头再打 `schedule_service.py` 更适合做成一刀见效的 fail-closed partial。
- 我没有给 helper 新派主任务。当前 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 的 developer workspace 仍停在 `cec137`，相对 `code_root@f00cd3f` 是 `diverged_or_unknown`；这轮继续强派只会把旧工作区重新拉进主线。

## 结果

- 我新增了 [index_training_center_role_creation_detail.css](/D:/code/AI/J-Agents/workflow/.repository/pm-main/src/workflow_app/server/presentation/templates/index_training_center_role_creation_detail.css)，把 role creation detail/stage/profile/hover-float surface 从主 CSS 里抽成独立 manifest part。
- 我更新了 [index_css_manifest.json](/D:/code/AI/J-Agents/workflow/.repository/pm-main/src/workflow_app/server/presentation/templates/index_css_manifest.json) 和 [verify_training_center_role_creation_css_split.py](/D:/code/AI/J-Agents/workflow/.repository/pm-main/scripts/acceptance/verify_training_center_role_creation_css_split.py)，并把新 probe 挂进 [workflow_gate_probe_registry.py](/D:/code/AI/J-Agents/workflow/.repository/pm-main/scripts/acceptance/workflow_gate_probe_registry.py)。
- 主 CSS [index_training_center_role_creation.css](/D:/code/AI/J-Agents/workflow/.repository/pm-main/src/workflow_app/server/presentation/templates/index_training_center_role_creation.css) 从 `1205` 行压到 `696` 行，新 split part 为 `510` 行。
- 最新 `line budget` 仍 `fail-closed`，但 `blocking_offender_count` 已从 `21` 降到 `19`，`guideline_gate` offender 从 `2` 降到 `1`，首批冻结对象改成 `schedule_service.py / workflow_env_common.ps1 / defect_service_task_commands.py`。
- 代码已收口到 `pm-main@f00cd3f`，并同步到 `../workflow_code@f00cd3f`；当前发布边界为 `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0`。

## 证据

- 红灯会话：`.repository/pm-main/.test/20260420-090840-131/report.md`
- 绿灯会话：`.repository/pm-main/.test/20260420-091315-406/report.md`
- 回归会话：`.repository/pm-main/.test/20260420-091321-975/report.md`
- 语法会话：`.repository/pm-main/.test/20260420-091328-983/report.md`
- 最新 line budget：`.repository/pm-main/.test/20260420-091339-589/report.md`
- live 真相：`/api/status` 仍为 `running_task_count=1 / queued_task_count=2 / active_agent_count=1`；`/api/runtime-upgrade/status` 仍为 `candidate_version=prod=20260419-180446 / candidate_is_newer=false / can_upgrade=false / ghost_running_detected=false`。

## 下一动作

- 继续正面打 `schedule_service.py / workflow_env_common.ps1 / defect_service_task_commands.py`，先把 Mandatory Gate 再往下压。
- 等 `line budget / workflow gate / runtime release gate` 到可发布状态后，再部署 `test`、刷新 `prod candidate`，然后重跑 supported live member-route 正向证据。
- `memory_ref: .codex/memory/2026-04/2026-04-20.md`
