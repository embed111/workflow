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
1. snapshot_updated_at: `2026-05-21T19:05:00+08:00`
2. active 版本仍是 `V13`
3. 当前版本标题为 `全仓逻辑边界与冗余实现根治`
4. 当前最高价值泳道为 `7x24 连续性 / 发布边界 / 工程质量探测`
5. 生命周期阶段为 `开发实现 -> 基于基线测试 -> 验收 -> 发布候选刷新 -> 发布边界阻塞复核`
6. baseline 已随正式生产升级对齐为 `prod=20260521-160216`
7. runtime_upgrade: `current=20260521-160216 / candidate=20260521-185742 / candidate_is_newer=true / running_task_count=2 / can_upgrade=false / ghost=false / continuous_gap=false`
8. 当前版本判断: `version_transition_decision=stay / switch_blockers=V14 next_activation_ready=false；V13 exit gates 未关闭；CODE_QUALITY_PIPELINE 仍 warn；candidate=20260521-185742 尚未正式 apply；runtime running_task_count=2；R6/R8 未完成`
9. 当前恢复优先级: `本轮消费质量流水线 rank1=src/workflow_app/server/services/assignment_service_parts/node_lifecycle_actions.py:415(override_assignment_node_status)：把旧 DB override 状态覆盖逻辑中的 running/static status guard 拆成具名 helper。pm-main=b99aeb8；workflow_code=8f3a8a0；test gate passed 并刷新 candidate=20260521-185742。质量流水线保持 warn / failure_count=0 / warning_count=67，旧 rank1 已出队，新 rank1=src/workflow_app/server/services/training_loop_service_parts/loop_round_status_detail_runtime.py:118(_build_training_loop_capabilities)。prod live 回读 ghost=false / continuous_gap=false；正式 prod apply 仍受 running_task_count=2 阻塞。下一动作是在当前 workflow 节点结束后回读 prod supervisor 是否 apply candidate=20260521-185742；若 running gate 清零则优先等待/触发受支持 idle apply；若仍未 apply 且 live 继续绿灯，再处理新质量 rank1=training_loop capabilities。`
10. history_ref: `pm/versions/V13/history/2026-05/2026-05-21.md`

