# 定时触发闭环经验

## 适用范围
- `定时任务 -> 任务中心` 命中建单
- pm / `workflow` 周期性唤醒与自迭代
- schedule trigger 的失败恢复与回写

## 稳定经验
- 定时 worker 命中后不要同步等待“建节点 + 派发 + 结果回写”整条链完成。应先把 `trigger_hit` 落盘，再后台继续做建单/派发/回写；否则一次慢建单就会把 `scan` 请求和 worker 一起拖死。
- schedule 真相源不能只记“命中过了”，必须尽快补齐：
  - `assignment_ticket_id`
  - `assignment_node_id`
  - `last_trigger_at`
  - `last_result_status`
  否则计划明明已经在任务图里建出节点，schedule detail 仍会显示“待触发”，用户无法继续追踪。
- 半成功现场要允许恢复。只要任务图节点已经带有 `source_schedule_id + trigger_instance_id`，后续扫描或 detail 读取就应能反查这些字段，把 schedule trigger 回写补齐，而不是一直卡在 `trigger_hit`。
- 只靠 `scan` 或手工打开 detail 做恢复不够稳。worker 本身也要周期扫最近的 `trigger_hit/queued/running/dispatch_failed` 非终态 trigger，把丢失的后台处理线程重新挂起来；否则计划会长期卡在“已建单待调度/运行中”，只有人工点开页面时才继续推进。
- schedule trigger 恢复不能无差别地把所有 `dispatch_failed` 一次性重放。像 `[持续迭代] workflow` 这种被 `smoke baseline guard` 挡下来的 trigger，如果每轮都立刻重试，会把 `schedules.jsonl` 刷爆，还会把真正需要优先恢复的 `queued` trigger 挤掉。恢复顺序应该优先 `trigger_hit/queued/running`，`dispatch_failed` 至少要加冷却窗口。
- schedule trigger 恢复在同一轮里不能并发起太多线程，尤其是这些 trigger 都指向同一张全局任务图时。一次性恢复多条会把任务图快照、run 记录回写和 work-record index 一起挤到同一把 SQLite 锁上，最终表现成 `database is locked`、`/api/status` 超时和恢复线程互相放大。更稳的默认是每轮只启动极小批次恢复，再由下一轮继续补。
- 对同一条 `[持续迭代] workflow` 来说，旧的 backlog trigger 没必要按历史顺序全部补跑。worker 恢复更稳的口径是“每个 schedule 只恢复最新的一条非终态 trigger”，否则昨天下午的旧唤醒、旧自迭代会重新塞满 ready 队列，把真正最新的一轮挤到后面。
- 当 `workflow` 自迭代节点不是业务失败，而是被系统按“运行句柄缺失 / workflow 已重启”收口时，也要像正常失败一样续挂下一轮 `[持续迭代] workflow`。否则站点虽然能被 watchdog 拉回，但 7x24 连续推进会在这类重启现场悄悄断链。
- `create_node` 和 `dispatch` 也必须对 `trigger_instance_id` 做幂等保护。否则同一 trigger 会生成多个 assignment node，甚至把 dispatch 打到与计划详情回写不同的节点上，最终留下“计划详情还指着 ready 节点，真实执行却跑在另一个节点”的错位现场。
- 生产 smoke 验收时，要把用户可见的 `GET /api/schedules/{id}` 详情当成 done_definition 的真相源，而不是只看本地 raw detail。现网里 raw detail 可能还停在 `queued`，但 HTTP detail 已经把 assignment/result 富化到 `running/failed`；同时接口本身也可能有瞬时抖动，所以验收脚本应采用较长超时和重试，并把 raw/http 偏差记成警告而不是直接误判失败。
- `schedule -> assignment` 桥接层要给同一 `trigger_instance_id` 固定一个稳定 `node_id`，并优先在已知全局主图 ticket 内做恢复扫描；不要每次都全局扫所有任务目录，更不要把“随机新建节点”当成默认恢复策略。
- `run_schedule_smoke_baseline` 这类自测入口不能直接内联调用 `_process_schedule_trigger_async` 并换一把 thread key。它必须复用正常的 `_start_schedule_trigger_processing` 门闩，否则同一 trigger 会绕过进程内锁，重新触发建单/派发竞争。
- 读取任务中心全局主图时，若数据库里已经绑定了 canonical ticket，就先直接验证并复用该 ticket；不要每次 list/dashboard 都重新全量扫描所有 workflow-ui 图和全部节点，否则面板很容易从“数据存在”退化成“接口超时后显示 0”。
- 如果要做 `workflow` 的长期自迭代，不要在 assignment 完成后立即递归再派发一条同类节点；更稳的做法是把“下一轮”写成一个滚动的一次性 schedule，让系统在几分钟后再唤醒，既不断链，也避免瞬时热循环。
- 对 pm/`workflow` 这类自迭代计划，默认要走低频、分钟粒度、短上下文、低风险目标；不要一上来就做高频自治。
- `[持续迭代] workflow` 这类自迭代 schedule 如果挂在 `smoke baseline guard` 后面，可能在计划命中后直接被拦成 `dispatch_failed`，即使版本计划和唤醒文案都已经写对。要保持 7x24 连续推进，不能只依赖这一条滚动 schedule，还要保留一条更低频的 pm 保底唤醒，必要时允许 PM 直接往任务中心补一条当前版本任务。
- `smoke baseline guard` 不能只按 `assigned_agent_id=workflow` 粗暴套到所有计划上。真正需要被 smoke 约束的是 `[持续迭代] workflow` 这类滚动自迭代计划；`pm持续唤醒` 这种保底恢复入口必须继续允许建单/补链，否则一旦 smoke 失败，主链和保底链会一起断。

