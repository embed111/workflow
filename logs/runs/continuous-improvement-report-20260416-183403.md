# Continuous Improvement Report

- ticket_id: `asg-20260327-223335-b79f27`
- node_id: `node-sti-20260416-5af36d83`
- snapshot_at: `2026-04-16T18:39:19+08:00`
- lane: `测试探测`
- lifecycle_stage: `开发实现`
- version_transition_decision: `stay(V3)`

## 本轮推进
- 我先确认旧的 `173828` focused smoke `node-20260416-175628-a5fe91 / arun-20260416-175711-d4471e` 已在 `2026-04-16T18:14:37+08:00` 成功回交，并把旧基线上的 `/api/config/developer-workspaces` 异常冻结成 `DTS-00009`。
- 我再核 current live `prod=20260416-180910`，确认 `/api/config/developer-workspaces` 一度回到六个 developer workspace `clean_synced@1faa381`；但新 smoke 的最新采样已经把 `pm-main` 的两处 tracked dirty 抓出来了：`src/workflow_app/server/api/runtime_upgrade.py` 与 `scripts/acceptance/verify_runtime_upgrade_ghost_running_repair.py`。
- 我确认 `workflow_bugmate` 的 analyze 节点 `dr-20260416-c4b76f58cf-analyze / arun-20260416-182216-523e64` 已进入 `running`，不再停在 `ready`。
- 我随后创建并派发了新的 `workflow_testmate` current-live smoke `node-20260416-182651-41f1d9 / arun-20260416-182812-97e25f`，直接验证 `180910` 基线上 `DTS-00009` 是否仍复现。

## 当前版本
- `V3-R1`: `completed / 100% / ETA 2026-04-16 / 未超时`
- `V3-R2`: `in_progress / 99% / ETA 2026-04-16 / 未超时`。当前等待 `workflow_testmate` 的 `180910` smoke 与 `workflow_bugmate` 的 `DTS-00009` analyze 一起收口职责边界证据。
- `V3-R3`: `planned / 35% / ETA 2026-04-18 / 未超时`
- `V3-R4`: `completed / 100% / ETA 2026-04-16 / 未超时`
- `V3-R5`: `in_progress / 99% / ETA 2026-04-16 / 未超时`。当前等待 `workflow_testmate` 的 `180910` smoke 明确确认 `DTS-00009` 在 current live 上是否已消失。

## 发布边界
- `root_sync_state=ahead_dirty`
- `ahead_count=0`
- `dirty_tracked_count=2 / untracked_count=0`
- `workspace_head=code_root_head=1faa381`
- `push_block_reason=pm-main_dirty_runtime_upgrade_ghost_repair_patch_detected`
- `next_push_batch=冻结并盘点 src/workflow_app/server/api/runtime_upgrade.py + scripts/acceptance/verify_runtime_upgrade_ghost_running_repair.py 这批 ghost-running repair 改动，确认归属与验证范围后再决定 commit/push`

## Live 真相
- 当前 `prod=current_version=candidate_version=20260416-180910`
- `/api/runtime-upgrade/status`: `candidate_is_newer=false / request_pending=false / drain_active=false / running_task_count=3 / can_upgrade=false`
- running: `workflow` 主线 `node-sti-20260416-5af36d83`
- running: `workflow_bugmate` analyze `dr-20260416-c4b76f58cf-analyze / arun-20260416-182216-523e64`
- running: `workflow_testmate` smoke `node-20260416-182651-41f1d9 / arun-20260416-182812-97e25f`
- ready: 下一条主线 `node-sti-20260416-34db2512`
- ready: 保底巡检 `node-sti-20260416-3594bb53`

## 验证
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `http://127.0.0.1:8090/api/config/developer-workspaces`
- `git -C .repository/pm-main status --short --branch`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260416-175711-d4471e/result.json`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260416-182216-523e64/run.json`
- `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260416-182812-97e25f/run.json`

## 风险
- `workflow_testmate` 的 `180910` smoke 仍在 `running`，`V3-R2 / V3-R5` 还不能直接改判完成。
- `pm-main` 已被当前 smoke 采样成 `ahead_dirty`，当前发布边界不再允许我继续按 clean 口径推进后续代码批次。
- `/api/runtime-upgrade/status` 仍暴露 `ghost_running_count=4` 的历史 refs，这轮没有把它当当前发布边界阻塞，但需要继续清债。

## 引用
- `preference_ref: state/user-preferences.md`
- `memory_ref: .codex/memory/2026-04/2026-04-16.md`
