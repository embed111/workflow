# Continuous Improvement Report 2026-04-13 13:12

- preference_ref: state/user-preferences.md
- delta_observation: 切换 active 版本时，如果只改 `PM当前版本计划.md` 而不把新 active 版本文件同步升级成可解析的当前快照态，`pm_version_status` 和对应 acceptance 会一起掉空。
- delta_validation: 下一轮先派发 `V2-R7` 的映射盘点 helper，再确认新 materialize 的 mainline 节点是否已经稳定继承 `V2 / 需求分析 / 形成基线 / workspace_head=4afd071`。

## Summary
- active_version=`V2`
- lane=`需求分析`
- lifecycle_stage=`形成基线`
- baseline=`prod=20260413-112439`
- workspace_head=`4afd071`
- candidate_version=`20260413-130821`

## This Round
- 我正式化了 `workflow_testmate` 的 post-upgrade dispatch 回归脚本，修掉空字符串绑定和观测窗口内重型读链重复调用。
- 我让 `verify_pm_version_truth_source.py` 跟随 `active_version_file`，并补齐了 `V2` 版本文件的当前快照与需求级 ETA。
- 我完成了 `workflow gate`，把 `pm-main` 收口到 `4afd071`，同步到本机 `../workflow_code`，并刷新出新的 `prod candidate=20260413-130821`。

## Validation
- `.repository/pm-main/.test/20260413-125344-064/report.md`
- `.repository/pm-main/.test/20260413-125344-373/report.md`
- `.repository/pm-main/.test/20260413-125344-379/report.md`
- `.repository/pm-main/.test/20260413-130119-562/report.md`
- `.repository/pm-main/.test/20260413-130131-717/report.md`
- `.running/control/logs/test/deploy-20260413-130821.json`

## Warnings
- `prod` 当前仍运行在 `20260413-112439`；`20260413-130821` 正等待 idle watcher 在空窗自动切入。
- 当前 `12:18` running 节点与 `12:39` ready 节点属于修复前已 materialize 的过渡态；schedule 级 `launch_summary` 和 live `pm_version_status` 已恢复到 `V2` 正确读链。
