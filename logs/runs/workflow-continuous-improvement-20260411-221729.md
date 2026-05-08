# workflow 持续迭代报告

- updated_at: `2026-04-11T22:17:29+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260411-2296d40f`
- active_version: `V1`
- task_package: `V1-P2`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- baseline: `prod=20260411-214605`
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`

## 本轮结论
- 我这轮没有改代码，也没有跑额外测试；我把 `21:49` 主线最新 live 真相回写到了治理留痕。
- `pm-main / ../workflow_code` 当前仍 clean synced 到 `ea7291e`，发布边界继续干净，`root_sync_state=clean_synced` 不需要进入额外收口模式。
- 当前 `21:49` 这条主线已经在 `2026-04-11T22:11:56+08:00` 接成真实 run `arun-20260411-221157-a16f89`；任务图现场从上一轮的 `1 running + 1 ready` 收敛成 `1 running + 0 ready + future 已续挂`。
- live `prod` 仍是 `20260411-214605`，更高 `candidate=20260411-220013` 已就位但还未切入；当前真正待观察的是本轮 run 收尾后的 idle window 是否会触发 watcher 自动升级。
- `/api/status.pm_version_status.baseline` 仍显示旧脏值 `收成可复用读链。 2.`；这不是计划正文又漂了，而是 live `prod` 还没拿到 `ea7291e` 里的 baseline 解析修正。

## 根仓同步快照
- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `push_block_reason=-`
- `next_push_batch=待切批`
- 当前工作区：`pm-main`
- `workspace_head=code_root_head=ea7291e`
- 说明：`pm-main / ../workflow_code` 相对 `origin/main` 仍是 `ahead 10`，这里只继续作为上游参考，不构成本轮阻塞。

## live 现场
- `prod current_version=20260411-214605`
- `candidate_version=20260411-220013`
- `candidate_is_newer=true`
- `blocking_reason=running_tasks_present / can_upgrade=false`
- 当前真实 running：
  - `node_id=node-sti-20260411-2296d40f`
  - `run_id=arun-20260411-221157-a16f89`
  - `run_status=running`
  - `started_at=2026-04-11T22:11:56+08:00`
  - `latest_event_at=2026-04-11T22:16:04+08:00`
  - `provider_pid=65976`
- 当前 future 出口：
  - 主线：`[持续迭代] workflow -> 2026-04-11T22:27:00+08:00`
  - 保底：`pm持续唤醒 - workflow 主线巡检 -> 2026-04-11T23:27:00+08:00`
- 当前任务图真相：`1 running / 0 ready / 6 pending / 12 failed / 3 blocked`
- 当前 `/api/status` 仍显示 `truth_mismatch_count=1`，且 `pm_version_status.baseline` 仍是旧脏值 `收成可复用读链。 2.`；本轮只做现场对齐，不新增代码修复
- 当前 `/api/runtime-upgrade/status.last_action` 仍停在旧的 `watchdog_restart -> 20260411-093051`；当前 live 版本判断仍以 `current_version=20260411-214605`、`.running/control/envs/prod.json` 与 `.running/control/instances/prod.json` 为准

## 本轮动作
1. 我按读链重读了治理、经验、SOUL/USER/MEMORY、全局/月度/今日日记，并确认 `2026-04-10` 已经归档到月度总览。
2. 我核了 `pm-main / ../workflow_code` 的 Git 真相，确认当前没有 dirty/ahead/untracked 异常需要发布边界收口。
3. 我核了 `/healthz`、`/api/status`、`/api/schedules`、`/api/runtime-upgrade/status`、全局任务图、`status-detail`，并顺着 audit_ref 读取了当前 run 的 `run.json / events.log`。
4. 我把最新有效快照回写到 `docs/workflow/governance/PM版本推进计划.md` 和 `docs/workflow/governance/pm-version-live/2026-04/现场更新总览.md`。
5. 我新增了 `logs/runs/workflow-continuous-improvement-20260411-221729.md`，并同步补写了今日日记。

## 验证证据
- `git -C .repository/pm-main status --short --branch`
- `git -C .repository/pm-main rev-parse --short HEAD`
- `git -C .repository/pm-main rev-list --left-right --count origin/main...main`
- `git -C ../workflow_code status --short --branch`
- `git -C ../workflow_code rev-parse --short HEAD`
- `git -C ../workflow_code rev-list --left-right --count origin/main...main`
- `Invoke-RestMethod 'http://127.0.0.1:8090/healthz'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/schedules'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/graph'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260411-2296d40f'`
- `Get-Content -Raw C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-221157-a16f89/run.json`
- `Get-Content C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260411-221157-a16f89/events.log -Tail 120`
- `Get-Date -Format o`

## baseline 与变更控制
- 本轮 baseline 未变，继续沿用：`prod=20260411-214605`
- 本轮没有新增变更控制项，也没有新增代码实现；当前仍按 `V1-P2` 的 live 落地验证来收口
- 当前继续遵守：主线/巡检节点不自行调用 `/api/runtime-upgrade/apply`

## 协作与下一步
- 本轮没有继续补派 helper；当前更高优先的是先观察 `candidate=20260411-220013` 是否在当前 run 收尾后的空窗自动切入现网
- 主线 next：
  - 当前 running：`node-sti-20260411-2296d40f / arun-20260411-221157-a16f89`
  - 下一次主线触发：`2026-04-11T22:27:00+08:00`
- 保底 next：`2026-04-11T23:27:00+08:00`
- 升级 next：
  - 若当前 run 收尾后、`22:27` 前出现真实 idle window 而 `220013` 仍未自动 apply，下一轮优先验证 `prod supervisor / idle watcher`
  - 若 `220013` 已切入现网，下一轮优先复核 `/api/status.pm_version_status.baseline` 是否恢复正常，并再决定 baseline 是否切到 `prod=20260411-220013`

## Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: 当前 `21:49` 主线已在 `22:11:56` 接成真实 run，现场从 `1 running + 1 ready` 收敛成 `1 running + future 已续挂`；当前更该观察的是 idle watcher 是否能在本轮 run 结束后的空窗自动切入 `220013`
- delta_validation: 下一轮先复核 `current_version / candidate_version / schedules next_trigger_at / run finished_at` 四项；若 idle window 已出现但未自动升级，再沿 `prod supervisor / idle watcher` 继续排障
