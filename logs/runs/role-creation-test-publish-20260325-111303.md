# Role Creation Test Publish 20260325-111303

- time: `2026-03-25T11:13:03+08:00`
- scope: `创建角色隔离修复通过开发态浏览器验收后发布到 test`
- source_root: `C:\work\J-Agents\workflow`
- preference_ref: `state/user-preferences.md`
- delta_observation: 用户要求代码改动先在开发/临时环境验证，通过后默认发布到 `test`；`prod` 只保留用户手动升级，不直接停机覆盖。
- delta_validation: 本轮仅执行 `scripts/deploy_workflow_env.ps1 -Environment test`，核对部署日志、门禁报告与 `prod-candidate`，不触碰正式环境运行实例。

## Result

- 已发布 `test` 版本 `20260325-111152`。
- `test` 部署日志显示 `result=success`。
- `test gate` 报告显示 `result=passed`。
- `test` 环境当前在线：`http://127.0.0.1:8092/healthz` 返回 `ok=true`。
- `prod candidate` 已更新到 `20260325-111152`，供正式环境页面内人工选择升级。

## Validation

- 开发态验收证据：
  - `.test/evidence/role-creation-browser-acceptance/summary.json` 中 `ok=true`
  - `.test/evidence/role-creation-browser-acceptance/screenshots/rc_profile_tab.probe.json` 中 `pass=true`
  - `.test/evidence/role-creation-browser-acceptance/screenshots/rc_high_load.probe.json` 中 `pass=true`
- 发布命令：
  - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/deploy_workflow_env.ps1 -Environment test`
- 发布产物：
  - `.running/control/logs/test/deploy-20260325-111152.json`
  - `.running/control/reports/test-gate-20260325-111152.json`
  - `.running/control/prod-candidate.json`
  - `.running/control/envs/test.json`
  - `.running/control/pids/test.pid`

## Evidence

- 开发态浏览器验收总结：`.test/evidence/role-creation-browser-acceptance/summary.md`
- 开发态浏览器验收 JSON：`.test/evidence/role-creation-browser-acceptance/summary.json`
- 先前隔离修复记录：`logs/runs/role-creation-browser-acceptance-codex-isolation-20260325-104407.md`
- `test` 部署日志：`.running/control/logs/test/deploy-20260325-111152.json`
- `test` 门禁报告：`.running/control/reports/test-gate-20260325-111152.json`
- `prod` 候选文件：`.running/control/prod-candidate.json`

## Notes

- 本轮没有直接停止、重启或覆盖 `prod`。
- `test gate` 仍包含 line budget advisory / refactor trigger 提示，但不阻塞本次 `test` 发布，硬门禁已通过。
