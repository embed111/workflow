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
1. snapshot_updated_at: `2026-05-20T06:30:00+08:00`
2. active 版本仍是 `V13`
3. 当前版本标题为 `全仓逻辑边界与冗余实现根治`
4. 当前最高价值泳道为 `工程质量探测 / 架构优化 / 发布推进 / 生产可用性`
5. 生命周期阶段为 `开发实现 -> 基于基线测试 -> 验收 -> 发布候选刷新 -> 发布边界阻塞复核`
6. baseline 继续对齐为 `prod=20260520-053759`
7. runtime_upgrade: `candidate=20260520-062233 / candidate_is_newer=true / running_task_count=2 / can_upgrade=false / ghost=false / continuous_gap=false`
8. 当前版本判断: `version_transition_decision=stay / switch_blockers=V14 next_activation_ready=false；V13 exit gates 未关闭；CODE_QUALITY_PIPELINE 仍 warn；candidate=20260520-062233 尚未正式 apply；当前 workflow 与 novel_project_pm 节点仍 running；R6/R8 未完成`
9. 当前恢复优先级: `本轮已消费质量 warn rank1=verify_assignment_terminal_result_recovery_without_finalize.py:31(main)，pm-main=a0c45c9 / workflow_code=d3236dc，test/prod candidate 刷新到 20260520-062233；prod current 已确认追到 20260520-053759，live ghost=false / continuous_gap=false；正式 apply 继续交给 prod supervisor idle watcher；下一轮优先确认 candidate 是否 idle apply，再处理新 rank1=verify_legacy_task_crud_route_dispatch.py:24(main) 或恢复 V13-R6/R8`
10. history_ref: `pm/versions/V13/history/2026-05/2026-05-20.md`

