# workflow 持续迭代报告

- updated_at: `2026-04-11T22:49:27+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260411-ed474dee`
- active_version: `V1`
- task_package: `V1-P5`
- lane: `架构优化`
- lifecycle_stage: `变更控制`
- baseline: `prod=20260411-214605`
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`

## 本轮结论
- 我确认 `pm-main / ../workflow_code` 继续 `clean_synced` 到 `ea7291e`，当前 release boundary 仍然干净。
- 我识别出 `workflow_devmate / workflow_bugmate / workflow_testmate / workflow_qualitymate` 的 developer workspace refresh 真相漂到了 `origin/main=7a54432`，没有对齐本机根仓 `ea7291e`；随后我按受支持治理动作把四个工作区全部 `ff-only` 快进回本机 `../workflow_code/main`，并修正了 `state/developer-workspaces.json`。
- 我新挂并派发了 `node-20260411-224609-cf4f85 / V1-P5 升级drain窗口与新派发分流最小实现` 给 `workflow_devmate`，当前对应 run 为 `arun-20260411-224618-f92c33`，`V1-P5` 已从“等待窗口观察”进入真实执行。
- 当前 live `prod` 仍是 `20260411-214605`，更高 `candidate=20260411-220013` 继续被 `running_tasks_present` 卡住；但这轮的重点已经从被动等空窗切回 `V1-P5` 的实现推进。

## 根仓同步快照
- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `push_block_reason=-`
- `next_push_batch=待切批`
- 当前工作区：`pm-main`
- `workspace_head=code_root_head=ea7291e`
- helper developer workspace 实际 `HEAD`：`workflow_devmate / workflow_bugmate / workflow_testmate / workflow_qualitymate = ea7291e`
- 说明：`pm-main / ../workflow_code` 相对 `origin/main` 仍是 `ahead 10`，这里只继续作为上游参考，不构成本轮阻塞。

## live 现场
- `prod current_version=20260411-214605`
- `candidate_version=20260411-220013`
- `candidate_is_newer=true`
- `/api/runtime-upgrade/status`：`running_task_count=2 / blocking_reason=running_tasks_present / can_upgrade=false`
- 当前真实 running：
  - `workflow`: `node-sti-20260411-ed474dee / arun-20260411-222846-25f177`
  - `workflow_devmate`: `node-20260411-224609-cf4f85 / arun-20260411-224618-f92c33`
- 当前 ready：
  - `workflow`: `node-sti-20260411-18e25087 / [持续迭代] workflow / 2026-04-11 22:44:00`
- 当前任务图真相：`2 running / 1 ready / 6 pending / 12 failed / 3 blocked`
- 当前 future 出口：
  - 保底：`pm持续唤醒 - workflow 主线巡检 -> 2026-04-11T23:27:00+08:00`
- 当前 `/api/status.pm_version_status.baseline` 仍显示旧脏值 `收成可复用读链。 2.`；这不是计划正文又漂了，而是 live `prod` 还没拿到 `ea7291e` 里的 baseline 解析修正。
- 当前 `/api/status.truth_mismatch_count=1`，仍表现为 `active_version_mismatch(actual=disabled, expected=V1)`。
- 当前 `/api/runtime-upgrade/status.last_action` 仍停在旧的 `watchdog_restart -> 20260411-093051`；live 版本判断仍以 `current_version=20260411-214605`、`.running/control/envs/prod.json` 与 `.running/control/instances/prod.json` 为准。

## 本轮动作
1. 我按读链重读了治理、经验、SOUL/USER/MEMORY、全局/月度/今日日记，并确认当前任务仍服务于 `V1`。
2. 我核了 `pm-main / ../workflow_code` 的 Git 真相，确认当前没有 dirty/ahead/untracked 异常需要进入发布边界收口模式。
3. 我检查了 `/healthz`、`/api/status`、`/api/runtime-upgrade/status`、全局任务图和当前主线 run 文件，确认 live 现场已经变成 `workflow running + workflow_devmate running + workflow ready`。
4. 我先用受支持的 `manage_developer_workspace.py bootstrap --developer-id <helper>` 刷新四个 helper 工作区，再发现它们被对齐到 `origin/main=7a54432`。
5. 我随后改用受支持的本机根仓收口动作：在四个 helper 工作区分别执行 `git pull --ff-only D:/code/AI/J-Agents/workflow_code main`，把实际工作树拉回 `ea7291e`，并同步修正 `state/developer-workspaces.json`。
6. 我通过 UTF-8 JSON 调用 `POST /api/assignments/asg-20260327-223335-b79f27/nodes` 和 `POST /api/assignments/asg-20260327-223335-b79f27/dispatch-next`，把 `V1-P5` 最小实现切片挂给并派发给了 `workflow_devmate`。
7. 我把最新有效快照回写到了 `docs/workflow/governance/PM版本推进计划.md`、`docs/workflow/governance/pm-version-live/2026-04/现场更新总览.md`，并补记了今日日记与经验卡。

## 验证证据
- `git -C .repository/pm-main status --short --branch`
- `git -C .repository/pm-main rev-parse --short HEAD`
- `git -C ../workflow_code rev-parse --short HEAD`
- `git -C .repository/workflow_devmate rev-parse --short HEAD`
- `git -C .repository/workflow_bugmate rev-parse --short HEAD`
- `git -C .repository/workflow_testmate rev-parse --short HEAD`
- `git -C .repository/workflow_qualitymate rev-parse --short HEAD`
- `Invoke-RestMethod 'http://127.0.0.1:8090/healthz'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/graph'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-ed474dee'`
- `python ../workflow_code/scripts/manage_developer_workspace.py --root .running/control/runtime/prod --workspace-root D:/code/AI/J-Agents bootstrap --developer-id workflow_devmate`
- `python ../workflow_code/scripts/manage_developer_workspace.py --root .running/control/runtime/prod --workspace-root D:/code/AI/J-Agents bootstrap --developer-id workflow_bugmate`
- `python ../workflow_code/scripts/manage_developer_workspace.py --root .running/control/runtime/prod --workspace-root D:/code/AI/J-Agents bootstrap --developer-id workflow_testmate`
- `python ../workflow_code/scripts/manage_developer_workspace.py --root .running/control/runtime/prod --workspace-root D:/code/AI/J-Agents bootstrap --developer-id workflow_qualitymate`
- `git -C .repository/workflow_devmate pull --ff-only D:/code/AI/J-Agents/workflow_code main`
- `git -C .repository/workflow_bugmate pull --ff-only D:/code/AI/J-Agents/workflow_code main`
- `git -C .repository/workflow_testmate pull --ff-only D:/code/AI/J-Agents/workflow_code main`
- `git -C .repository/workflow_qualitymate pull --ff-only D:/code/AI/J-Agents/workflow_code main`
- `POST /api/assignments/asg-20260327-223335-b79f27/nodes`
- `POST /api/assignments/asg-20260327-223335-b79f27/dispatch-next`

## baseline 与变更控制
- 本轮 baseline 未变，继续沿用：`prod=20260411-214605`
- 本轮把最高价值泳道切回 `架构优化`，生命周期阶段切回 `变更控制`
- 本轮没有新增 `pm-main` 代码实现，也没有执行 `/api/runtime-upgrade/apply`
- 当前新增的变更控制内容是：helper developer workspace 必须以本机 `../workflow_code/main` 为真相源，不能只停在 `origin/main`

## 协作与下一步
- 主线 next：
  - 当前 running：`node-sti-20260411-ed474dee / arun-20260411-222846-25f177`
  - 下一条主线：`node-sti-20260411-18e25087` 已 ready，等待当前 `workflow` running 释放后接棒
- 保底 next：`2026-04-11T23:27:00+08:00`
- 升级 next：
  - 若当前 `workflow / workflow_devmate` 两条 running 收尾后仍未自动 apply `220013`，下一轮优先验证 `prod supervisor / idle watcher`
  - 若 `220013` 已切入现网，下一轮优先复核 `/api/status.pm_version_status.baseline` 是否恢复正常，并再决定 baseline 是否切到 `prod=20260411-220013`
- 实现 next：
  - 等 `workflow_devmate` 回传 `V1-P5` 的最小 drain / dispatch 分流切片，再优先沿它做 release boundary / 验证 / candidate 闭环

## Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: helper developer workspace refresh 当前可能只对齐到 `origin/main`，而不是本机 `../workflow_code/main`；本轮已用本机根仓 `ff-only` 收口并修正注册表，同时把 `V1-P5` 续挂给 `workflow_devmate`
- delta_validation: 下一轮先复核 `state/developer-workspaces.json` 与四个 helper 实际 `HEAD` 是否仍保持 `ea7291e`，再看 `workflow_devmate` 是否产出可落地的 `V1-P5` 实现切片