## 已踩过的坑
- 坑 1：schedule worker 在 `trigger_hit` 之后同步调用慢建单/慢派发，HTTP `scan` 超时了，但 trigger/plan 状态还没来得及更新，现场就会留下“节点已建出来，schedule detail 却还是 pending”的半断裂状态。
  - 避免方式：把建单/派发改成后台线程；trigger 命中只负责落最小必要留痕。
- 坑 2：prod 重启后，已经跑起来的自迭代节点可能被任务中心按“运行句柄缺失”回收成失败；如果 schedule 没有恢复逻辑，就会继续显示空 assignment refs。
  - 避免方式：后续扫描对 `trigger_hit/queued/running` 且 assignment refs 为空的触发实例做恢复检查，优先从任务图节点里的 `source_schedule_id/trigger_instance_id` 反查补齐。
- 坑 3：异步补偿或重复调度如果没有按 `trigger_instance_id` 去重，同一条一次性 smoke trigger 会被连续建出两个节点，计划表头和 trigger 明细又只保留最后一次回写，结果就是页面上显示的 assignment node 仍是 `ready`，而真正被 dispatch 的已经是另一条节点。
  - 避免方式：`create_node` 前先反查同 trigger 的既有节点；`dispatch` 前确认计划/trigger 指向的节点和目标节点一致，否则先修正回写再派发。
- 坑 4：smoke baseline 为了“补一脚恢复”而直接内联调用 `_process_schedule_trigger_async`，还故意拼了一个 `::smoke-inline` 的新 thread key，结果同一 trigger 的后台线程门闩完全失效，重复建节点和重复 dispatch 都会被放大。
  - 避免方式：smoke 和正式 scan 一律只走 `_start_schedule_trigger_processing`；如果需要补偿恢复，也要复用同一个 `trigger_instance_id` 对应的 thread key。
- 坑 5：dashboard / assignments 每次都为了解析 canonical workflow-ui 全局主图而重新全量扫描所有候选图和全部节点，在历史任务堆起来后会把接口拖到 20 秒级，前端最终表现成“活跃小伙伴 0、运行中任务 0、定时任务像是没有”。
  - 避免方式：先走已绑定 ticket 的轻量验证快路径；只有绑定缺失或失效时，才退回全量候选扫描。
- 坑 6：prod 恢复后，[持续迭代] workflow 虽然能成功命中，但如果当前 smoke baseline 保护条件没过，trigger 会直接写成 `dispatch_failed / smoke baseline last run not passed`，结果是计划看起来在跑、实际上没有给 PM 建出下一轮任务。
  - 避免方式：给 `workflow` 额外保留一条低频 pm 保底唤醒；同时在需要时允许 PM 直接往任务中心补一条带版本计划上下文的 `P0 ready` 任务，而不是死等滚动 schedule 自己穿过 smoke guard。
- 坑 7：如果 guard 只看 `assigned_agent_id=workflow`，连 `pm持续唤醒 - workflow 主线巡检` 这种保底计划也会一起被拦成 `dispatch_failed`，表面上 future trigger 还在，实际上能真正补链的入口已经全部失效。
  - 避免方式：把 guard 范围收窄到真正的 `[持续迭代]` / `continuous-improvement-report.md` 计划；保底唤醒只负责巡检、续挂和补单，不参与这层 smoke 封禁。
- 坑 8：如果只在 `run_schedule_scan` 里补偿 trigger，worker 一旦在 `trigger_hit -> create_node -> dispatch_requested` 之间重启，旧 trigger 会一直停在 `queued/running` 的中间态；后续虽然能在任务图里看到 node，但计划详情和下一轮接力都不会自动往前走。
  - 避免方式：让 worker 每轮都额外扫一遍最近的非终态 trigger，并基于 `trigger_instance_id` 重挂 `_start_schedule_trigger_processing`；终态 `succeeded/failed` 的 trigger 则直接跳过，避免无意义重试。
