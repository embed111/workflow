# continuous-improvement-report

## 判断
- `version_transition_decision=stay(V5)`。
- 我这轮继续保持 `工程质量探测 / 发布边界收口`，不重复 prod live proof，直接把 `index_training_loop_panels.css` 的 graph/detail/drawer 大段样式拆成独立 CSS part。
- 当前真正的 blocker 还是 `Mandatory Gate=false`，不是 git 边界；这轮已经把 CSS 这条首批冻结对象挪掉，但 `schedule_service.py / workflow_env_common.ps1 / assignment_center_render_runtime.js` 还在前排。

## 取舍
- 我没有再做一轮同质化的 live API 试探。live 现在已经是 `1 running + 1 ready + 1 patrol ready/future`，连续性成立，重复 smoke 的收益低于继续压 Mandatory Gate。
- 我也没有把这批代码留在本地。定向验证过后，我直接把改动提交到 `pm-main@90c876f`，再用受支持的 `fetch + ff-only merge` 把 `../workflow_code` 追平到同一提交，恢复 `root_sync_state=clean_synced`。
- 我检查了 helper 是否需要介入；这轮没有新建 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate` 任务，因为当前最高价值切片就是 pm-main 本地这刀 CSS split，而且我还没把剩余三块 blocker 切成互不打架的下一批。

## 下一动作
- 先继续压 `schedule_service.py / workflow_env_common.ps1 / assignment_center_render_runtime.js`。
- 等 `line budget / workflow gate / runtime release gate` 进入下一阶段后，再部署 `test`、刷新 `prod candidate`，随后重跑同一条 supported live member-route proof，补齐正向 `project_id/project_ref` 证据。

## 必要证据
- 发布边界：`root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=90c876f / push_block_reason=mandatory_gate_fail_closed / next_push_batch=schedule_service.py / workflow_env_common.ps1 / assignment_center_render_runtime.js split + gate/acceptance`
- line budget：最新 `blocking_offender_count=36`，`index_training_loop_panels.css` 已压到 `909` 行并退出 `first_batch_targets`；当前新的首批冻结对象是 `schedule_service.py / workflow_env_common.ps1 / assignment_center_render_runtime.js`
- live：`running_task_count=1 / queued_task_count=2 / active_agent_count=1`；当前 mainline `node-sti-20260420-510da3d4` 仍在 `running`，下一条 mainline `node-sti-20260420-3271d0d8` 已 `ready`，patrol `node-sti-20260420-0bc31a6c` 也在 `ready`，下次 patrol 触发时间是 `2026-04-20T02:20:00+08:00`
- upgrade：`current_version=candidate_version=20260419-180446 / candidate_is_newer=false / can_upgrade=false / ghost_running_detected=false`
- 定向验证：
  - `.repository/pm-main/.test/20260420-021052-329/report.md`
  - `.repository/pm-main/.test/20260420-021059-007/report.md`
  - `.repository/pm-main/.test/20260420-021105-893/report.md`
  - `.repository/pm-main/.test/20260420-021112-076/report.md`

## Snapshot Addendum
- preference_ref: state/user-preferences.md
- delta_observation: 这轮继续证明“先把已验证小批次提交并追平根仓”比把 Mandatory Gate 小批次继续留在本地更值；同时 CSS split 只要切到完整 graph/detail/drawer 尾段，就能一次性把主文件压出首批冻结对象。
- delta_validation: 下一轮优先按同样的“小批次拆分 -> 定向 probe -> line budget -> 根仓追平”节奏继续打 `schedule_service.py / workflow_env_common.ps1 / assignment_center_render_runtime.js`。
