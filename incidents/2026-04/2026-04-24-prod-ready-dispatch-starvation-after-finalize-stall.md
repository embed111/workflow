# 生产事故记录 | 2026-04-24 | prod ready 待派发假健康导致主线长时间空窗

- incident_id: `INC-20260424-prod-ready-dispatch-starvation-after-finalize-stall`
- severity: `SEV-2`
- environment: `prod`
- detected_at: `2026-04-24T00:17:00+08:00`
- detected_by: `workflow(pm)`
- related_version:
  - `broken_on_prod=20260423-213946`
  - `fixed_in_workspace=b762734`
  - `fixed_on_test=20260424-010149`
  - `fixed_on_prod=20260424-010431`
- related_requirement:
  - `V9-R4`
- status: `resolved`
- resolution_time: `2026-04-24T01:09:39+08:00`
- aar_policy: `defer_until_version_close`
- aar_target_version: `V9`

## 1. 事故摘要
- `prod` 在 `2026-04-23T22:50:53+08:00` 后长时间没有新的真实执行，但服务仍可恢复成“在线 + 有 ready/future 出口”的假健康形态。
- 用户侧直接症状是：
  - `token` 在早上八点后、以及这次夜里 `22:50` 后长时间不再增长
  - `8090` 一度不可达；恢复可达后，主线仍没有继续吃 token
  - 任务图里能看到 `ready` 或 `trigger_hit`，但就是派不出去

## 2. 用户面影响
- 从 `2026-04-23T22:50:53+08:00` 到 `2026-04-24T01:06:08+08:00` 之间，没有新的真实主线执行批次启动。
- 这不是“服务挂了”那么简单，而是更危险的“服务还活着，但 ready 任务不会继续派发”的假健康。
- 结果是：
  - 用户很容易被 `healthz`、`ready/future` 和页面可读性误导
  - `7x24` 实际推进中断，但表面不像完全停机

## 3. 现场真相
- 运行库里最后一条已完成真实执行是：
  - `arun-20260423-222919-8b35db`
  - `started_at=2026-04-23T22:29:13+08:00`
  - `finished_at=2026-04-23T22:50:53+08:00`
- 后续 trigger 现场：
  - `[持续迭代] workflow` 的 `sti-20260423-9eb98930` 长时间停在 `trigger_hit`
  - patrol 的 `23:00 / 23:20 / 23:40 / 00:00 / 00:20 / 00:40 / 01:00` 多拍 trigger 也只停在 `trigger_hit`
- helper 收尾现场：
  - `aaud-20260423-232328-bd2a23` 记录了 `recover_terminal_run_truth`
  - `detail.schedule_result={"queued": false, "reason": "ticket_lock_unavailable_bypassed"}`
  - 说明 finalize 曾经卡住，stale recovery 虽然把终态补回来了，但没有把下一条 ready 接力派发出去

## 4. 根因判断
- 直接根因不是 schedule 命中丢了，而是：
  - assignment finalize 把 `workspace memory / pm daily governance / prod upgrade request / follow-up dispatch`
  - 全部包在同一把全局 ticket mutation lock 里
- 一旦某条 helper run 在 post-commit 阶段卡住：
  - 同一张全局主图上的后续 `create_assignment_node` 会一起堵住
  - 已经存在的 `ready` 节点也可能因为 follow-up dispatch 没跑到而长期堆积
- 同时旧看门狗只盯“假 running / ghost running”，还没有把“`running_task_count=0` 但 ready 已老化、派发没继续”正式当成不健康并主动恢复。

## 5. 修复动作
- 代码修复：
  - `task_artifact_store_run_finalize_runtime.py`
    - 缩短 finalize 对全局 ticket mutation lock 的占用范围
    - 锁内只保留 run/node 终态回写与 schedule 续挂
    - `workspace memory / pm daily / prod upgrade / follow-up dispatch` 改到锁外执行
  - `schedule_ready_dispatch_runtime.py`
    - 新增 ready-dispatch 恢复逻辑
    - 当全局主图命中 `running=0 + ready 节点老化` 时，worker 主动补一次 `dispatch`
  - `schedule_trigger_runtime.py`
    - 把上述恢复接进 worker 的常规恢复轮次
- 验证：
  - `scripts/acceptance/verify_schedule_ready_dispatch_recovery.py`
  - `scripts/acceptance/verify_schedule_trigger_recovery_worker.py`
  - `scripts/acceptance/run_acceptance_workflow_gate.py`
- 发布：
  - `workflow_code/main` 收口到 `b762734`
  - `test=20260424-010149`
  - `prod=20260424-010431`

## 6. 事故证据
- gate：
  - `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260424-005807.md`
- 定向 probe：
  - `.repository/pm-main/.test/20260424-005223-495/report.md`
  - `.repository/pm-main/.test/20260424-005144-164/report.md`
- 部署：
  - `.running/control/logs/test/deploy-20260424-010149.json`
  - `.running/control/logs/prod/deploy-20260424-010431.json`
- live 恢复证据：
  - `.running/control/runtime/prod/logs/events/schedules.jsonl`
    - `2026-04-24T01:08:40+08:00 ready_dispatch_recovery_requested`
  - `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260424-010609-19fb0e/run.json`
    - 证明 `node-sti-20260423-9eb98930` 已重新进入真实 `running`

## 7. 后续避免方向（供版本结束 AAR 展开）
- `7x24` 的健康口径正式改成：
  - 不是“服务活着”
  - 也不是“还有 ready/future”
  - 而是 `ready` 任务要能继续被派发
- 运行看门狗除了盯 `ghost running`，还要持续盯：
  - `running_task_count=0`
  - `ready` 节点已老化
  - 最近没有新的 `dispatch/run`
- finalize 的长期规则要明确：
  - 锁内只做最小必要终态回写
  - 所有慢副作用尽量移到锁外
  - 不能再让一条 helper finalize 把整张全局主图一起拖死

## 8. AAR 约束
- 当前不在本事故卡里直接展开完整 AAR。
- `V9` 结束后，必须补做：
  - `pm/versions/V9/aar/YYYY-MM/<date>-prod-ready-dispatch-starvation-after-finalize-stall.md`
- AAR 至少要回答：
  - 为什么当时会把“ready/future 仍在”误认为健康
  - 为什么 finalize 的慢副作用还能持有全局 ticket 锁
  - 为什么看门狗此前只盯假运行，没有把假待派发纳入正式恢复闭环
