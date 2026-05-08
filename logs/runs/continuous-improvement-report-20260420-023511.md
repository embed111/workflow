# continuous-improvement-report

## 判断
- `version_transition_decision=stay(V5)`。
- 我这轮继续保持 `工程质量探测 / 发布边界收口`，没有重复 prod live proof，而是把 assignment detail 与 drawer helper 从 `assignment_center_render_runtime.js` 抽到了新 bundle part `assignment_center_detail_drawer_runtime.js`。
- 当前真正的 blocker 还是 `Mandatory Gate=false`，不是 git 边界；这轮已经把 `assignment_center_render_runtime.js` 挪出首批冻结对象，但 `schedule_service.py / workflow_env_common.ps1 / run_acceptance_role_creation_browser.py` 还在前排。

## 取舍
- 我没有再做一轮同质化的 live API 试探。live 现在仍是 `1 running + 2 queued/ready` 的连续推进态，重复 smoke 的收益低于继续压 Mandatory Gate。
- 我也没有把这批代码留在本地。定向验证过后，我直接把改动提交到 `pm-main@eeaa6cc`，再用受支持的 `fetch + ff-only merge` 把 `../workflow_code` 追平到同一提交，恢复 `root_sync_state=clean_synced`。
- 我检查了 helper 是否需要介入；这轮没有新建 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate` 任务，因为当前最高价值切片就是 pm-main 本地这刀 detail/drawer split，而且新的第三个 blocker 已切到 `run_acceptance_role_creation_browser.py`，我得先把下一批边界重新切干净。

## 下一动作
- 先继续压 `schedule_service.py / workflow_env_common.ps1 / run_acceptance_role_creation_browser.py`。
- 等 `line budget / workflow gate / runtime release gate` 进入下一阶段后，再部署 `test`、刷新 `prod candidate`，随后重跑同一条 supported live member-route proof，补齐正向 `project_id/project_ref` 证据。

## 必要证据
- 发布边界：`root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=eeaa6cc / push_block_reason=mandatory_gate_fail_closed / next_push_batch=schedule_service.py / workflow_env_common.ps1 / run_acceptance_role_creation_browser.py split + gate/acceptance`
- line budget：最新 `blocking_offender_count=36`，`assignment_center_render_runtime.js` 已从 `1694` 行压到 `1334` 行并退出 `first_batch_targets`；当前新的首批冻结对象是 `schedule_service.py / workflow_env_common.ps1 / run_acceptance_role_creation_browser.py`
- live：`running_task_count=1 / queued_task_count=2 / active_agent_count=1`；当前 mainline 是 `node-sti-20260420-3271d0d8 (running)`，patrol 是 `node-sti-20260420-f70965ef (ready)`，下一次 patrol 触发时间是 `2026-04-20T02:40:00+08:00`
- upgrade：`current_version=candidate_version=20260419-180446 / candidate_is_newer=false / can_upgrade=false / ghost_running_detected=false`
- 定向验证：
  - `.repository/pm-main/.test/20260420-023233-951/report.md`
  - `.repository/pm-main/.test/20260420-023240-893/report.md`
  - `.repository/pm-main/.test/20260420-023247-695/report.md`
  - `.repository/pm-main/.test/20260420-023258-677/report.md`
  - `.repository/pm-main/.test/20260420-023304-788/report.md`

## Snapshot Addendum
- preference_ref: state/user-preferences.md
- delta_observation: 当 `assignment_center_render_runtime.js` 已完成 workboard split 后，继续把 detail/drawer surface 抽到独立 bundle part，可以在不重复 live smoke 的前提下把主文件从 Mandatory Gate 首批冻结对象里挪出去。
- delta_validation: 下一轮优先沿同样的“小批次拆分 -> 定向 probe -> line budget -> 根仓追平”节奏继续打 `schedule_service.py / workflow_env_common.ps1 / run_acceptance_role_creation_browser.py`。

- memory_ref: `.codex/memory/2026-04/2026-04-20.md`
