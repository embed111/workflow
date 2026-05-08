# Comics Bootstrap Smoke 退役收口

- time: `2026-04-27T22:00:46+08:00`
- preference_ref: `state/user-preferences.md`
- target_project_id: `project-comics-smoke`
- target_project_name: `Comics Bootstrap Smoke`

## 结论
- `Comics Bootstrap Smoke` 已从 active 项目列表移除。
- prod 中保留 archived tombstone，防止旧 continuity repair 把“记录缺失”误判成“需要恢复”。
- 旧 project-controller schedule `sch-20260421-5dda16b1` 已先 disable，再 delete，不再出现在 `/api/schedules`。
- 旧 release/workflow gate 中会强制要求 `project-comics-smoke` 存在、readback 或恢复的检查已从代码门禁中移除。

## 代码收口
- commit: `.repository/pm-main@1dff9b0 fix(project): 停用 comics smoke 恢复门禁`
- root sync: `../workflow_code/main@1dff9b0`
- 变更范围：
  - `scripts/workflow_env_runtime_upgrade.ps1`: project continuity repair 不再默认补 `project-comics-smoke`。
  - `scripts/acceptance/workflow_gate_probe_registry.py`: 移除 `project_ops_live_regression`、`project_ops_live_regression_quiet_mode`、`project_registry_evidence_restore`、`assignment_project_controller_self_iteration_schedule` gate 注册。
  - `scripts/acceptance/run_acceptance_runtime_release_gate.py`: 移除 release gate 中的 project continuity launch repair binding 与 project ops live regression 强制检查。
  - `scripts/acceptance/verify_runtime_release_gate_api_catalog_binding.py`: 同步 release gate 绑定验证。

## 文档约束
- `docs/workflow/governance/7x24连续运行机制.md`: 新增“已退役运营项目不再自动恢复”。
- `.codex/experience/project-registry-continuity-and-quiet-probe.md`: 补充 archived tombstone 与退役项目不恢复经验。

## 验证
- line budget: `.repository/pm-main/.test/20260427-215044-942/report.md`
- PowerShell parse: `.repository/pm-main/.test/20260427-215114-720/report.md`
- release gate binding: `.repository/pm-main/.test/20260427-215140-067/report.md`
- environment wrappers: `.repository/pm-main/.test/20260427-215151-866/report.md`
- test deploy / prod candidate:
  - `test=20260427-215714`
  - `prod candidate=20260427-215714`
  - evidence: `.running/control/reports/test-gate-20260427-215714.json`

## Live 状态
- `/api/projects`: active 仅 `workflow`、`project-ai-novel-profit`。
- `/api/projects?include_archived=true`: `project-comics-smoke` 为 `lifecycle_state=archived`、`manual_pause=true`、`startup_ready=false`、`blocking_items=[manual_pause_active]`。
- `/api/schedules`: `contains_project_comics_smoke=false`、`contains_comics_bootstrap_smoke=false`。
- `/api/runtime-upgrade/status`: `current_version=20260427-184256`、`candidate_version=20260427-215714`、`candidate_is_newer=true`、`request_pending=false`、`ghost_running_detected=false`。

## 后续边界
- 不自动 apply prod；按默认发布约束，生产仍由用户手动升级。
- 后续多项目能力验证不能再以 `project-comics-smoke` 作为必须存在样本。

## Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: 用户明确要求停用 `Comics Bootstrap Smoke`，且不希望为了旧 smoke 项目继续恢复或消耗 token。
- delta_validation: 后续遇到 project continuity / quiet project gate 时，先确认目标项目是否已退役；已退役项目只保留 tombstone，不恢复、不续挂、不设为门禁样本。
