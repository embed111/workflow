# PM治理专项用例编号

## 使用说明
- 本文件用于维护 `workflow(pm)` 侧治理能力的正式专项用例编号。
- 当某条 PM 治理需求需要独立编号、独立验收和独立证据引用时，优先在这里登记，而不是继续借用无关模块的编号。
- 当前只收录已经落到代码与 acceptance 的编号；纯口头规划不进入本表。

## 用例列表

### `TC-PM-001`
- 绑定需求：`V2-R1` 每日任务自动执行与历史清理
- 目标：每日治理自动补档、最近 `7` 份保留清理，以及 `/api/status` / `/api/dashboard` 的治理状态暴露保持一致。
- 主要覆盖：
  - `pm/daily-execution-history/YYYY-MM-DD.md`
  - `pm/daily-learning-reports/YYYY-MM-DD/<agent_id>.md`
  - `.repository/pm-main/src/workflow_app/server/services/pm_daily_governance_service.py`
  - `.repository/pm-main/scripts/bin/refresh_pm_daily_governance.py`
  - `.repository/pm-main/scripts/acceptance/verify_pm_daily_governance_tc_pm_001.py`
- 通过标准：
  - 今日 daily 文件缺失时，可自动补出 `system_ops_check / learning_prompt / next` 骨架。
  - `daily-execution-history` 与 `daily-learning-reports` 都会按最近 `7` 份收口。
  - `/api/status` 与 `/api/dashboard` 都能返回 `pm_daily_governance_status`，并带出当前 daily 路径与学习报告目录。

### `TC-PM-002`
- 绑定需求：`V2-R1` 每日任务自动执行与历史清理
- 目标：helper 因 workspace 边界改走 `self-target delivery` 或仅在 `result_ref` 保留真实学习报告时，治理服务仍能识别这些交付并把内容投影回 `pm/daily-learning-reports/YYYY-MM-DD/<agent_id>.md`；若像 `workflow_ucdmate` 这类可选角色已经在当天通过真实交付进入正式协作口径，但尚未留下学习报告，也要把它继续保留在缺口列表里，而不是误报成 completed。
- 主要覆盖：
  - `.repository/pm-main/src/workflow_app/server/services/pm_daily_governance_service.py`
  - `.repository/pm-main/scripts/bin/refresh_pm_daily_governance.py`
  - `.repository/pm-main/scripts/acceptance/verify_pm_daily_governance_tc_pm_002.py`
  - `C:/work/J-Agents/.output/delivery/<agent_id>/*/DELIVERY_INFO.json`
  - `C:/work/J-Agents/.output/tasks/*/nodes/*.json`
  - `C:/work/J-Agents/.output/tasks/*/runs/*/result.json`
- 通过标准：
  - `pm_daily_governance_status` 会把已回流到 `self-target delivery` 或已保存在 `result_ref` 的 helper 学习报告计入有效覆盖，不再继续误判成 `missing_learning_reports`。
  - 执行 `refresh_pm_daily_governance.py` 时，会把这些真实 helper 报告投影回 `pm/daily-learning-reports/YYYY-MM-DD/<agent_id>.md`。
  - 当尚有未完成 helper 时，daily 状态保持 `in_progress`；只剩真实未回流对象才继续留在缺口列表里。
  - 当 `workflow_ucdmate` 这类已通过当日真实交付进入正式协作口径，但还没有对应学习报告时，daily 不能继续显示 `completed`，必须把它保留在 `missing_learning_reports`。

### `TC-PM-003`
- 绑定需求：`V2-R4` 7x24 主线治理动作轻量自动化
- 联动覆盖：`V2-R7` 需求点 -> 用例 -> 验收证据映射矩阵
- 目标：当 live `prod` 切到新的 current version 后，PM 侧的版本快照和 mainline/patrol 的 live 摘要都要有正式编号化回归，不再只靠 helper smoke 报告口头挂接。
- 主要覆盖：
  - `pm/PM当前版本计划.md`
  - `pm/versions/V2/版本计划.md`
  - `.repository/pm-main/scripts/acceptance/verify_pm_current_version_snapshot_refresh.py`
  - `.repository/pm-main/scripts/acceptance/verify_pm_current_version_snapshot_alignment.py`
  - `.repository/pm-main/scripts/acceptance/verify_schedule_live_result_summary.py`
  - `.repository/pm-main/scripts/acceptance/verify_pm_current_version_tc_pm_003.py`
