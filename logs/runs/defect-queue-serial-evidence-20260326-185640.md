# 缺陷总开关串行建单验收证据 20260326-185640

- topic: 缺陷总开关开启态下串行建单补充验收
- generated_at: 2026-03-26T18:56:40+08:00
- workspace: `C:\work\J-Agents\workflow`
- evidence_scope: `local/test isolated runtime`
- browser_acceptance_summary: `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\summary.json`

## 验收口径
- 所有缺陷共用一个总开关。
- 同一时刻只允许一个主动处理位。
- 上一条缺陷未解决前，不得给下一条缺陷建任务。
- 全局主图和单缺陷幂等只是上述规则下的实现方式，不替代串行建单规则本身。

## 对应证据
### 1. 总开关开启后，全队列进入串行模式
- API: `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\api\queue-mode-on.json`
  - `queue.enabled=true`
  - `queue.active_display_id=DTS-00004`
  - `queue.next_display_id=DTS-00002`
- 页面截图: `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\screenshots\queue-on.png`
- 页面探针: `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\screenshots\queue-on.probe.json`
  - `queue_toggle_text=按顺序创建任务：开启`
  - 当前选中的 `DTS-00002` 被标记为 `queue_mode_text=下一条待建单`
  - `process_btn_visible=false`

### 2. 同一时刻只允许一个主动处理位
- API: `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\api\head-detail-active.json`
  - `report.display_id=DTS-00004`
  - `report.queue_mode=active`
  - `report.queue_mode_text=当前主动处理位`
  - `task_ref_total=3`
  - 处理链写入 `ticket_id=asg-20260326-185457-fcdcc7`
- 页面截图: `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\screenshots\queue-active.png`
- 页面探针: `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\screenshots\queue-active.probe.json`
  - `queue_active_display_id=DTS-00004`
  - `queue_next_display_id=DTS-00002`
  - `selected_queue_mode_text=当前主动处理位`

### 3. 上一条未解决前，下一条不得建任务
- API: `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\api\second-detail-before-advance.json`
  - `report.display_id=DTS-00002`
  - `report.queue_mode=next`
  - `task_ref_total=0`
- API: `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\api\manual-process-blocked.json`
  - `status=409`
  - `code=defect_queue_gate_blocked`
  - `reason=active_slot_busy`
  - `active_report_id=dr-20260326-e210a799fa`
- 页面截图: `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\screenshots\queue-on.png`
- 页面探针: `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\screenshots\queue-on.probe.json`
  - `selected_queue_mode_text=下一条待建单`
  - `task_ref_total=0`
  - `process_btn_visible=false`

### 4. 上一条解决后，主动处理位才推进到下一条
- API: `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\api\resolve-head.json`
- API: `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\api\second-detail-active.json`
  - `report.display_id=DTS-00002`
  - `report.queue_mode=active`
  - `task_ref_total=3`
  - `history` 中新增 `已在任务中心创建处理任务`
  - 新建任务仍写入同一总图 `ticket_id=asg-20260326-185457-fcdcc7`
- 页面截图: `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\screenshots\queue-advanced.png`
- 页面探针: `C:\work\J-Agents\workflow\.test\evidence\defect-center-browser\screenshots\queue-advanced.probe.json`
  - `queue_active_display_id=DTS-00002`
  - `queue_next_display_id=DTS-00003`

## 结论
- 当前验收结果已覆盖“总开关开启态下串行建单”的一层规则。
- `任务中心全局主图` 与单缺陷 `external_request_id` 幂等，当前只是串行建单规则生效后的具体落地形式：
  - 主动处理位唯一；
  - 下一条在上一条未解决前无任务引用、按钮不可触发、手动建单被后端拒绝；
  - 只有上一条完成后，主动处理位和建单资格才推进到下一条。
