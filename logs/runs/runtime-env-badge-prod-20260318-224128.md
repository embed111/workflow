# 运行记录 - 左上角环境徽标

- timestamp: 2026-03-18T22:42:51+08:00
- request: 在左上角 `workflow` 文本旁标注当前处于什么环境，便于同时运行多个环境时快速区分
- runtime_environment: prod
- preference_ref: state/user-preferences.md

## 影响代码

- `src/workflow_app/server/presentation/templates/index.html`
- `src/workflow_app/web_client/app_runtime_state_helpers.js`
- `src/workflow_app/server/presentation/templates/index_training_center_layout.css`
- `.running/prod/src/workflow_app/server/presentation/templates/index.html`
- `.running/prod/src/workflow_app/web_client/app_runtime_state_helpers.js`
- `.running/prod/src/workflow_app/server/presentation/templates/index_training_center_layout.css`

## 实现说明

- 顶部品牌位新增 `#runtimeEnvBadge`，模板默认显示 `SOURCE`
- 前端复用既有 `state.runtimeEnvironment`，在启动后按 `DEV/TEST/PROD/SOURCE` 更新徽标文字、`data-env` 和辅助文本
- 样式按环境区分颜色：`dev=green`、`test=amber`、`prod=red`、`source=gray`
- 未新增新的后端接口或运行时开关，继续沿用环境策略只读口径

## 验证证据

- `GET http://127.0.0.1:8090/healthz` -> `{"ok":true,"ts":"2026-03-18T22:40:06+08:00"}`
- `GET http://127.0.0.1:8090/api/status` -> `environment=prod`、`show_test_data=false`、`show_test_data_source=environment_policy`
- `GET http://127.0.0.1:8090/api/config/show-test-data` -> `deprecated=true`、`read_only=true`、`environment=prod`
- Headless DOM: `logs/runs/runtime-env-badge-prod-20260318-224128/home-dom.html`
- DOM 结果: `<span id="runtimeEnvBadge" class="brand-env-badge" data-env="prod" ...>PROD</span>`
- Screenshot: `logs/runs/runtime-env-badge-prod-20260318-224128/home.png`

## 备注

- 页面模板中的静态默认值为 `SOURCE`，真实显示值由启动后的环境策略响应驱动更新
- 本次实现与“测试数据展示由环境策略决定、前端只读消费”的最新文档口径一致