- 通过标准：
  - live `prod` 切到新版本后，受支持的 current-version 快照刷新动作会把 `PM当前版本计划.md` 与版本计划里的 baseline / live status 一并追平，不再因为旧文案格式漏刷。
  - `PM当前版本计划.md` 与 `pm/versions/V2/版本计划.md` 的 `active_version / lane / lifecycle_stage / baseline` 快照保持一致。
  - `workflow gate` 已能通过 `TC-PM-003` 直接回归 mainline/patrol 的 live 摘要优先级，不再把旧的 `assigned agent already has running node` 暴露成当前结果，而是稳定显示 `待开始 / 进行中` 等 live 文案。
  - `R4` 的 current-version evidence 已在 PM 侧 gate 留下正式编号，不再只停在 `workflow_testmate` 的 smoke 资产里。

### `TC-PM-004`
- 绑定需求：`V2-R6` 需求总表与版本归属映射矩阵
- 联动覆盖：`V2-R7` 需求点 -> 用例 -> 验收证据映射矩阵
- 目标：`pm/versions/V2/需求映射与覆盖矩阵.md` 不能再只保证“28 行需求都在”，还要和当前 active baseline、`row 28` 的跨版本归属，以及 `R7` 的 current-version smoke 分层结论一起保持同步。
- 主要覆盖：
  - `pm/versions/V2/需求映射与覆盖矩阵.md`
  - `.repository/pm-main/scripts/acceptance/verify_active_version_requirements_matrix.py`
  - `.repository/pm-main/scripts/acceptance/verify_active_version_requirements_matrix_snapshot.py`
  - `.repository/pm-main/scripts/acceptance/verify_pm_current_version_matrix_tc_pm_004.py`
- 通过标准：
  - `需求映射与覆盖矩阵.md` 的 `version / baseline / updated_at` 会追平当前 active `V2` 真相，不再长期停在旧 baseline。
  - `row 28` 的跨版本治理说明已经正式吸收到 `V4-R3`，不再继续保留旧的 `V2-P0` 占位说法。
  - `V2-R7` 的矩阵行会同时保留“当前 live baseline smoke 证据”和“`test=8092` 仅属运行态数据缺口”的分层结论，避免把非 prod 信号误写成现网回退。

### `TC-PM-005`
- 绑定需求：`V2-R2` 版本排期与负责人视图
- 目标：把任务中心版本推进侧栏里的 owner 视图正式收口成可回归的 PM 工作面，并明确“版本详情继续内嵌，不再拆独立版本详情页”的产品决策。
- 主要覆盖：
  - `.repository/pm-main/src/workflow_app/server/services/pm_version_board_service.py`
  - `.repository/pm-main/src/workflow_app/web_client/assignment_center_render_runtime.js`
  - `.repository/pm-main/scripts/acceptance/verify_pm_version_board_view.py`
  - `.repository/pm-main/scripts/acceptance/verify_assignment_version_board_filters.js`
- 通过标准：
  - `pm_version_board` 的 owner 行会直接给出 `requirement_count / active_requirement_ids / status_counts / next_eta / collaborators`，不再只剩一个轻量计数壳。
  - 任务中心版本推进侧栏会明确显示“版本详情继续内嵌在任务中心版本推进侧栏，不再拆独立版本详情页；负责人焦点卡就是默认细粒度工作面。”，把版本详情页扩面判断正式冻结。
  - owner 筛选后的负责人焦点卡会直接暴露 `状态分布 / 最近 ETA / 当前 active 需求 / 协作方`，不需要再靠独立详情页补第二套工作面。
  - `/api/status` 与 `/api/dashboard` 返回的 `pm_version_board` 都会带出同一份 `detail_view` 决策与 owner 摘要，前后端真相保持一致。
