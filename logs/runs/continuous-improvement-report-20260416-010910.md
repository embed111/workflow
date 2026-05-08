# continuous-improvement-report

- generated_at: `2026-04-16T01:09:10+08:00`
- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260415-15166d14`
- active_version: `V3`
- lane: `功能开发`
- lifecycle_stage: `开发实现`
- version_transition_decision: `stay(V3)`
- memory_ref: `.codex/memory/2026-04/2026-04-16.md`

## Result Summary
- 我把 assignment center/backend 的默认焦点从“优先 ready mainline”收成了“优先当前 running，同时显式保留 next mainline handoff”，避免 patrol 正在真实 running 时 UI 继续误报主线已经在跑。
- 我把 `verify_assignment_mainline_visibility.py` 改成用真实 `run.json` 种 live 夹具，并把 `verify_assignment_execution_thread_start_outside_dispatch_lock.py` 收成显式 `WORKFLOW_RUNTIME_ENV=test`，避免 isolated acceptance 被 live prod drain 串味。
- 我完成了 `line budget -> assignment visibility probes -> dispatch-lock probe -> pm awake TC pack -> 完整 workflow gate` 的验证链，并确认 gate 最终通过。
- 我把代码提交为 `e3e437b fix(assignment-center): 当前运行优先展示并隔离主线可见性验收`，用受支持的 `ff-only` 把本机 `workflow_code` 收口到同一提交，再把 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 五个 developer workspace 一起 refresh 到新头。
- 我停掉旧 `test` 后重新部署，刷新出新的 `candidate=20260416-010530`；当前 `prod` 仍在 `20260416-000938`，idle watcher 需要等空窗后再自动切换。

## Active Requirement Review
- `V3-R1`: `status=in_progress / progress=70% / eta=2026-04-16 / timeout=未超时`
- `V3-R2`: `status=in_progress / progress=88% / eta=2026-04-16 / timeout=未超时`
- `V3-R3`: `status=planned / progress=35% / eta=2026-04-18 / timeout=未超时`
- `V3-R4`: `status=in_progress / progress=97% / eta=2026-04-16 / timeout=未超时`
- `V3-R5`: `status=in_progress / progress=92% / eta=2026-04-16 / timeout=未超时`
- AAR: `本轮无需求点超时，不新增 AAR`

## Release Boundary
- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `workspace_head=code_root_head=e3e437b`
- `push_block_reason=-`
- `next_push_batch=等待 candidate 20260416-010530 进入 live 后，由 workflow_testmate 复跑 prod current-version smoke，并确认 assignment center 当前运行/主线接棒不回退`
- `pm-main git status=main...origin/main`
- `../workflow_code git status=main...origin/main [ahead 81]` 仅作为 GitHub/origin 参考，不构成本轮本机根仓阻塞

## Live Snapshot
- `prod_current_version=20260416-000938`
- `candidate_version=20260416-010530`
- `candidate_is_newer=true`
- `request_pending=false`
- `drain_active=true`
- `running_task_count=1`
- `queued_task_count=2`
- `active_agent_count=1`
- `pm_version_status.baseline=document_baseline=prod=20260416-000938`
- `pm_version_board.next_activation_candidate=V4`
- `pm_version_board.next_activation_ready=false`

## Validation
- `.repository/pm-main/.test/20260416-003720-861/report.md`
- `.repository/pm-main/.test/20260416-004455-791/report.md`
- `.repository/pm-main/.test/20260416-004511-679/report.md`
- `.repository/pm-main/.test/20260416-005205-826/report.md`
- `.repository/pm-main/.test/20260416-005654-749/report.md`
- `.repository/pm-main/.test/20260416-005754-240/report.md`
- `.running/control/logs/test/deploy-20260416-010530.json`

## Snapshot Addendum
- preference_ref: `state/user-preferences.md`
- delta_observation: `assignment center 在 patrol running + mainline ready 的 live 现场里，最容易失真的是“当前到底谁在跑”；这轮已经把当前 running 优先展示、isolated acceptance 环境隔离和本机 workflow_code ff-only 收口一起压成稳定做法。`
- delta_validation: `candidate=20260416-010530` 进入 live 后，让 workflow_testmate 用 current-version smoke 复跑 prod，并额外确认 assignment center 的“当前运行 / 主线接棒”展示不回退。`
