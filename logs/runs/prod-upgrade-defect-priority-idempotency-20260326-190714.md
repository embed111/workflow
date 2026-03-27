# 生产发布记录 20260326-190714

- topic: 缺陷中心当前工作区版本发布
- started_at: 2026-03-26T19:06:03+08:00
- finished_at: 2026-03-26T19:07:14+08:00
- source_workspace: `C:\work\J-Agents\workflow`
- released_version: `20260326-190603`
- previous_prod_version: `20260326-164817`
- candidate_source: `test`

## 发布动作
- 发现 `test` 环境仍有运行实例 `PID=4952`，先停止该实例后继续发布链路。
- 执行 `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/deploy_workflow_env.ps1 -Environment test`，生成并放行候选 `20260326-190603`。
- 调用 `POST http://127.0.0.1:8090/api/runtime-upgrade/apply`，将 `prod` 从 `20260326-164817` 切换到 `20260326-190603`。
- 等待 `8090` 恢复健康，并核对 `prod` 控制文件完成收口。

## 门禁与证据
- test gate: `C:\work\J-Agents\workflow\.running\control\reports\test-gate-20260326-190603.json`
- test deploy log: `C:\work\J-Agents\workflow\.running\control\logs\test\deploy-20260326-190603.json`
- prod manifest: `C:\work\J-Agents\workflow\.running\control\envs\prod.json`
- prod last action: `C:\work\J-Agents\workflow\.running\control\prod-last-action.json`

## 结果
- `test` 候选发布成功，`result=success`，`test_gate.status=passed`。
- `prod` 当前版本已更新为 `20260326-190603`，`deploy_status=deployed`。
- `prod-last-action.json` 显示本次升级 `status=success`，`previous_version=20260326-164817`。
- `GET http://127.0.0.1:8090/healthz` 返回 `ok=true`。
