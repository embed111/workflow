# 持续迭代报告 2026-04-17 20:37

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260417-58114eb5`
- active_version: `V4`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- preference_ref: `state/user-preferences.md`
- memory_ref: `.codex/memory/2026-04/2026-04-17.md`

## 本轮推进

- 我把 live smoke 撞出来的 capped trace 读链问题收成了正式修复：`workspace_state_and_metrics.py` 现在会在 trace 到达上限时只写完整 UTF-8 前缀，并在读取事件尾部时容忍被截断的尾巴，避免 `status-detail.event_count/events` 再掉成 `0/[]`。
- 我新增了 `verify_assignment_run_event_tail_decode_tolerant.py`，并把它接进 `workflow gate`，让这条 regression 不再只靠 live smoke 偶遇。
- 我把五个 helper developer workspace 全部 refresh 到 `clean_synced@753a503`，把这轮新 head 带出来的 helper drift 收回根仓真相。
- 我识别出 `test gate` 的阻塞是旧 `artifact_root` 残留复用了历史测试图，随后通过受支持的 `/api/config/artifact-root` 把 `test` 拉回 `.running/.output`，确认 bootstrap 立刻恢复为 `created=true / running=1`，再重部署 `test`，刷新出新的 `prod candidate=20260417-203210`。
- 我随后通过受支持的 `/api/runtime-upgrade/repair-ghost-running` 收掉了 `8092` 上新残留的 `T9 ghost`，让 `test` 当前版本现场回到 `ghost_running_detected=false`。

## 验证

- `line budget`: `.repository/pm-main/.test/20260417-201900-191/report.md`
- 新 probe: `.repository/pm-main/.test/20260417-202112-466/report.md`
- `workflow gate`: `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260417-202431.md`
- 真实截断文件直读验证：当前补丁下 `arun-20260417-200200-ce9db3/events.log` 已能重新解析，`status-detail.event_count=120`
- `test gate / candidate`: `.running/control/reports/test-gate-20260417-203210.json`
- `test deploy`: `.running/control/logs/test/deploy-20260417-203210.json`
- `prod` 当前真相：`current_version=20260417-194345 / candidate_version=20260417-203210 / candidate_is_newer=true / drain_active=true / running_task_count=1`
- `developer workspaces` 当前真相：`pm-main / workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 已全部 `clean_synced@753a503`
- `test` 当前真相：`current_version=20260417-203210 / ghost_running_detected=false / running_task_count=0`

## V4 状态

- `V4-R1`: `in_progress / 70% / eta=2026-04-19 / 未超时`
- `V4-R2`: `planned / 5% / eta=2026-04-20 / 未超时`
- `V4-R3`: `planned / 10% / eta=2026-04-20 / 未超时`
- `V4-R4`: `in_progress / 98% / eta=2026-04-20 / 未超时`
- `version_transition_decision=stay(V4)`
- `next_activation_candidate=- / next_activation_ready=false / switch_blockers=V5 仍保持 backlog activation_readiness=draft`

## 发布边界

- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0 / untracked_count=0`
- `workspace_head=code_root_head=753a503`
- `push_block_reason=-`
- `next_push_batch=等待 idle watcher 在空窗把 20260417-203210 切进 prod，再复跑 current-version truth smoke 与 browser regression`

## 增量观察

- delta_observation: `194345` 当前 live 上真正新红点不是首屏 UCD 本体，而是 capped `events.log` 把 `status-detail.event_count/events` 打回 `0/[]`；同一轮里 helper developer workspace drift 和 test `artifact_root` 旧残留也一起暴露。
- delta_validation: 等 `203210` 切进 `prod` 后，优先复跑 `collect_v4_r1_r4_current_version_smoke.py` 与 browser regression，确认 capped trace 下的 `status-detail.event_count` 与页面运行详情都保持正常。
