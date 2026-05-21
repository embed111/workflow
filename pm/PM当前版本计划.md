# PM当前版本计划

## 1. 文档定位
- 本文件是当前活跃版本的自动引用文件，不再单独承载当前版本的完整排期正文。
- 当前版本的完整计划统一维护在对应版本目录下的 `版本计划.md` 中。
- 当前版本的日级推进与现场更新统一维护在对应版本目录下的 `history/` 中。

## 2. 当前活跃版本
- active_version: `V13`
- active_version_title: `全仓逻辑边界与冗余实现根治`
- active_version_file: `pm/versions/V13/版本计划.md`
- version_history_root: `pm/versions/V13/history/`

## 3. 版本目录导航
- 全量版本目录、状态与路径索引统一看：`pm/PM版本目录导航.md`

## 4. 自动引用规则
1. 先读取本文件。
2. 再读取 `active_version_file` 指向的版本计划文件。
3. 再读取当前版本目录下的：
   - `需求台账.md`
   - `阶段看板.md`
   - `迭代甘特图.md`
4. 当前版本的具体需求点、责任人、进入前提、退出门槛，以该版本目录下的 `版本计划.md` 为准。
5. 当前版本的阶段、下一门禁、计划窗口和里程碑，以该版本目录下的 `需求台账.md / 阶段看板.md / 迭代甘特图.md` 为准。
6. 当前版本的日级推进、后移和排期判断，以该版本目录下的 `history/YYYY-MM/YYYY-MM-DD.md` 为准。
7. 当前活跃版本切换时，优先更新本文件中的：
   - `active_version`
   - `active_version_title`
   - `active_version_file`
   - `version_history_root`
## 5. 当前状态快照
1. snapshot_updated_at: `2026-05-21T08:31:00+08:00`
2. active 版本仍是 `V13`
3. 当前版本标题为 `全仓逻辑边界与冗余实现根治`
4. 当前最高价值泳道为 `7x24 连续性 / 发布边界 / 工程质量探测`
5. 生命周期阶段为 `开发实现 -> 基于基线测试 -> 验收 -> 发布候选刷新 -> 发布边界阻塞复核`
6. baseline 继续对齐为 `prod=20260520-233627`
7. runtime_upgrade: `current=20260520-233627 / candidate=20260521-082506 / candidate_is_newer=true / running_task_count=2 / can_upgrade=false / ghost=false / continuous_gap=false`
8. 当前版本判断: `version_transition_decision=stay / switch_blockers=V14 next_activation_ready=false；V13 exit gates 未关闭；CODE_QUALITY_PIPELINE 仍 warn；candidate=20260521-082506 尚未正式 apply；runtime running_task_count=2；R6/R8 未完成`
9. 当前恢复优先级: `本轮完成 release boundary snapshot 质量首债：将 collect_release_boundary_snapshot 的默认 payload 构造抽到 _initial_release_boundary_snapshot；提交 pm-main=9cb0009，同步 workflow_code=4241be4，并部署 test/刷新 candidate=20260521-082506。质量流水线从 warning_count=72 降到 71，新 rank1=training_plan_service_parts/queue_management.py:297。下一动作是在当前 workflow 与 novel_project_pm 节点结束后回读 prod supervisor 是否 apply candidate=20260521-082506；若 running gate 清零则优先等待/触发受支持 idle apply；若仍未 apply 且 live 继续绿灯，处理新质量 rank1。`
10. history_ref: `pm/versions/V13/history/2026-05/2026-05-21.md`

