# workflow-pm-wake-summary-20260412-232846

- conclusion: `继续推进`
- version_progress: `工程质量探测`
- lane: `工程质量探测`
- lifecycle_stage: `基于基线测试`
- memory_ref: `.codex/memory/2026-04/2026-04-12.md`

## 现场结论
- `healthz=200 @ 2026-04-12T23:25:21+08:00`
- `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / push_block_reason=- / next_push_batch=待切批`
- `pm-main` 与 `../workflow_code` 当前都对齐 `a3e5eda`
- `prod` 升级门禁为 `current_version=candidate_version=20260412-211849 / candidate_is_newer=false / request_pending=false / drain_active=false / blocking_reason=存在运行中任务，暂不可升级`
- 当前 live 出口为：`23:20 patrol running + 21:53 mainline ready + 23:31 mainline future + 23:40 patrol future`
- 当前 `running_task_count=1 / queued_task_count=1 / active_agent_count=1`
- 当前不是 `0 running + ready pileup` 的假健康，所以我这轮不补新的主线入口，也不调用 `/api/runtime-upgrade/apply`

## 新增进展
- 本轮推进项切到 `工程质量探测`：我确认 `workflow_mainline_handoff_pending` 已从短时压后升级成跨多轮的持久在线风险
- `21:40` 保底节点 `node-sti-20260412-e95dfb12` 直到 `2026-04-12T23:20:54+08:00` 才以 `Codex 连接中断` 收尾，并在收尾时把下一次主线续挂到 `2026-04-12T23:31:00+08:00`
- 老主线 `node-sti-20260412-8e017392 / [持续迭代] workflow / 2026-04-12 21:53:00` 自 `2026-04-12T21:53:33+08:00` 起一直保持 `ready`
- `22:00 / 22:20 / 22:40 / 23:00` 的 patrol ready 节点都被后续 patrol 命中覆盖删除，说明保底链一直在滚动，但 mainline 一直没有拿到运行槽
- 当前 `23:20` patrol `node-sti-20260412-ce7fb40e` 已在 `2026-04-12T23:22:28+08:00` 被真实 dispatch；当前 run `arun-20260412-232229-55191d` 仍是 live running，`provider_pid=64748 / latest_event_at=2026-04-12T23:26:15+08:00`

## 新风险
- 同一 `workflow` agent 的串行门禁当前持续让 patrol 优先占槽，主线推进已被压后超过 `90` 分钟
- 老 ready mainline 仍带着旧 snapshot：`baseline=prod=20260412-201138`；但 `/api/schedules` 里的主线 future 已经推进到 `baseline=prod=20260412-211849`
- 如果当前 `23:20` patrol 收尾后，`21:53` ready mainline 仍没有在 `23:31` future mainline 或 `23:40` patrol 之前被 dispatch，这条风险就要升级为受支持的 `schedule refresh/update` 或 helper 工程治理任务

## 为什么这轮不直接治理
- 当前 `23:20` patrol 是真 running live task；我如果在它执行期间重写 schedule，会增加现网扰动，但不会消除“同 agent 只有一个运行槽”的根因
- 当前 `prod` 仍同时保留 `ready + future` 的主线出口，所以这不是静默断链，不满足补新主线入口的条件
- 这轮最安全的动作是先冻结证据，把“长期 handoff 饥饿”明确记成 `V1-R2` 的新现场，再由下一轮在当前 patrol 收尾后决定是否进入 `schedule refresh/update`

## 并行判断
- `parallel_candidate_count=1`
- `parallel_dispatched_count=0`
- `active_helper_tasks=[]`
- `parallel_block_reason=当前 23:20 patrol 真 running；在现网 handoff 是否自动恢复还没确认前，我不并发引入 helper 扰动。若 21:53 / 23:31 主线在本轮收尾后仍继续饥饿，下一轮优先 refresh workflow_devmate 并派发工程治理切片`

## 下一步
- 主线 ready: `node-sti-20260412-8e017392 / [持续迭代] workflow / 2026-04-12T21:53:00+08:00`
- 主线 future: `[持续迭代] workflow -> 2026-04-12T23:31:00+08:00`
- 保底 future: `pm持续唤醒 - workflow 主线巡检 -> 2026-04-12T23:40:00+08:00`
- 下一轮优先确认当前 `23:20` patrol 收尾后，`21:53` ready mainline 是否终于被 dispatch；若仍没有，就把“patrol 长任务持续压后 mainline”升级成 `V1-R2` 的最高优先级治理项
