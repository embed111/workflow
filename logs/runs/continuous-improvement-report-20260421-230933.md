# Continuous Improvement Report

## Judgment
- `version_transition_decision=stay(V7)`，这轮真正推进的是 `发布推进`。
- 我已把 `workflow_devmate` 的 `V7-R1` batch1 以 `e3cc78a` 收口到 `workflow_code`，部署出 `test=20260421-230632`，并刷新 `prod candidate=20260421-230632`。
- `workflow_testmate` 的 `V7-R3` batch1 不再是 running；它已经 partial pass。landed workspace 的两条消费 surface 都已回归通过，`8092` 上的 `workflow project_task_summary.interface_catalog_entry.status=ready` 也已经跟上新版本，当前 blocker 只剩 deployed role/task readback 与 compare fail-closed。

## Tradeoffs
- 我这轮没有继续开 `workflow_devmate` compare/read-model batch，也没有补 `workflow_ucdmate` UI refinement。回归结果已经证明当前最高价值 blocker 是 promotion/readback，不是 batch1 代码不完整。
- 我也没有伪造每日治理完成态；今日学习报告和 `pm/daily-execution-history` 继续保留 warning。

## Next Action
- 先等 `prod` idle watcher apply `candidate=20260421-230632`，然后复查 `8090` 的 deployed role/task host readback。
- 如果 `230632` 落地后，`status-detail.selected_node.interface_catalog_entry / role_interface_catalog_status` 仍缺，我就把它切成下一条 `workflow_devmate` compare/read-model batch，而不是扩大到 `V8`。
- `V8` 仍未初始化，所以当前切版判断继续保持 `stay(V7)`。

## Evidence
- commit: `e3cc78a feat(interface): 接通项目与角色的接口目录消费入口`
- test sessions:
  - `.repository/workflow_devmate/.test/20260421-230343-188/report.md`
  - `.repository/workflow_devmate/.test/20260421-230354-120/report.md`
  - `.repository/workflow_devmate/.test/20260421-230401-923/report.md`
  - `.repository/workflow_devmate/.test/20260421-230409-017/report.md`
- deploy report: `.running/control/logs/test/deploy-20260421-230632.json`
- live readback:
  - `http://127.0.0.1:8092/api/status`
  - `http://127.0.0.1:8090/api/runtime-upgrade/status`
  - `state/developer-workspaces.json`

## Warnings
- `prod` 仍是 `20260421-210425`；`candidate=20260421-230632` 已更高，正在等待空窗升级。
- `V7-R2` compare 仍然 fail-closed，因为 `baseline_version / per_probe_results / compare_target_ref` 还没到位。
- `pm/daily-execution-history/2026-04-20.md`、`pm/daily-execution-history/2026-04-21.md` 与 `pm/daily-learning-reports/2026-04-21/` 仍未补齐。

- preference_ref: state/user-preferences.md
- delta_observation: 当回归已经把 blocker 收口为 promotion/readback 时，我这轮继续优先做 root-sync、test/candidate 刷新和开发工作区 refresh，而不是重复状态播报或提前扩 compare/UI scope。
- delta_validation: 下一轮直接以 `230632` 的 deployed role/task readback 为主验证面；若该面仍缺，再切 `workflow_devmate` compare/read-model batch，而不是先写更多计划解释。
- memory_ref: `.codex/memory/2026-04/2026-04-21.md`
