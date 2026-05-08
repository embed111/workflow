# Workflow PM Wake Summary - 20260412-114723

- ticket/node: `asg-20260327-223335-b79f27 / node-sti-20260412-9dd5390b`
- phase/lane: `开发实现 / 工程质量探测`
- conclusion: 当前继续推进，不保持暂停，也不需要额外补新保底；但这轮确实命中了两次受支持异常治理，已经在本轮完成收口。

## Live

- `prod /healthz=ok`
- 当前真实运行节点仍是 `node-sti-20260412-9dd5390b / arun-20260412-111913-b596f8`
- 当前 workboard 为 `running_task_count=1 / queued_task_count=0`，不是 `0 running + ready pileup` 的假健康
- `[持续迭代] workflow` 已恢复 future `2026-04-12T11:55:00+08:00`
- `pm持续唤醒 - workflow 主线巡检` 已续到 future `2026-04-12T12:55:00+08:00`

## Boundary

- 最终发布边界：`root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=880976d / push_block_reason=- / next_push_batch=待切批`
- 上游 `origin/main [ahead 17]` 继续只作为参考，不当成本轮本机阻塞

## Actions

- 发现 `.repository/pm-main` 的 self-iteration prompt 改动未收口后，先补最小验证与 `workflow gate`
- 收口提交 `d31c87b fix(pm-7x24): 避免主线提示词重复空转`
- 收口提交 `c665ea0 fix(pm-7x24): 压缩主线提示词避免 node_goal 超长`
- 收口提交 `880976d fix(pm-7x24): 主动治理工作区异常避免等待`
- 已同步本机 `../workflow_code` 到 `880976d`
- 已两次按受支持链路部署 `test`，最终刷新 `prod candidate=20260412-114509`
- 发现 `11:35` 主线因 `node_goal too long` 失败后，已把 prompt 压短并重新补回主线 future
- 已通过 `/api/schedules/{id}` 刷新 live future prompt，确认 release boundary 已回到 `clean_synced / 880976d`

## Upgrade

- 当前 `prod current=20260412-041736`
- 当前 `candidate=20260412-114509`
- `candidate_is_newer=true / can_upgrade=false / running_task_count=1 / drain_active=true`
- 这轮没有手工调用 `/api/runtime-upgrade/apply`，继续由 idle watcher 在空窗发起正式升级

## Evidence

- 定向验证会话：`.repository/pm-main/.test/20260412-112509-591/report.md`
- gate 会话 1：`.repository/pm-main/.test/20260412-112528-931/report.md`
- 定向验证会话 2：`.repository/pm-main/.test/20260412-114200-218/report.md`
- gate 会话 2：`.repository/pm-main/.test/20260412-114212-469/report.md`
- gate 报告：`.repository/pm-main/.test/runs/workflow-gate-acceptance-20260412-114336.md`
- test 部署报告：`.running/control/logs/test/deploy-20260412-112845.json`
- test 部署报告：`.running/control/logs/test/deploy-20260412-114509.json`
- 当前 patrol 详情：`/api/assignments/asg-20260327-223335-b79f27/status-detail?node_id=node-sti-20260412-9dd5390b`
- 当前 schedules：`/api/schedules`
- 当前升级门禁：`/api/runtime-upgrade/status`

## Warnings

- 当前运行中的 patrol 节点仍是 `11:08` 时刻派发的旧 prompt 快照；这不影响当前 run 持续，但 `11:55` 主线是否不再命中 `node_goal too long` 仍需下一轮现场复核
- `sch-20260405-56eee156` 的最近结果仍停在 `11:35` 那次失败快照；当前是通过重新启用 future `11:55` 进行补链，不是抹掉历史失败证据
