# 缺陷标题栏总开关与连续串行建单验收 20260327-101330

- topic: 缺陷记录标题栏总开关与连续解决缺陷收口
- started_at: 2026-03-27T10:02:44+08:00
- finished_at: 2026-03-27T10:13:30+08:00
- workspace: `C:\work\J-Agents\workflow`
- candidate_version: `20260327-101259`

## 结论
- `按顺序创建任务` 总开关已从详情上方独立条带移到左侧 `缺陷记录` 标题栏右侧，且页面不再保留旧条带。
- 右侧详情区已补为轻量 `顺序建单摘要`，固定展示当前主动处理缺陷、下一条待建单缺陷和串行规则说明。
- 总开关开启后会立即推进排序首条缺陷；上一条进入 `已解决` 或 `已关闭` 后，会继续自动推进下一条，直到队列清空。
- 全过程始终只有 1 条缺陷占用主动处理位，且所有处理/复核链仍统一挂到 `任务中心全局主图`。

## 代码落点
- 标题栏总开关渲染：`src/workflow_app/server/presentation/templates/index.html`
- 总开关样式与摘要卡样式：`src/workflow_app/server/presentation/templates/index_defect_center.css`
- 总开关状态渲染与顺序建单摘要：`src/workflow_app/web_client/defect_center_render_runtime.js`
- 浏览器探针与布局/串行验收：`src/workflow_app/web_client/defect_center_events.js`
- 自动推进触发与接口封装：`src/workflow_app/server/api/defects.py`
- 单主动处理位与队列真相源：`src/workflow_app/server/services/defect_service.py`

## 关键证据
### 1. 标题栏存在独立总开关，详情显示顺序建单摘要
- 浏览器 summary:
  - `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\summary.json`
- 关闭态截图:
  - `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\screenshots\queue-off.png`
- 开启态截图:
  - `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\screenshots\queue-on.png`
- 探针字段:
  - `queue_toggle_in_title=true`
  - `legacy_queue_strip_present=false`
  - `queue_summary_visible=true`

### 2. 开启后立即推进首条缺陷
- API:
  - `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\api\queue-mode-on.json`
  - `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\api\list-queue-on.json`
- 结果:
  - `active_report_id=dr-20260327-86ea607be4`
  - `next_report_id=dr-20260327-3fa591affa`
  - `candidate_total=4`

### 3. 上一条退出主动处理位后自动推进下一条
- 首条解决后:
  - `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\api\resolve-head.json`
  - `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\api\list-after-head-resolved.json`
- 第二条解决后:
  - `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\api\resolve-second.json`
  - `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\api\list-after-second-resolved.json`
- 第三条解决后:
  - `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\api\resolve-third.json`
  - `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\api\list-after-third-resolved.json`
- 页面截图:
  - `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\screenshots\queue-active.png`
  - `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\screenshots\queue-advanced.png`

### 4. 全程单主动处理位，并最终排空队列
- 队列排空:
  - `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\api\close-dispute.json`
  - `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\api\list-final-all.json`
  - `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\screenshots\queue-drained.png`
- 结果:
  - `active_report_id=''`
  - `next_report_id=''`
  - `candidate_total=0`
- 单主动位断言来自每次 `/api/defects?status=all` 返回的 `queue.active_report_id` 与列表 `queue_mode=active` 数量校验，浏览器脚本已逐步断言。

### 5. 全局主图、优先级真相源与幂等未回退
- 浏览器 summary:
  - `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\summary.json`
- 幂等/优先级回归 summary:
  - `C:\work\J-Agents\workflow\.test\evidence\defect-priority-truth-and-idempotency\summary.json`
- 结果:
  - 所有处理/复核任务共用 `ticket_id=asg-20260327-101045-bca841`
  - `P0/P2` 节点优先级与缺陷 `task_priority` 保持一致
  - 历史重复图被删除，仅保留全局主图

## 验证
- `node -e "const fs=require('fs'); new Function(fs.readFileSync('src/workflow_app/web_client/defect_center_render_runtime.js','utf8')); new Function(fs.readFileSync('src/workflow_app/web_client/defect_center_events.js','utf8')); console.log('js-ok')"`
- `python -m py_compile src/workflow_app/server/api/defects.py scripts/acceptance/run_acceptance_defect_center_browser.py scripts/acceptance/run_acceptance_defect_priority_truth_and_idempotency.py`
- `python scripts/acceptance/run_acceptance_defect_center_browser.py --root .`
- `python scripts/acceptance/run_acceptance_defect_priority_truth_and_idempotency.py --root .`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/deploy_workflow_env.ps1 -Environment test`

## 发布结果
- `test` 候选:
  - `C:\work\J-Agents\workflow\.running\control\envs\test.json`
- 部署记录:
  - `C:\work\J-Agents\workflow\.running\control\logs\test\deploy-20260327-101259.json`
- 门禁报告:
  - `C:\work\J-Agents\workflow\.running\control\reports\test-gate-20260327-101259.json`
