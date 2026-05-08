# continuous improvement report 2026-04-15 03:16:08

- preference_ref: state/user-preferences.md
- delta_observation: `workflow_devmate / workflow_qualitymate / workflow_bugmate` 的 2026-04-15 学习报告都已经 delivered，但旧的 PM delivery projection 仍会漏掉真实自由标题下的当日报告；同时我在修第一次 fallback 时，又发现旧日期的 `workflow_testmate` 学习报告会被误投影进今天。
- delta_validation: 下一轮优先继续核 `workflow_testmate` 的 2026-04-15 学习节点 `node-20260415-021148-2cb441` 是否已经从 `running / artifact_delivery_status=pending` 收束到真实交付；如果还没收束，就继续沿 node/run/delivery 三条真相查，不再让旧报告干扰 today daily 判断。

## Summary

- 我在 `.repository/pm-main/src/workflow_app/server/services/pm_daily_governance_service.py` 修掉了 PM daily governance 对 helper 学习报告 delivery inbox 的识别偏差：现在既能识别真实自由标题下的学习报告，又会强制要求 `task_name` 或 `delivered_at` 命中当天日期，避免把旧日报误投影到今天。
- 我同步更新了 `.repository/pm-main/scripts/acceptance/verify_pm_daily_governance_tc_pm_002.py`，并按 `test-session-manager` 跑过 `.repository/pm-main/.test/20260415-031359-994/report.md`、`.repository/pm-main/.test/20260415-031400-026/report.md`、`.repository/pm-main/.test/20260415-031400-074/report.md`，确认 `py_compile`、`TC-PM-002` 和治理自动化回归都通过。
- 我把 dev workspace 两拍提交收成 `590ad63 / fad7df2`，再用受支持的 `../workflow_code <- .repository/pm-main` `fetch + ff-only merge` 把根仓追到 `fad7df2`，随后停 `test` 并重部署，刷新出新的 `prod candidate=20260415-031506`。
- 我用 `python .repository/pm-main/scripts/bin/refresh_pm_daily_governance.py --shell-root D:/code/AI/J-Agents/workflow --date 2026-04-15` 把 `workflow_devmate / workflow_qualitymate / workflow_bugmate` 三份 2026-04-15 学习报告投影进 PM 仓，同时删掉了误投影的 `workflow_testmate` 旧日报；现在 today daily 的真实缺口只剩 `workflow_testmate` 的 2026-04-15 报告。

## Validation

- `.repository/pm-main/.test/20260415-031359-994/report.md`
- `.repository/pm-main/.test/20260415-031400-026/report.md`
- `.repository/pm-main/.test/20260415-031400-074/report.md`
- `python .repository/pm-main/scripts/bin/refresh_pm_daily_governance.py --shell-root D:/code/AI/J-Agents/workflow --date 2026-04-15`
- `.running/control/logs/test/deploy-20260415-031506.json`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `http://127.0.0.1:8090/api/schedules`
