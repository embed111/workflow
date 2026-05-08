# 持续迭代运行留痕 2026-04-20 01:15:40

- ticket: `asg-20260327-223335-b79f27`
- node: `node-sti-20260420-ecbc8d55`
- version: `V5`
- lane: `工程质量探测 / 发布边界收口`
- lifecycle_stage: `开发实现`
- version_transition_decision: `stay(V5)`
- root_sync_state: `clean_synced`
- ahead_count: `0`
- dirty_tracked_count: `0`
- untracked_count: `0`
- push_block_reason: `mandatory_gate_fail_closed`
- next_push_batch: `assignment_center_render_runtime.js / schedule_service.py / workflow_env_common.ps1 split + gate/acceptance`

## 判断
- 我这轮继续保持 `V5`，不切版。原因没变：`controller cadence closure` 仍缺 live finalize 消费证据，`prod/live member task` 仍没有正向项目字段证据，`Mandatory Gate` 也还没转绿。
- 当前最值钱的动作不是再做一轮同类 live probe，而是继续削掉 clean head 上的首批 blocker。我选了 `index_training_loop_panels.css`，因为它是最容易在本轮直接退出 first batch targets 的一刀。

## 推进动作
- 我新增了 `.repository/pm-main/src/workflow_app/server/presentation/templates/index_assignment_workboard_version_project.css`，把 assignment workboard 的 version/project 样式独立成 CSS part。
- 我更新了 `.repository/pm-main/src/workflow_app/server/presentation/templates/index_css_manifest.json`，让 `/static/workflow-web.css` 正式装配新 part。
- 我新增了 `.repository/pm-main/scripts/acceptance/verify_assignment_workboard_version_project_css_split.py`，锁住“主 CSS 不再内联 version/project 样式 + 新 part 已进 manifest”的 contract。
- 我同步更新 `.repository/pm-main/scripts/acceptance/verify_assignment_workboard_layout_rules.js`，让它按 `index_css_manifest.json` 校验整包 CSS，而不是误把单个 part 文件当成唯一真相。
- 我把这批已验证改动提交成 `pm-main@c58d4ce refactor(assignment): 拆分任务看板版本与项目样式以压低 CSS blocker`，并用受支持的 `fetch + ff-only merge` 把 `../workflow_code` 追平到同一提交。

## 结果
- 最新 `line budget` 仍 fail-closed，但 `index_training_loop_panels.css` 已从 `2040` 行降到 `1695` 行，并且已经退出 `first_batch_targets`。
- 当前新的 `first_batch_targets` 已变成 `assignment_center_render_runtime.js / schedule_service.py / workflow_env_common.ps1`。
- 当前 `prod/candidate` 仍同为 `20260419-180446`；live 仍是 `running_task_count=1 / queued_task_count=2`，所以本轮没有升级空窗，也没有推进 `test/prod candidate`。

## 验证
- `verify_assignment_workboard_version_project_css_split.py`
  - `.repository/pm-main/.test/20260420-011300-882/report.md`
- `verify_assignment_workboard_layout_rules.js`
  - `.repository/pm-main/.test/20260420-011301-151/report.md`
- `verify_assignment_center_view_tabs_assets.py`
  - `.repository/pm-main/.test/20260420-011301-151-01/report.md`
- `check_workspace_line_budget.py --root .`
  - `.repository/pm-main/.test/20260420-011301-151-02/report.md`
  - `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.json`
- live API
  - `/healthz`
  - `/api/status`
  - `/api/schedules`
  - `/api/runtime-upgrade/status`

## 备注
- `pm/daily-execution-history/2026-04-20.md` 仍缺失；原因不是忘记，而是今天的每日学习任务与真实学习报告尚未收口，我这轮不伪造 completed 记录。
- preference_ref: `state/user-preferences.md`
- delta_observation: 这轮继续证明“先做最容易退出首批冻结对象的一刀”比重复 live proof 更能直接推进 Mandatory Gate。
- delta_validation: 下一轮优先继续切 `assignment_center_render_runtime.js` 或 `schedule_service.py / workflow_env_common.ps1`，再决定是否把下一刀派给 `workflow_devmate`。
