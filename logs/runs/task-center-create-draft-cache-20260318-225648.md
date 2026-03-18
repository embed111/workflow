# 运行记录 - 任务中心创建任务草稿缓存

- timestamp: 2026-03-18T22:56:48+08:00
- request: 点击创建任务时保留之前的编辑缓存
- runtime_environment: prod
- preference_ref: state/user-preferences.md

## 影响代码

- `src/workflow_app/web_client/app_status_and_icon_utils.js`
- `src/workflow_app/web_client/assignment_center_state_helpers.js`
- `src/workflow_app/web_client/assignment_center_render_runtime.js`
- `src/workflow_app/web_client/assignment_center_events.js`
- `.running/prod/src/workflow_app/web_client/app_status_and_icon_utils.js`
- `.running/prod/src/workflow_app/web_client/assignment_center_state_helpers.js`
- `.running/prod/src/workflow_app/web_client/assignment_center_render_runtime.js`
- `.running/prod/src/workflow_app/web_client/assignment_center_events.js`

## 实现说明

- 新增 `assignmentCreateDraftCacheKey=workflow.p0.assignment.createDraft`
- 创建任务抽屉改为：关闭时同步并保留草稿，不再直接重置表单
- 草稿同时保存在内存态和 `localStorage`，支持误关抽屉后重开回填，也支持页面刷新后恢复
- `提交创建` 成功后才清空草稿与表单状态
- 补充内部 probe：`assignment_probe_case=draft_persist`，自动执行“打开 -> 输入 -> 关闭 -> 重开 -> 校验回填”

## 验证证据

- Smoke DOM: `logs/runs/assignment-draft-smoke-20260318-1.html`
- Probe URL: `http://127.0.0.1:8090/?assignment_probe=1&assignment_probe_case=draft_persist&assignment_probe_delay_ms=900`
- Probe DOM: `logs/runs/assignment-draft-persist-probe-20260318/probe.html`
- Probe Result:
  - `data-pass=1`
  - `draft_cache_present=true`
  - `draft_node_name=缓存保留验证任务`
  - `draft_goal=关闭抽屉后再次打开，之前编辑内容应自动回填。`
  - `draft_priority=P2`
  - `draft_upstream_search=cache-check`

## 备注

- 当前缓存作用域为当前页面 origin 下的任务中心创建任务草稿
- 若用户正式提交创建成功，草稿会按预期清空，避免旧内容污染下一次新建
