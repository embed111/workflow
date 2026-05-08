# 非内建项目连续性与 quiet probe 经验

## 适用范围
- 非内建项目 registry / runtime policy 连续性
- `verify_project_ops_live_regression.py --require-quiet-project`
- prod 上 quiet non-builtin sample 的 exact live evidence

## 稳定经验
- 如果 non-builtin 项目曾经在 live prod 存在过，但后续因为手改 runtime state 或 unsupported 删除而从 `project-registry.json` / `project-runtime-policies.json` 消失，不要直接在 prod 重新 bootstrap 新 fixture。更稳的默认是：先用精确匹配当前 `runtime_root` 的历史 live 证据恢复同一条项目 row 和 runtime policy，再继续 quiet probe 或切版判断。
- 但这条恢复能力只适用于“仍被明确要求继续存在”的项目。若用户已经要求退役某个项目，尤其是 `project-comics-smoke / Comics Bootstrap Smoke` 这类一次性 smoke 项目，正确做法是保留 `lifecycle_state=archived` 的 tombstone，并把 runtime policy 置为 `manual_pause=true`；不要物理删除 tombstone，也不要再按历史 evidence 恢复成 active。
- 支持恢复时，证据源不能只看“文件里出现过同名项目”。更稳的默认是：同时校验 `project_registry_path` 和 `runtime_policy_registry_path` 必须精确命中目标 `runtime_root`，避免把 `test` fixture 或其他环境的样本误恢复到 `prod`。
- quiet project probe 要区分两层合同：
  - `自然 quiet 样本合同`：只要求 non-builtin 项目、`default_tab=overview`、`task_signal_summary/default_tab_reason` 表明 `proof 已完成`、项目合同与 `created_artifacts` 可回读。
  - `test fixture 合同`：只在 fixture 路径里额外要求 `next_handoff_interval_minutes=15`、`failure_retry_cooldown_minutes=45`、`failure_retry_max_attempts=4`、`failure_escalation_threshold=3`、`minimum_member_count=2`、`allowed_run_window=09:00-23:00`。
- 不要把 `test fixture` 的 handoff/cooldown/window 参数误当成 prod 自然样本的硬条件。否则 prod 明明已经恢复了 quiet sample，`--require-quiet-project` 仍会被假 blocker 卡住。
- 更进一步，不能把临时 quiet sample 变成长期发布门禁。`project-comics-smoke` 退役后，`workflow gate` 和 `runtime release gate` 都不应再强制检查它的 continuity/readback/startup-ready；未来多项目能力回归要使用中性 fixture 或当前真实 active 项目。
- 当前恢复脚本仍可作为受控工具保留，但不再作为 `project-comics-smoke` 的自动恢复入口：
  - 恢复脚本：`.repository/pm-main/scripts/repair_project_registry_from_evidence.py`
  - 历史验收脚本：`.repository/pm-main/scripts/acceptance/verify_project_registry_evidence_restore.py`
  - 历史 quiet-mode 脚本：`.repository/pm-main/scripts/acceptance/verify_project_ops_live_regression_quiet_mode.py`
