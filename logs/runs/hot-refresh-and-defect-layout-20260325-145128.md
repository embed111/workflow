# Hot Refresh And Defect Layout 20260325-145128

- time: `2026-03-25T14:51:28+08:00`
- scope: `F5 热刷新不再重进全屏 startup + 缺陷提交区不再长期挤压列表`
- source_root: `C:\work\J-Agents\workflow`
- preference_ref: `state/user-preferences.md`
- delta_observation: 用户指出按 `F5` 也会重新进入加载环节，同时缺陷提交区与缺陷列表共处左列，容易把列表可视空间挤掉并造成“记录没了”的错觉。
- delta_validation: 本轮先在开发态完成缺陷中心真实浏览器验收和启动遮罩最小运行态验证，再发布到 `test` 并恢复 `8092` 在线；`prod` 不直接操作。

## Result

- 主页面 startup overlay 改为默认隐藏，只有启动明显变慢或启动失败时才显示，不再每次 `F5` 都进入全屏 startup。
- 缺陷提交区改为可折叠，默认在已有缺陷记录且无草稿时收起，把左侧空间优先留给缺陷列表。
- 缺陷列表空态会直接提示“当前环境独立存储”，降低在 `test/prod` 切换时把环境隔离误判成记录丢失的概率。
- 当前修复已发布到 `test` 版本 `20260325-145026`，并重新启动在线服务。

## Validation

- 缺陷中心真实浏览器验收：
  - `.test/evidence/defect-center-browser/summary.json` 中 `ok=true`
- 启动遮罩最小运行态验证：
  - `.test/evidence/hot-refresh-overlay-min/summary.json` 中 `overlay_hidden_in_initial_html=true`
- `test` 发布：
  - `.running/control/logs/test/deploy-20260325-145026.json` 显示 `result=success`
  - `.running/control/reports/test-gate-20260325-145026.json` 显示 `result=passed`
  - `http://127.0.0.1:8092/healthz` 返回 `ok=true`

## Artifacts

- 缺陷中心模板：`src/workflow_app/server/presentation/templates/index.html`
- 缺陷中心样式：`src/workflow_app/server/presentation/templates/index_defect_center.css`
- 缺陷中心渲染：`src/workflow_app/web_client/defect_center_render_runtime.js`
- 缺陷中心事件：`src/workflow_app/web_client/defect_center_events.js`
- 启动遮罩状态：`src/workflow_app/web_client/app_status_and_icon_utils.js`
- 缺陷中心浏览器验收：`.test/evidence/defect-center-browser/summary.json`
- 启动遮罩最小验证：`.test/evidence/hot-refresh-overlay-min/summary.json`
- `test` 部署日志：`.running/control/logs/test/deploy-20260325-145026.json`
- `test` 门禁报告：`.running/control/reports/test-gate-20260325-145026.json`
- `prod` 候选文件：`.running/control/prod-candidate.json`

## Notes

- 为替换版本，仅停止并重启了 `test` 环境进程；`prod` 未被直接停止、重启或覆盖。
- `test gate` 仍有 line budget advisory / refactor trigger 提示，但硬门禁通过，不阻塞本次发布。
