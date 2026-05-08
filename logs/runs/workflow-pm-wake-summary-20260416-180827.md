# workflow pm wake summary - 2026-04-16 18:08

- ticket: `asg-20260327-223335-b79f27`
- node: `node-sti-20260416-5531f850`
- lane: `测试探测`
- lifecycle_stage: `开发实现`
- version_transition_decision: `stay(V3)`
- memory_ref: `.codex/memory/2026-04/2026-04-16.md`
- preference_ref: `state/user-preferences.md`

## 本轮结论
- 我先把 `pm-main` 的假 `ahead 3` 清掉，再把五个 helper developer workspace 从 `603577c` 追平到 `1faa381`，当前 `/api/config/developer-workspaces` 已恢复六个工作区全部 `clean_synced@1faa381`。
- 我修复了 `.repository/pm-main/scripts/bin/refresh_pm_current_version_snapshot.py` 对“缺少 baseline 行、只保留 \`prod 已切到...\` 句式”的 live 兼容，并补了一条真实回归到 `.repository/pm-main/scripts/acceptance/verify_pm_current_version_snapshot_refresh.py`；`line budget`、定向回归和完整 `workflow gate` 均通过。
- 我把这批代码提交为 `1faa381 fix(snapshot): 兼容缺少baseline行的current-version快照刷新`，并用受支持的本机 `../workflow_code` fast-forward 收口，再把 `pm-main / workflow_testmate / workflow_devmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 六个 developer workspace 全量 refresh 到同一提交。
- 我重新执行了 live snapshot refresh，当前 `/api/status.pm_version_status.document_baseline` 已恢复为 `prod=20260416-173828`。
- 我补发了 `workflow_testmate` 的 focused smoke 节点 `node-20260416-175628-a5fe91` / run `arun-20260416-175711-d4471e`；它已经进入 `running`，但创建时仍锁着旧的 `code_root_head=603577c`。由于我随后把根仓推进到了 `1faa381`，这条 smoke 若最终只报 head mismatch，不视为产品回退，而是下一拍按 `1faa381` 直接 clean rerun。
- 我完成了 `test` 部署并刷新出新的 `prod candidate=20260416-180910`；当前 `prod` 仍是 `20260416-173828`，`candidate_is_newer=true / drain_active=true / running_task_count=2`，当前巡检节点不会触发正式升级。

## active 需求评估
- `V3-R1`: `completed / 100% / ETA 2026-04-16 / 未超时`
- `V3-R2`: `in_progress / 99% / ETA 2026-04-16 / 未超时`
  现网 `workflow_focus_context` 仍保持“patrol running + next mainline ready”的正确分离；剩余动作改成等待 `node-20260416-175628-a5fe91` 回交 focused smoke。若这条 smoke 只因旧 `603577c` 期望失真，则按 `1faa381` clean rerun。
- `V3-R3`: `planned / 35% / ETA 2026-04-18 / 未超时`
- `V3-R4`: `completed / 100% / ETA 2026-04-16 / 未超时`
  发布边界和 helper workspace 漂移已收口到 `1faa381`。
- `V3-R5`: `in_progress / 99% / ETA 2026-04-16 / 未超时`
  `document_baseline` 已追平到 `173828`，focused smoke 已 running；当前唯一未收口项是等待 smoke 正式回执。
- 本轮没有需求点超时，不触发新的 `AAR`。

## 发布边界
- `root_sync_state=clean_synced`
- `ahead_count=0`
- `dirty_tracked_count=0`
- `untracked_count=0`
- `workspace_head=code_root_head=1faa381`
- `push_block_reason=-`
- `next_push_batch=等待 workflow_testmate 回交 node-20260416-175628-a5fe91 的 173828 smoke；若其因旧 603577c 期望失败，则按 1faa381 clean rerun，再决定是否继续质量审计 / defect 路由`

## 验证证据
- `git -C .repository/pm-main status --short --branch`
- `http://127.0.0.1:8090/healthz`
- `http://127.0.0.1:8090/api/status`
- `http://127.0.0.1:8090/api/runtime-upgrade/status`
- `http://127.0.0.1:8090/api/config/developer-workspaces`
- `http://127.0.0.1:8090/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-20260416-175628-a5fe91&include_test_data=0`
- `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.md`
- `.repository/pm-main/.test/20260416-175427-602/report.md`
- `.repository/pm-main/.test/20260416-175820-940/report.md`
- `.running/control/logs/test/deploy-20260416-180910.json`

## 风险与下一步
- 当前 live 风险不是“主线断了”，而是 `workflow_testmate` 这条 smoke 创建在根仓推进前，prompt 里仍保留旧 `603577c` 期望；如果它因此报错，我下一拍不做额外解释，直接按 `1faa381` clean rerun。
- 当前 `workflow_mainline_handoff_pending=true`：巡检节点 `node-sti-20260416-5531f850` 还在运行，真正的 `[持续迭代] workflow` `node-sti-20260416-5af36d83` 已 ready，下一拍要确认 patrol 收尾后 mainline 能正常接棒。
- `/api/runtime-upgrade/status` 仍有 `ghost_running_detected=true / ghost_running_count=4` 的历史 refs；这轮先不清债，保留到下次在 smoke 和 handoff 收口后再处理。
