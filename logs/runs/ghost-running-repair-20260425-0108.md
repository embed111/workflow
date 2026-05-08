# ghost running 修复记录 2026-04-25 01:08

- topic: 清理当前 `prod` 上的 ghost running，恢复 `7x24` 连续运行的真实可读状态。
- operator: `workflow(pm)`
- environment: `prod current=20260424-174453`

## 问题现场
- 修复前 `/api/runtime-upgrade/status` 返回：
  - `ghost_running_detected=true`
  - `ghost_running_count=2`
  - refs 指向：
    - `node-20260424-ai-novel-ignite-01`
    - `node-sti-20260424-5fc400ac`
- 同时 `/api/status` 仍显示：
  - `running_task_count=2`
- 说明：看门狗侧已经识别到假运行，但系统其他读面还没有统一到终态真相。

## 执行动作
- 使用本地受支持函数逐条执行 `_runtime_upgrade_repair_single_ghost_running(...)`，把两条 ghost node 同步为终态。
- 随后对全局主图执行一次 `dispatch_assignment_next(...)`，确认当前没有残留 `ready` 节点需要继续派发。

## 修复结果
- 修复后 `/api/runtime-upgrade/status`：
  - `running_task_count=0`
  - `agent_call_count=0`
  - `ghost_running_detected=false`
  - `ghost_running_count=0`
- 节点终态已统一：
  - `node-20260424-ai-novel-ignite-01 -> failed`
  - `node-sti-20260424-5fc400ac -> failed`
- 全局主图当前状态：
  - `running=0`
  - `ready=0`
  - `scheduler_state=running`

## 7x24 连续性
- 当前不是“正在执行”，而是“假运行已清掉，系统回到等待下一棒”的空窗态。
- 保底巡检仍有 future：
  - `pm持续唤醒 - workflow 主线巡检`
  - `next_trigger_at=2026-04-25T01:20:00+08:00`
- 主线 schedule 也仍保持启用，且 `2026-04-25 01:00 +08:00` 有一轮 `update_schedule` 留痕，说明下一棒 once 计划已被继续更新。

## 结论
- 这轮 ghost running 已清理完成。
- `7x24` 当前已恢复到“服务在线、没有假运行、保留下一棒 future”的健康待触发状态。
- 当前剩余问题不在“幽灵运行没清掉”，而在：
  - 为什么会出现 `starting/provider_pid=0` 假运行
  - 为什么不同读面对同一节点终态投影不一致
  - 看门狗虽然能识别 ghost，但缺自动统一收口与测试护栏

## 后续
- 已继续把 watchdog/ghost-running 的测试护栏排进 `V12-R5`。
