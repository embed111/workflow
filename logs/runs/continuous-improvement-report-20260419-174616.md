# Continuous Improvement Report

- generated_at: `2026-04-19T17:46:16+08:00`
- active_version: `V4`
- task_package: `V4-R6`
- lane: `工程质量探测`
- lifecycle_stage: `变更控制`
- baseline: `prod=20260419-144557`
- preference_ref: `state/user-preferences.md`

## Change Control
- 本轮不是普通修补，而是把“行数探测只报不拦”正式升级为当前 active 版本里的强制门禁治理。
- 当前变更同时落在三层：
  - 版本/发布治理文档
  - line budget checker
  - workflow gate / runtime release gate

## Actions
- 新增 `V4-R6 工程质量门禁强制化与超大文件治理一期`，并回写到：
  - `pm/versions/V4/版本计划.md`
  - `pm/PM当前版本计划.md`
  - `pm/versions/V4/需求映射与覆盖矩阵.md`
- 更新治理真相：
  - `docs/workflow/governance/默认发布约束.md`
  - `docs/workflow/requirements/需求详情-代码体积治理与无损重构.md`
- 修改 `.repository/pm-main/scripts/quality/check_workspace_line_budget.py`
  - 新增 `mandatory_gate`
  - 默认退出码改为按 `Mandatory Gate` fail-closed
- 修改 `.repository/pm-main/scripts/acceptance/run_acceptance_workflow_gate.py`
  - `workspace_line_budget` 改为读取 `mandatory_gate_pass`
- 修改 `.repository/pm-main/scripts/acceptance/run_acceptance_runtime_release_gate.py`
  - `workspace_line_budget` 改为读取 `mandatory_gate_pass`
- 新增 `.repository/pm-main/scripts/acceptance/verify_workspace_line_budget_mandatory_gate.py`
  - 用 fixture workspace 验证两个 gate helper 都已跟上新的强制门禁口径

## Validation
- `py_compile` 通过：
  - `.repository/pm-main/.test/20260419-174351-782/report.md`
- `verify_workspace_line_budget_mandatory_gate.py` 通过：
  - `.repository/pm-main/.test/20260419-174358-998/report.md`
- 真实 workspace `line budget` 已按预期 fail-closed：
  - `.repository/pm-main/.test/20260419-174511-394/report.md`
  - `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- `workflow gate` 已按预期被新的强制门禁拦下：
  - `.repository/pm-main/.test/20260419-174526-162/report.md`
  - `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260419-174532.md`
- `runtime release gate` 已按预期被新的强制门禁拦下：
  - `.repository/pm-main/.test/20260419-174540-523/report.md`
  - `.repository/pm-main/.test/manual-release-gate/test-gate-manual-mandatory-gate-check.json`

## Current Gate Truth
- `mandatory_gate_pass=false`
- `hard_gate_pass=true`
- `refactor_trigger_count=31`
- `guideline_trigger_count=8`
- 当前 blocker 来源：
  - `refactor_trigger_gate`
  - `guideline_gate`
- 当前最大热点：
  - `src/workflow_app/server/services/schedule_service.py=3841`
  - `src/workflow_app/web_client/assignment_center_render_runtime.js=2838`
  - `scripts/workflow_env_common.ps1=2222`

## Release Boundary
- `pm-main` 当前仍是本地 dirty 批次：
  - `git status --short --branch` = `## main...origin/main [ahead 22]`
  - `dirty_tracked_count=6 / untracked_count=1`
- 当前不继续：
  - `test` 部署
  - `prod candidate` 刷新
- 原因：
  - `Mandatory Gate` 已进入 fail-closed
  - 当前治理批次还没把真实 blocker 清到可发布状态

## Next
- 先冻结 `V4-R6` 的首批拆分顺序，默认从 `schedule_service.py`、`assignment_center_render_runtime.js`、`workflow_env_common.ps1` 开始。
- 在 `Mandatory Gate` 重新转绿前，不继续默认发布链路。
