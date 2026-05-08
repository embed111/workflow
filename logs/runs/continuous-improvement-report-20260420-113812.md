# [持续迭代] workflow / 2026-04-20 10:58:00

## 判断
- `version_transition_decision=stay(V5)`。当前 active 版本仍是 `V5 / 高价值新功能与长期能力扩展`，生命周期继续保持在 `开发实现`，最高价值泳道仍是 `工程质量探测 / 发布边界收口`。
- 这轮我没有重复上一轮的 `assignment_core` 拆分，而是直接把 `loop_round_runtime.py` 里的 status-detail 能力/任务演进/基线投影视图抽到新的 `loop_round_status_detail_runtime.py`。`loop_round_runtime.py` 从 `1160` 行降到 `692` 行，`blocking_offender_count` 从 `15` 降到 `14`，Mandatory Gate 的第三个首批冻结对象已切换为 `src/workflow_app/server/services/runtime_upgrade_service.py`。
- 当前还不能切版，也不能推进 `test / prod candidate`。切版 blocker 仍是 `controller cadence closure` 缺 live finalize 消费证据、正向 `prod/live member task` 还未形成 `project_id/project_ref` 证据，以及 `V5-R5` 的 Mandatory Gate 仍为 false。

## 取舍
- 这轮我继续打 `V5-R5`，没有再做同质化 live smoke。因为当前主线 `running_task_count=1`、下一条 mainline 与 patrol 都仍是 `ready`，最值钱的动作是继续把 clean head 的强制门禁往下压。
- helper 这轮仍不强派：`workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 的 developer workspace 仍停在 `cec137`，相对 `code_root@efcd301` 处于 `diverged_or_unknown`；在旧 commit 上派新的工程治理主任务不划算。

## 下一动作
- 下一刀继续正面收口 `schedule_service.py / workflow_env_common.ps1 / runtime_upgrade_service.py`，把 Mandatory Gate 再往下压。
- 等 `line budget / workflow gate / runtime release gate` 进入下一阶段后，再部署 `test`、刷新 `prod candidate`，并重跑 supported live member-route proof。

## 推进性修改
- 新增 `.repository/pm-main/src/workflow_app/server/services/training_loop_service_parts/loop_round_status_detail_runtime.py`，把 training loop round 的 capability/tasks-evolution/baseline projection 和 `get_training_queue_status_detail()` 从主 part 里抽成独立 support module。
- 更新 `.repository/pm-main/src/workflow_app/server/services/training_loop_service_parts/manifest.json`，把新 part 纳入 `training_loop_service_parts` 装配。
- 新增 `.repository/pm-main/scripts/acceptance/verify_training_loop_round_runtime_split.py`，锁住“main part < 900 行 + support part < 1000 行 + manifest 挂载 + `enter-next-round / rollback-round-increment` 后 status-detail 仍通”的 contract。
- 更新 `.repository/pm-main/scripts/acceptance/workflow_gate_probe_registry.py`，把新 split probe 纳入 gate registry。
- 代码已提交并同步：`pm-main@efcd301` / `workflow_code@efcd301`。

## 验证
- `.repository/pm-main/.test/20260420-113519-342/report.md`：`verify_training_loop_round_runtime_split.py` 通过；`status-detail` 在默认、`enter-next-round`、`rollback-round-increment` 三条路径上都继续返回能力、任务演进和能力基线。
- `.repository/pm-main/.test/20260420-113533-140/report.md`：`check_workspace_line_budget.py --root .` 预期 fail-closed；`blocking_offender_count=14`，首批冻结对象已切到 `schedule_service.py / workflow_env_common.ps1 / runtime_upgrade_service.py`。
- `git -C .repository/pm-main log -1 --pretty=format:"%H %cI %s"` 与 `git -C ../workflow_code log -1 --pretty=format:"%H %cI %s"` 已一致为 `efcd301 2026-04-20T11:37:42+08:00 refactor(training): 拆分 loop round status detail 运行时以压低门禁 blocker`。
- `/healthz` 正常；`/api/status` 当前是 `running_task_count=1 / queued_task_count=2 / active_agent_count=1`；`/api/runtime-upgrade/status` 仍是 `candidate_version=current_version=20260419-180446 / candidate_is_newer=false / can_upgrade=false`。

## 当前版本需求更新
- `V5-R1`: `in_progress / 60% / 最近更新=2026-04-19T23:50:42+08:00 / eta=2026-04-21 / 未超时`。prod live member route 的负向证据已钉死，当前等待新 candidate 带上正向 `project_id/project_ref`。
- `V5-R2`: `in_progress / 35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`。继续保持 go/no-go 与 blocker 路由真相同步。
- `V5-R3`: `in_progress / 35% / 最近更新=2026-04-19T20:37:53+08:00 / eta=2026-04-21 / 未超时`。当前等待 controller/member 合同继续落到正式 runtime 字段。
- `V5-R4`: `in_progress / 96% / 最近更新=2026-04-19T23:50:42+08:00 / eta=2026-04-21 / 未超时`。prod baseline 仍未带上 member route 正向字段，下一次重检继续依赖新 candidate。
- `V5-R5`: `in_progress / 99% / 最近更新=2026-04-20T11:38:12+08:00 / eta=2026-04-21 / 未超时`。`loop_round_runtime.py` 已退出 first batch targets，强制门禁 blocker 从 `15` 继续压到 `14`。

## 发布边界与 Warning
- `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=efcd301 / push_block_reason=mandatory_gate_fail_closed / next_push_batch=schedule_service.py / workflow_env_common.ps1 / runtime_upgrade_service.py split + gate/acceptance`
- `pm-main` 相对外部 `origin` 仍是 `ahead 4`，`workflow_code` 相对外部 `origin` 仍是 `ahead 201`，但本轮发布边界判断继续以 `pm-main == ../workflow_code == efcd301` 为准。
- `candidate_version` 仍等于 `prod=20260419-180446`；这批能力尚未进入新的 `test / prod candidate`。
- `pm/daily-execution-history/2026-04-20.md` 仍缺失，因为今天的每日学习任务与真实学习报告尚未收口；我这轮没有伪造 completed 记录。

- preference_ref: state/user-preferences.md
- delta_observation: 你仍然要求我把交付正文写成“先判断、取舍和下一动作，再补必要证据”，不接受状态墙式回报。
- delta_validation: 下一轮 continuous-improvement-report 和 history 继续沿用先判断后证据的结构，不退回播报腔。

memory_ref: `.codex/memory/2026-04/2026-04-20.md`
