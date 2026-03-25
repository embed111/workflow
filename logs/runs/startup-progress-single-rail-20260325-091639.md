# Startup Progress Single Rail 20260325-091639

- time: `2026-03-25T09:16:39+08:00`
- scope: `初始化界面双进度条收口为单一阶段进度轨`
- source_root: `C:\work\J-Agents\workflow`
- preference_ref: `state/user-preferences.md`
- delta_observation: 用户指出初始化界面存在两个进度条，希望合成一套更清晰的启动进度表达。
- delta_validation: 后续启动页与主页面内的启动遮罩继续保持单一阶段进度轨，不再叠加独立横向填充条；涉及启动体验改动时优先补真实截图验证。

## Result

- `scripts/assets/workflow_startup_splash.html` 已移除独立横向进度条，保留百分比和单一阶段轨，阶段节点之间用纵向连接线表达整体进度。
- `src/workflow_app/server/presentation/templates/index.html` 的 `startupOverlay` 已移除单独的 bar DOM，只保留百分比、等待时长和阶段轨。
- `src/workflow_app/server/presentation/templates/index_startup_overlay.css` 已将启动遮罩改成单一阶段进度轨样式，覆盖 `active/done/error` 三种状态。
- `src/workflow_app/web_client/app_status_and_icon_utils.js` 不再尝试驱动不存在的 `startupOverlayBar`，仍沿用原有阶段推进逻辑驱动百分比和阶段状态。

## Validation

- 本地启动页截图
  - 文件：`.test/evidence/startup-progress-single-rail/startup-splash.png`
  - 结果：仅保留一套阶段进度轨，无独立横向填充条
- 本地主页面启动遮罩截图
  - 文件：`.test/evidence/startup-progress-single-rail/startup-overlay.png`
  - 结果：仅保留一套阶段进度轨，无独立横向填充条
- 临时验证环境
  - 端口：`127.0.0.1:8186`
  - `healthz`：通过
  - 临时进程：验证后已停止 `PID=30960`
- `test` 发布
  - 版本：`20260325-091550`
  - 部署日志：`.running/control/logs/test/deploy-20260325-091550.json`
  - 门禁报告：`.running/control/reports/test-gate-20260325-091550.json`
  - 结果：`result=success`，`status=passed`
- `prod` 候选状态
  - 当前正式版本：`20260324-205932`
  - 新候选版本：`20260325-091550`
  - 运行时状态：`candidate_is_newer=true`、`banner_visible=true`、`can_upgrade=true`
  - 结果：本轮未直接停止、重启或覆盖 `prod`

## Evidence

- 启动页资源：`scripts/assets/workflow_startup_splash.html`
- 主页面遮罩结构：`src/workflow_app/server/presentation/templates/index.html`
- 主页面遮罩样式：`src/workflow_app/server/presentation/templates/index_startup_overlay.css`
- 主页面遮罩状态驱动：`src/workflow_app/web_client/app_status_and_icon_utils.js`
- 启动阶段推进：`src/workflow_app/web_client/app_runtime_controls.js`
- 启动页截图：`.test/evidence/startup-progress-single-rail/startup-splash.png`
- 启动遮罩截图：`.test/evidence/startup-progress-single-rail/startup-overlay.png`
- `test` 部署日志：`.running/control/logs/test/deploy-20260325-091550.json`
- `test` 门禁报告：`.running/control/reports/test-gate-20260325-091550.json`
- `prod` 候选文件：`.running/control/prod-candidate.json`

## Notes

- `app_status_and_icon_utils.js` 不是独立可直接 `node --check` 的单文件入口，语法检查不作为本轮主验证手段；本轮改用真实页面截图和本地启动验证闭环。
- 当前 `test gate` 仍带 line budget advisory，但不影响本轮启动体验收口和候选发布。
