# continuous-improvement-report-20260419-091935

- preference_ref: state/user-preferences.md
- delta_observation: 当前 `08:35` workflow 主线的 live `node_goal` 仍会把上一轮结果里的字面量 `@<head> / <version>` 和截断 `memory_ref=.codex/memory/...` 带回 prompt；仅替换真实版本号/commit 还不够。
- delta_validation: 等 `prod` 从 `20260419-084003` 升到 `20260419-091811` 后，对 post-upgrade 的 workflow mainline / patrol 做 live 连续对话抽样，确认 `previous-result` summary 不再出现 literal placeholder 或截断 `memory_ref`。
- decision: `version_transition_decision=stay(V4)`；当前 blocker=`V4-R5` 仍缺 `prod -> 20260419-091811` 后的 post-upgrade live 抽样；`V5` 仍是 `activation_readiness=draft`。
- evidence:
  - `root_sync_state=clean_synced / workspace_head=code_root_head=a745970 / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0`
  - `workflow gate`: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260419-091632.md`
  - `test deploy`: `.running/control/logs/test/deploy-20260419-091811.json`
  - `developer workspace status`: `python ../workflow_code/scripts/manage_developer_workspace.py --root .running/control/runtime/prod status`
  - `live upgrade status`: `/api/runtime-upgrade/status`
