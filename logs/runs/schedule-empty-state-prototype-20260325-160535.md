# 定时任务空态按原型图收口 - 2026-03-25 16:05:35

## 背景
- 用户反馈：定时任务为空时页面展示有问题，要求按原型图收口。
- 本轮目标：修复空列表后的错误状态残留，并把空态布局改成与原型图一致的双栏占位表达。

## 代码改动
- 修复 `refreshSchedulePlans` 在计划列表清空后未回收 `state.scheduleDetail`，避免右侧详情残留旧计划。
- 重写定时任务空态渲染：
  - 左侧列表空态改为引导卡片，保留原型图式的信息层级与新建入口。
  - 右侧详情空态改为结构化占位，保留“计划详情 / 发起内容 / 触发规则 / 未来触发 / 最近结果 / 关联实例”分区。
  - 日历右侧空态改为结构化占位，保留“发起内容预览 / 当月计划 / 实际结果”分区。
- 同步更新定时任务浏览器探针，兼容新空态 DOM，不再依赖旧版 `.schedule-empty` 单卡片结构。

## 验证
- `node` 语法检查通过：
  - `src/workflow_app/web_client/schedule_center_render_runtime.js`
  - `src/workflow_app/web_client/schedule_center_state_helpers.js`
  - `src/workflow_app/web_client/schedule_center_events.js`
- 隔离运行时轻量浏览器回归：
  - 创建 1 条计划后删除，确认删除后回到空态，不再残留旧详情。
  - 空态浏览器探针 `empty_state` 通过：`.test/evidence/schedule-center-empty-smoke/screenshots/empty_after_delete.probe.json`
  - 列表视角空态截图已落盘：`.test/evidence/schedule-center-empty-smoke/screenshots/empty_list_after_delete.png`
  - 日历视角空态截图已落盘：`.test/evidence/schedule-center-empty-smoke/screenshots/empty_after_delete.png`

## 关键产物
- `src/workflow_app/web_client/schedule_center_state_helpers.js`
- `src/workflow_app/web_client/schedule_center_render_runtime.js`
- `src/workflow_app/web_client/schedule_center_events.js`
- `src/workflow_app/server/presentation/templates/index_schedule_center.css`
- `.test/evidence/schedule-center-empty-smoke/screenshots/empty_after_delete.png`
- `.test/evidence/schedule-center-empty-smoke/screenshots/empty_after_delete.probe.json`
- `.test/evidence/schedule-center-empty-smoke/screenshots/empty_list_after_delete.png`
