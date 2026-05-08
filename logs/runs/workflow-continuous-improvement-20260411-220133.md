# workflow 持续迭代报告

- updated_at: `2026-04-11T22:01:33+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260411-f4bc26eb`
- active_version: `V1`
- task_package: `V1-P2`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- baseline: `prod=20260411-214605`
- memory_ref: `.codex/memory/2026-04/2026-04-11.md`

## 本轮结论
- 我把 `PM版本推进计划.md -> pm_version_status_service.py -> /api/status,/api/dashboard,schedule prompt` 这条真相读链里的 baseline 解析 bug 收口了，避免再把前文代码标识里的 `baseline` 误读成当前快照 baseline。
- 这批修正已经完成 `line budget -> 定向 truth-source 验收 -> workflow gate -> test -> prod candidate` 闭环；当前 `pm-main / ../workflow_code` 已 clean synced 到 `ea7291e`，新的 `candidate=20260411-220013` 已就位。
- live `prod` 目前已经是 `20260411-214605`，但还没切到包含本轮修正的 `220013`，所以 `/api/status.pm_version_status.baseline` 仍暂时显示旧脏值；当前真正阻塞是 `running_tasks_present / can_upgrade=false`，不是发布边界重新变脏。

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
  - `node_id=node-sti-20260411-f4bc26eb`
  - `run_id=arun-20260411-214708-61a24c`
  - `run_status=running`
  - `latest_event_at=2026-04-11T21:49:36+08:00`
  - `provider_pid=23976`
- 当前 ready 出口：
  - `node_id=node-sti-20260411-2296d40f`
  - `planned_trigger_at=2026-04-11T21:49:00+08:00`
  - `status=ready`
- 当前任务图真相：`1 running / 1 ready / 6 pending / 12 failed / 3 blocked`
- 当前 `/api/status` 仍带旧 baseline 脏值 `收成可复用读链。 2.`；原因不是计划快照又漂了，而是 live `prod=20260411-214605` 还没拿到本轮 `ea7291e` 的修正
- 当前 `/api/runtime-upgrade/status.last_action` 仍停在旧的 `watchdog_restart -> 20260411-093051`；当前 live 版本应以 `current_version=20260411-214605`、`.running/control/envs/prod.json` 与 `.running/control/instances/prod.json` 为准

## 本轮动作
1. 我重读了治理链、版本计划、发布边界方案和今日日记，然后重新核了 `pm-main / ../workflow_code` 的 Git 真相与 live API。
2. 我在 `.repository/pm-main` 修了 `pm_version_status_service.py`，把 baseline 解析锚到 `4.6.1 当前现场更新`，并兼容 `继续沿用 / 为 / 已切到` 三种 baseline 文案。
3. 我补强了 `scripts/acceptance/verify_pm_version_truth_source.py`，直接钉住“当前快照 baseline 必须等于 `4.6.1` 里的 baseline 行”。
4. 我按 `test-session-manager` 串行跑了：
   - `python scripts/quality/check_workspace_line_budget.py --root .`
   - `python scripts/acceptance/verify_pm_version_truth_source.py`
   - `python scripts/acceptance/run_acceptance_workflow_gate.py --root . --host 127.0.0.1 --port 8098`
5. 我把改动提交为 `ea7291e fix(pm-version): 收紧当前快照baseline解析并补回归验收`，并通过 `git -C ../workflow_code pull --ff-only D:/code/AI/J-Agents/workflow/.repository/pm-main main` 同步回本机代码根仓。
6. `test` 部署先被健康实例拦住；我随后用受支持的 `stop_workflow_env.ps1 -Environment test` 停掉 `PID=13792`，再成功刷新 `test` 与 `prod candidate=20260411-220013`。

## 验证证据
- `git -C .repository/pm-main status --short --branch`
- `git -C .repository/pm-main rev-parse --short HEAD`
- `git -C ../workflow_code status --short --branch`
- `git -C ../workflow_code rev-parse --short HEAD`
- `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- `.repository/pm-main/.test/20260411-215531-202/report.md`
- `.repository/pm-main/.test/20260411-215644-293/report.md`
- `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260411-215820.md`
- `.running/control/reports/test-gate-20260411-220013.json`
- `.running/control/logs/test/deploy-20260411-220013.json`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/runtime-upgrade/status'`
- `Invoke-RestMethod 'http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/graph'`
- `Get-Content .running/control/prod-candidate.json`
- `Get-Content .running/control/envs/prod.json`
- `Get-Content .running/control/instances/prod.json`

## baseline 与变更控制
- 本轮 baseline 已切到：`prod=20260411-214605`
- 本轮变更控制更新：
  - `V1-P2B` 的当前快照 baseline 解析 bug 已修复并进入 `candidate=20260411-220013`
  - `V1-P5` 仍未退出，但当前不再是“candidate 刷不出来”；当前真正等待的是 `220013` 的升级空窗
  - 当前继续遵守：主线/巡检节点不自行调用 `/api/runtime-upgrade/apply`

## 协作与下一步
- 本轮没有新挂 helper 任务；原因不是缺执行者，而是当前最值钱的动作是先让 `ea7291e` 进入现网，再观察升级空窗是否仍需要 `V1-P5` 的 drain / dispatch 分流。
- 主线 next：
  - 当前 running：`node-sti-20260411-f4bc26eb / arun-20260411-214708-61a24c`
  - 当前 ready：`node-sti-20260411-2296d40f / [持续迭代] workflow / 2026-04-11 21:49:00`
- 升级 next：只有当真正出现 `running_task_count=0` 的 idle 窗口后，`candidate=20260411-220013` 仍未自动 apply，下一轮才优先验证 `prod supervisor / idle watcher`
- 若 `node-sti-20260411-2296d40f` 接棒后继续长期维持 `1 running + 1 ready`，再回到 `V1-P5` 继续评估 drain / dispatch 分流

## Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: 受支持的 `prod` 直接重发已经把现网切到 `20260411-214605`，但 `runtime-upgrade/status.last_action` 仍停在旧的 `watchdog_restart`；live 版本判断必须看 `current_version + envs/instances + deploy log`，不能只看 `last_action`
- delta_validation: 下一轮先等 `candidate=20260411-220013` 的真实升级结果；若 live `prod` 仍不切版，再沿 `current_version / envs / instances / deploy log / watcher` 这条读链排障
