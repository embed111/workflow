# Defect Records Complete Display 20260325-133653

- time: `2026-03-25T13:36:53+08:00`
- scope: `缺陷记录展示不全修复 + 开发态验收 + test 发布`
- source_root: `C:\work\J-Agents\workflow`
- preference_ref: `state/user-preferences.md`
- delta_observation: 用户反馈当前缺陷记录展示不全，需要确保缺陷中心不是只显示一部分记录或误报总数。
- delta_validation: 本轮先在开发态完成分页/搜索验证与真实浏览器验收，再发布到 `test` 并恢复 `test` 在线，不触碰 `prod`。

## Root Cause

- 缺陷列表接口与前端请求都写死了 `limit=200`，记录超过 200 条时只会显示最近一段。
- 关键词搜索是在取回这 200 条之后才做前端/服务端二次过滤，导致更早但命中的记录也可能搜不到。
- 页面顶部文案直接把“已加载条数”写成“总记录数”，造成“看起来像全量，实际被截断”的误导。

## Result

- 缺陷列表接口已支持 `offset` 分页，并返回 `total / returned / next_offset / has_more`。
- 关键词过滤已前移到 SQL 查询层，避免先截断再搜索。
- 缺陷中心列表区已支持“加载更多”，顶部文案改为真实的 `已加载 X / 总数 Y`。
- 当前修复已发布到 `test` 版本 `20260325-133552`，并重新启动在线服务。

## Validation

- 后端语法检查：
  - `python -m py_compile src/workflow_app/server/api/defects.py src/workflow_app/server/services/defect_service.py`
- 分页/搜索回归：
  - 临时 SQLite 注入 250 条缺陷记录后，`offset=0/100/200` 分页分别返回 `100/100/50`
  - 关键词 `UNIQUE-KEYWORD` 可以命中超出首页窗口之外的旧记录
- 浏览器真实验收：
  - `.test/evidence/defect-center-browser/summary.json` 中 `ok=true`
- `test` 发布：
  - `.running/control/logs/test/deploy-20260325-133552.json` 显示 `result=success`
  - `.running/control/reports/test-gate-20260325-133552.json` 显示 `result=passed`
  - `http://127.0.0.1:8092/healthz` 返回 `ok=true`

## Artifacts

- 后端接口：`src/workflow_app/server/api/defects.py`
- 缺陷列表查询：`src/workflow_app/server/services/defect_service.py`
- 缺陷中心状态：`src/workflow_app/web_client/app_status_and_icon_utils.js`
- 缺陷中心渲染：`src/workflow_app/web_client/defect_center_render_runtime.js`
- 缺陷中心事件：`src/workflow_app/web_client/defect_center_events.js`
- 缺陷中心模板：`src/workflow_app/server/presentation/templates/index.html`
- 缺陷中心样式：`src/workflow_app/server/presentation/templates/index_defect_center.css`
- 浏览器验收证据：`.test/evidence/defect-center-browser/summary.json`
- `test` 部署日志：`.running/control/logs/test/deploy-20260325-133552.json`
- `test` 门禁报告：`.running/control/reports/test-gate-20260325-133552.json`
- `prod` 候选文件：`.running/control/prod-candidate.json`

## Notes

- 为发布新版本，仅停止并替换了 `test` 环境进程，随后已恢复在线。
- 本轮没有直接停止、重启或覆盖 `prod`。
- `test gate` 仍有 line budget advisory / refactor trigger 提示，但硬门禁通过，不阻塞本次发布。
