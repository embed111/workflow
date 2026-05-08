# 持续迭代报告 2026-04-17 19:19:23 +08:00

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260417-b2efa172`
- active_version: `V4`
- lane: `测试探测`
- lifecycle_stage: `基于基线测试`
- baseline: `prod=20260417-174930`
- workspace_head: `adf0226`
- code_root_head: `adf0226`
- root_sync_state: `clean_synced`
- preference_ref: `state/user-preferences.md`

## 本轮推进
- 我把 `workflow_devmate` 的首屏状态分层补丁从 helper 工作区回放到 `pm-main`，提交为 `.repository/pm-main@adf0226 fix(task-center): 拆分首屏materialization状态并降权旧starvation注释`。
- 我按 `test-session-manager` 跑通了 `line budget`、`verify_assignment_center_mainline_visibility.js`、`verify_assignment_workboard_signal_cards.js` 和完整 `workflow gate`。
- 我没有把根仓阻塞留给下一轮：在 `updateInstead` 继续拒绝直接 push 的情况下，我按稳定经验改走 `git -C ../workflow_code fetch <pm-main> main + git -C ../workflow_code merge --ff-only FETCH_HEAD`，把本机代码根仓收口到 `../workflow_code@adf0226`。
- 我停掉旧 `test` 后重新部署，刷新出了新的 `prod candidate=20260417-191531`。
- 我还处理了 `workflow_testmate` 回归 run 的 `running_finalize_stall`：调用受支持的 `/api/runtime-upgrade/repair-ghost-running` 后，`ghost_running_detected` 已回到 `false`，升级门禁只剩真实 running 在挡。

## 验证证据
- `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/20260417-191018-142/report.md`
- `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/20260417-191026-468/report.md`
- `D:/code/AI/J-Agents/workflow/.repository/pm-main/.test/runs/workflow-gate-acceptance-20260417-191323.md`
- `D:/code/AI/J-Agents/workflow/.running/control/logs/test/deploy-20260417-191531.json`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/artifacts/node-20260417-184228-f0f39b/output/workflow-testmate-v4-r1-materialization-regression-174930.md`

## 当前版本判断
- `V4-R1=status=in_progress / progress=70% / eta=2026-04-19 / timeout=未超时`
- `V4-R2=status=planned / progress=5% / eta=2026-04-20 / timeout=未超时`
- `V4-R3=status=planned / progress=10% / eta=2026-04-20 / timeout=未超时`
- `V4-R4=status=in_progress / progress=92% / eta=2026-04-20 / timeout=未超时`
- `version_transition_decision=stay(V4)`
- `next_activation_candidate=- / next_activation_ready=false`
- `switch_blockers=V5 仍保持 backlog activation_readiness=draft`
- 本轮没有需求点超时，不新增 AAR。

## 当前 live 真相
- `/api/status`: `active_agent_count=1 / running_task_count=1 / queued_task_count=2 / workflow_mainline_starvation_state=mitigated`
- `/api/runtime-upgrade/status`: `current_version=20260417-174930 / candidate_version=20260417-191531 / candidate_is_newer=true / drain_active=true / running_task_count=1 / ghost_running_detected=false`
- `workflow_testmate` 的 `174930` 回归已经明确回流：旧 live 首屏仍是旧 bundle 逻辑，fail 主因是 `实现未生效`，不是状态读链错误；这条结论 supersede 了 `145421/160828` 的旧 smoke 口径。

## 下一步
- 等 idle watcher 在空窗把 `candidate=20260417-191531` 切进 `prod`。
- 切版后优先复跑首屏 materialization regression 和 `collect_v4_r1_r4_current_version_smoke.py`。
- 若 `191531` live 后首屏仍然 fail，再把问题切成新的最小实现批次继续推进。

## 增量观察
- delta_observation: `updateInstead` 继续拒绝直接 push 到本机 `workflow_code` 时，根仓侧 `fetch + ff-only merge` 仍然是受支持且可靠的收口动作；同时 helper 回归 run 的 `running_finalize_stall` 会直接卡住 idle watcher，必须当轮修掉。
- delta_validation: 等 `191531` 切进 live 后，复跑同一条首屏 materialization regression，验证 fail 是否从“实现未生效”转为真正绿灯。
- memory_ref: `.codex/memory/2026-04/2026-04-17.md`
