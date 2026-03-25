# 缺陷详情页按原型图收口并发布 test - 2026-03-25 17:08:01

## 背景
- 用户要求 `bug` 详情界面也按原型图展示，不能只修列表与空态。
- 本轮目标是在不改后端缺陷接口的前提下，收口右侧详情结构、完成真实浏览器验收，并仅发布到 `test`。

## 代码改动
- `src/workflow_app/web_client/defect_center_render_runtime.js`
  - 重构右侧详情渲染，改为原型图式结构：顶部 `DTS` 编号/标题/状态、三张事实卡、原始上报、当前判定、补充与复评输入区、任务引用、状态时间线。
- `src/workflow_app/web_client/defect_center_state_helpers.js`
  - 调整缺陷状态 tone，`dispute` 与 `not_formal` 不再共用同一套泛化样式。
- `src/workflow_app/server/presentation/templates/index_defect_center.css`
  - 新增详情页卡片、证据左右分栏、时间线、状态 chip 与响应式布局样式，向原型图的视觉结构靠齐。
- `scripts/acceptance/run_acceptance_defect_center_browser.py`
  - 将慢接口 `process-task` 与 `review-task` 的请求超时提升到 `240s`，避免真实浏览器验收因为慢接口误判失败。

## 验证
- `python -m py_compile scripts/acceptance/run_acceptance_defect_center_browser.py` 通过。
- 缺陷中心官方浏览器验收通过：`.test/evidence/defect-center-browser/summary.json`
- 原型聚焦 smoke 通过：`.test/evidence/defect-center-prototype-smoke/summary.json`
- `test` 已部署到版本 `20260325-164619`：`.running/control/logs/test/deploy-20260325-164619.json`
- `test gate` 通过：`.running/control/reports/test-gate-20260325-164619.json`
- `http://127.0.0.1:8092/healthz` 返回 `{"ok": true, ...}`

## 关键产物
- `src/workflow_app/web_client/defect_center_state_helpers.js`
- `src/workflow_app/web_client/defect_center_render_runtime.js`
- `src/workflow_app/server/presentation/templates/index_defect_center.css`
- `scripts/acceptance/run_acceptance_defect_center_browser.py`
- `.test/evidence/defect-center-browser/screenshots/defect-main.png`
- `.test/evidence/defect-center-browser/screenshots/defect-dispute.png`
- `.test/evidence/defect-center-browser/screenshots/defect-review-input.png`

## Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: 用户对缺陷详情页同样要求严格按原型图收口，并继续坚持“先开发验证，再发布 test，prod 手动升级”。
- delta_validation: 后续请用户在 `test` 上重点验收顶部 `DTS` 头区、事实卡、原始上报分栏、补充输入区、任务引用和时间线的结构与观感；如还有偏差，再继续收口间距与字体。
