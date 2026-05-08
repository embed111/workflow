# 7x24 主线恢复记录 2026-04-26 06:03

- preference_ref: state/user-preferences.md
- delta_observation: 用户通过 token 消耗发现 `2026-04-26 01:38 +08:00` 后主线停止；本轮恢复时确认不能只看 `/healthz`，必须核 `schedule detail -> node.json -> run.json -> events.log`。
- delta_validation: 下一轮继续验证 `[持续迭代] workflow` 终态后是否自动产生下一棒，尤其关注失败路径和 provider 冷启动超时。

## 背景
- 用户反馈：`7x24小时运行怎么停了`，观察到 `01:38` 后 token 停止消耗。
- 约束：只恢复原 `[持续迭代] workflow` 主线，不恢复 legacy `pm持续唤醒 - workflow 主线巡检`。

## 现场判断
- `prod` Web 服务在线，`/healthz` 可读。
- `prod` 已升级到 `current=candidate=20260426-012259`。
- 最初现场不是服务宕机，而是主线没有真实 running：`running_task_count=0`，原主线 schedule 无 future 出口。
- `05:34` 恢复触发 `sti-20260426-bb4a8b73` 建出了 `node-sti-20260426-bb4a8b73`，但 run `arun-20260426-053347-5d8a59` 先停在 `starting/provider_pid=0`。
- 该 run 后续真实启动过 provider，并在 `05:43:41 +08:00` 因任务内部读取缺失 `.running/control/prod-current.json` 失败收尾；失败后原 schedule 又落到 `enabled=false / next_trigger_at=""`。

## 恢复动作
- 使用受支持 API 更新原 schedule `sch-20260405-56eee156`：
  - `enabled=true`
  - once trigger: `2026-04-26T05:50:00+08:00`
  - priority 保持 `P1`
- 手动调用 `/api/schedules/scan` 命中 `sti-20260426-d93c99e2`。
- 对半断裂 trigger 再次调用 `/api/schedules/scan`，恢复出 assignment node：
  - ticket: `asg-20260327-223335-b79f27`
  - node: `node-sti-20260426-d93c99e2`
- 调用 `/api/assignments/asg-20260327-223335-b79f27/dispatch-next` 派发 ready 节点。
- 等待 provider 冷启动窗口，未再次中断半启动 run。

## 当前结果
- `/api/status`：
  - `running_task_count=1`
  - `queued_task_count=0`
  - `active_agent_count=1`
- `/api/runtime-upgrade/status`：
  - `current_version=20260426-012259`
  - `candidate_version=20260426-012259`
  - `running_task_count=1`
  - `ghost_running_detected=false`
- `/api/schedules/sch-20260405-56eee156`：
  - recent trigger `sti-20260426-d93c99e2`
  - `trigger_status=running`
  - `assignment_node_id=node-sti-20260426-d93c99e2`
- 文件真相：
  - node: `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/nodes/node-sti-20260426-d93c99e2.json`
  - run: `C:/work/J-Agents/.output/tasks/asg-20260327-223335-b79f27/runs/arun-20260426-055355-bd87fb/run.json`
  - events: `provider_start / thread.started / turn.started` at `2026-04-26T06:02:01+08:00`
  - provider pid: `55660`

## 二次复核 2026-04-26 06:07
- `arun-20260426-055355-bd87fb` 仍为真实 running：
  - `run.json.status=running`
  - `run.json.updated_at=2026-04-26T06:07:20+08:00`
  - `provider_pid=55660`
  - Windows 进程 `node pid=55660` 仍存活
- `node-sti-20260426-d93c99e2.json` 仍为 `status=running / record_state=active`。
- `result.json` 尚未出现，说明本轮尚未终态收尾。
- `stdout.txt` 与 `events.log` 已达到产品截断上限；后续观察不能再依赖 tail 增长，必须继续以 `run.json / result.json / node.json / runtime-upgrade status` 为准。
- `/api/runtime-upgrade/status` 仍显示 `running_task_count=1 / ghost_running_detected=false / current=candidate=20260426-012259`。

## 剩余风险
- provider 启动耗时约 8 分钟，`dispatch-next` 客户端超时不等于派发失败；后续不要在冷启动窗口内重复 override 或取消。
- `05:34` 那一棒暴露出任务内部仍有历史路径假设：读取 `.running/control/prod-current.json` 会失败；这应由正在恢复的主线或下一轮作为工程修复项继续处理。
- 失败路径曾把原 once schedule 投影为无 future 出口；后续要继续验证 durable handoff 是否覆盖所有终态。
