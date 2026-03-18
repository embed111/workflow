# Session Snapshot

- updated_at: 2026-03-18T23:13:01+08:00
- preference_ref: state/user-preferences.md
- current_focus: 按正式链路完成 test 门禁、生成 prod candidate，并已切换 prod 到新版本
- delta_observation: 用户接受“先部署到 `test`、通过门禁生成候选、再在正式环境页面升级”的标准链路；本次升级前 `prod` 无运行中任务，`can_upgrade=true`
- delta_validation: `test` 部署版本=`20260318-150842`，测试会话=`.test/20260318-230842-156/`；候选=`.running/control/prod-candidate.json`；`prod` 已从 `20260318-073748` 升级到 `20260318-150842`，状态见 `.running/control/prod-last-action.json`；预升级页面证据=`logs/runs/prod-upgrade-20260318-prepare/pre-upgrade-dom.html`+`pre-upgrade.png`；升级后 DOM=`logs/runs/prod-upgrade-20260318-prepare/post-upgrade-dom.html`
