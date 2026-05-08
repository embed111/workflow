# 持续迭代运行留痕 2026-04-20 01:44:10

- ticket: `asg-20260327-223335-b79f27`
- node: `node-sti-20260420-008ba4ef`
- version: `V5`
- lane: `工程质量探测 / 发布边界收口`
- lifecycle_stage: `开发实现`
- version_transition_decision: `stay(V5)`
- root_sync_state: `clean_synced`
- ahead_count: `0`
- dirty_tracked_count: `0`
- untracked_count: `0`
- push_block_reason: `mandatory_gate_fail_closed`
- next_push_batch: `schedule_service.py / workflow_env_common.ps1 / index_training_loop_panels.css split + gate/acceptance`

## 判断
- 我继续保持 `V5`，不切版。`next_activation_ready=false`；当前 blocker 仍是 `controller cadence closure` 缺 live finalize 消费证据、`prod/live member task` 还没有正向 `project_id/project_ref` 证据，以及 `Mandatory Gate` 仍未转绿。
- 这轮更高价值的不是重复 live proof，而是把上一轮 failed node 留下的 `assignment_center_render_runtime.js` split 直接收口，并优先把它从 Mandatory Gate 的首批冻结对象里挪出去。

## 推进动作
- 我新增 `.repository/pm-main/src/workflow_app/web_client/assignment_center_workboard_group_runtime.js` 和 `.repository/pm-main/src/workflow_app/web_client/assignment_center_workboard_sections.js`，把 assignment workboard 的 group/lane 逻辑与 version/project/schedule/failure/render 区块拆成两个 bundle part。
- 我更新 `.repository/pm-main/src/workflow_app/web_client/bundle_manifest.json`，把 workboard runtime 的装配顺序固定成 `group -> sections -> main runtime`。
- 我补上 `.repository/pm-main/scripts/acceptance/verify_assignment_workboard_runtime_split.py`，并把 `.repository/pm-main/scripts/acceptance/verify_assignment_workboard_layout_rules.js` 改成按 `bundle_manifest.json` 校验整包 JS，不再盯旧的单文件真相。
- 我把这批已验证改动提交成 `pm-main@882bc55 refactor(assignment): 拆分任务看板 runtime sections 以压低首批 blocker`，再用受支持的 `fetch + ff-only merge` 把 `../workflow_code` 追平到同一提交。

## 结果
- 我继承上一轮 failed node 留下的 `sections_missing:assignment_center_workboard_sections.js` 红灯后，这轮已经把 split probe 收绿。
- 最新 `line budget` 仍 fail-closed，但 `assignment_center_render_runtime.js` 已经退出 `first_batch_targets`；当前 clean head 的 `first_batch_targets` 已改成 `schedule_service.py / workflow_env_common.ps1 / index_training_loop_panels.css`。
- `assignment_center_render_runtime.js` 在最新 line budget 报告里已经降到 `1694` 行，新拆出的 `assignment_center_workboard_group_runtime.js=170`、`assignment_center_workboard_sections.js=953`，workboard runtime 边界已经从单体文件里剥开。
- live 连续性没有被我打断：`/healthz` 正常；当前是 `mainline running + next mainline ready + patrol ready / future`；`prod/candidate` 仍同为 `20260419-180446`，且 `running_task_count=1`，所以本轮没有升级空窗。

## 验证
- 红灯继承：上一轮 failed node `node-sti-20260420-f06823e8` 的失败摘要是 `sections_missing:assignment_center_workboard_sections.js`
- `verify_assignment_workboard_runtime_split.py`
  - `.repository/pm-main/.test/20260420-014011-485/report.md`（red）
  - `.repository/pm-main/.test/20260420-014041-237/report.md`（green）
- `verify_assignment_workboard_layout_rules.js`
  - `.repository/pm-main/.test/20260420-014048-032/report.md`（red）
  - `.repository/pm-main/.test/20260420-014131-447/report.md`（green）
- `verify_assignment_center_view_tabs_assets.py`
  - `.repository/pm-main/.test/20260420-014139-189/report.md`
- `check_workspace_line_budget.py --root .`
  - `.repository/pm-main/.test/20260420-014147-589/report.md`
  - `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.json`
- git / live
  - `git -C .repository/pm-main log -1 --pretty=format:"%H %cI %s"`
  - `git -C ../workflow_code log -1 --pretty=format:"%H %cI %s"`
  - `/healthz`
  - `/api/status`
  - `/api/schedules`
  - `/api/runtime-upgrade/status`

## 备注
- 当前 helper 仍未派发新增主线任务：`parallel_candidate_count=1 / parallel_dispatched_count=0 / active_helper_tasks=- / non_dispatch_reason=这轮最高价值切片是 pm-main 本地 Mandatory Gate 收口，而且我需要先把上一轮 failed split 收成 clean_synced`
- `pm/daily-execution-history/2026-04-20.md` 仍缺失；原因没变，今天的每日学习任务与真实学习报告还没收口，我这轮不伪造 completed 记录。
- preference_ref: `state/user-preferences.md`
- delta_observation: 上一轮 failed split probe 本身就是可复用红灯；把 layout probe 改成 bundle 真相源后，前端大文件拆片可以继续沿“red node -> green probe -> line budget 重排首批冻结对象”的节奏推进。
- delta_validation: 下一轮优先继续打 `schedule_service.py / workflow_env_common.ps1 / index_training_loop_panels.css` 的 Mandatory Gate blocker，再决定是否把下一刀切给 `workflow_devmate`。
- memory_ref: `.codex/memory/2026-04/2026-04-20.md`
