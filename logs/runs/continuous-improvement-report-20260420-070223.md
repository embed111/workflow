**判断**
- `version_transition_decision=stay(V5)`。我这轮把主泳道继续放在 `工程质量探测 / 发布边界收口 / V5-R5`，没有重复上一轮的 `task_artifact_store_core.py` 切片，而是直接把 `defect_service.py` 的查询/队列/task-ref enrich 面抽成 `defect_service_query_runtime.py`，并顺手修掉 defect task chain 里 `_assignment_build_node_record()` 的 `project_id/project_ref` 旧签名漂移。
- 这刀让 `defect_service.py` 从 `1294` 行降到 `796` 行，已经退出 Mandatory Gate 首批冻结对象；最新 `blocking_offender_count=27`，新的首批冻结对象是 `schedule_service.py / workflow_env_common.ps1 / src/workflow_app/server/services/assignment_service_parts/task_artifact_store_run_runtime.py`。
- 下一步我优先继续切这三个 blocker；等 `line budget / workflow gate / runtime release gate` 进入下一阶段后，再部署 `test`、刷新 `prod candidate`，然后重跑 supported live member-route proof。

**证据**
- live 真相：`/healthz` 正常；`/api/status` 当前是 `running_task_count=1 / queued_task_count=1 / active_agent_count=1`，主线 `node-sti-20260420-053a4658` 仍在 running，下一条 mainline `node-sti-20260420-2d9fbe93` 已 ready；保底巡检 schedule 仍启用，最近一次命中为 `2026-04-20T07:00:00+08:00`。
- 发布边界：`root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=d5b5436 / push_block_reason=mandatory_gate_fail_closed / next_push_batch=schedule_service.py / workflow_env_common.ps1 / task_artifact_store_run_runtime split + gate/acceptance`。
- 验证：
  - 红灯基线：`.repository/pm-main/.test/20260420-064849-363/report.md`
  - split probe 绿灯：`.repository/pm-main/.test/20260420-065508-856/report.md`
  - defect query runtime contract 绿灯：`.repository/pm-main/.test/20260420-065929-824/report.md`
  - `py_compile` 绿灯：`.repository/pm-main/.test/20260420-065941-119/report.md`
  - 最新 `line budget`：`.repository/pm-main/.test/20260420-065950-393/report.md`
  - 参考 warning：`.repository/pm-main/.test/20260420-065629-850/report.md`

**快照补记**
- preference_ref: `state/user-preferences.md`
- delta_observation: 你仍然要我先给判断、取舍和下一动作，再补必要证据；在 7x24 主线里，如果当前最高价值是 Mandatory Gate 收口，我不应该机械重复 live probe 或状态播报。
- delta_validation: 下一轮继续保持“先挑最高价值 blocker 再切最小可验证代码批次”的节奏；只有当 `line budget / gate` 足够接近转绿时，才把注意力切回 `test/prod candidate` 与 live member-route 正向证据。
