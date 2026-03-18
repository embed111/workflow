# 运行记录 - test 门禁后升级 prod

- timestamp: 2026-03-18T23:13:01+08:00
- request: 按标准链路先部署到 `test` 并生成 `prod candidate`，再通过正式环境网页升级
- runtime_environment: prod
- preference_ref: state/user-preferences.md

## 执行摘要

- `test` 部署成功，版本=`20260318-150842`
- `test` 门禁通过并生成新的 `prod candidate`
- 升级前 `prod` 当前版本=`20260318-073748`
- 升级前 `prod` 状态：`running_task_count=0`、`can_upgrade=true`、`banner_visible=true`
- 已触发正式升级，升级后 `prod` 当前版本=`20260318-150842`
- `prod-last-action` 记录结果=`success`

## 关键证据

- 测试会话报告: `.test/20260318-230842-156/report.md`
- 测试会话日志: `.test/20260318-230842-156/logs/test-run.log`
- `test` 部署报告: `.running/control/logs/test/deploy-20260318-150842.json`
- `test` 门禁证据: `.running/control/reports/test-gate-20260318-150842.json`
- `prod candidate`: `.running/control/prod-candidate.json`
- 升级前页面 DOM: `logs/runs/prod-upgrade-20260318-prepare/pre-upgrade-dom.html`
- 升级前页面截图: `logs/runs/prod-upgrade-20260318-prepare/pre-upgrade.png`
- 升级后页面 DOM: `logs/runs/prod-upgrade-20260318-prepare/post-upgrade-dom.html`
- 最近升级动作: `.running/control/prod-last-action.json`
- 部署/升级事件流: `.running/control/deployment-events.jsonl`

## 关键状态

- 升级前 `GET /api/runtime-upgrade/status`
  - `current_version=20260318-073748`
  - `candidate_version=20260318-150842`
  - `candidate_is_newer=true`
  - `can_upgrade=true`
  - `banner_visible=true`
  - `running_task_count=0`
- 升级申请返回
  - `message=prod upgrade accepted; page may reconnect shortly`
- 升级后 `GET /api/runtime-upgrade/status`
  - `current_version=20260318-150842`
  - `candidate_is_newer=false`
  - `can_upgrade=false`
  - `blocking_reason=暂无可升级版本`
- 升级后 `GET /api/status`
  - `environment=prod`
  - `show_test_data=false`
  - `agent_search_root_ready=true`

## 审计留痕摘录

- `.running/control/deployment-events.jsonl`
  - `deploy/test/20260318-150842 -> success`
  - `upgrade_switching/prod/20260318-150842 -> pending`
  - `upgrade/prod/20260318-150842 -> success`
- `.running/control/prod-last-action.json`
  - `previous_version=20260318-073748`
  - `current_version=20260318-150842`
  - `status=success`
  - `finished_at=2026-03-18T15:10:42.7316339Z`

## 备注

- 本次正式升级通过页面同源接口 `/api/runtime-upgrade/apply` 触发，等效于页面顶部“升级正式环境”按钮
- 本次轮询未观察到明显离线窗口，但最终状态与审计记录已确认切换成功
