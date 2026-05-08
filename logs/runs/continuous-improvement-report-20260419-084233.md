# continuous-improvement-report-20260419-084233

- preference_ref: state/user-preferences.md
- delta_observation: 当前 `08:01` workflow 主线的 live prompt 虽已对齐 baseline，但 `previous-result` 上下文仍输出 `@<head> / <version>` 尖括号占位；我已在 `pm-main/workflow_code@30dd373` 把它收成 `当前提交 / 当前版本 / 当前候选` 这类自然化脱敏文案，并把对应 probe 接进 `workflow gate`。
- delta_validation: 等当前 mainline 收尾并让 idle watcher 把 `prod` 升到 `20260419-084003` 后，对 `08:35` workflow mainline / `08:40` patrol 做 live 连续对话抽样，确认 `previous-result` 上下文不再出现尖括号占位。
- decision: `version_transition_decision=stay(V4)`；当前 blocker=`V4-R5` 仍缺 `prod=20260419-084003` 下的 live 连续对话抽样；`V5` 仍是 `activation_readiness=draft`。
- evidence:
  - `root_sync_state=clean_synced / workspace_head=code_root_head=30dd373 / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0`
  - `workflow gate`: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260419-083843.md`
  - `test deploy`: `.running/control/logs/test/deploy-20260419-084003.json`
  - `live status-detail`: `/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260419-70c8289d&include_test_data=0`
