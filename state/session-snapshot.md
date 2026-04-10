# Session Snapshot

## Entries

### 2026-04-07T12:18:46+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你明确要求当前单人阶段停止使用 `dev/pm-main`，改成直接跟踪 `main`，并继续把服务端 `WMI` 高占比压下去。
- delta_validation: 我已无损归档旧 `.repository/pm-main`、重建跟踪 `main` 的新工作区，补上设备路径/WMI 快路径和 runtime-config 回写修复，完成行数门禁、两项定向验收、`workflow gate`、assignment/dashboard 延迟测量、`test` 部署和 `prod` candidate 刷新。

### 2026-04-07T12:22:00+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你进一步明确要求后续不同小伙伴的代码也统一直接合入 `../workflow_code/main`，保证所有生效代码都在同一条主线上起作用。
- delta_validation: 我已把 `AGENTS.md` 和 `协作约定.md` 的协作口径补成“各工作区开发验证，最终统一合入 `workflow_code/main`”。

### 2026-04-07T13:10:00+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你反馈顶层 `run_workflow.bat` 启动失败，说明当前最影响使用的不是代码主线，而是 PM 顶层便捷入口的现网可用性。
- delta_validation: 我已定位并修掉两层阻塞：一是 `.running/prod/.runtime/state/runtime-config.json` 残留旧 `D:` 路径，二是 deployed `start_workflow_env.ps1` 缺少 `Resolve-WorkflowStartSourceRoot` 导致递归 `.running/prod/.running/...`；同时把 `run_workflow.bat` 的 prod 启动默认改成 `-SkipBackfill`，现已验证 `8090/healthz` 恢复正常。

### 2026-04-07T13:52:42+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮通过任务中心真实派发 `生产 smoke 基线 20260407-1350`，验收口径明确要求以“计划详情可见的 trigger、assignment refs、最近结果状态和回写时间”为准，并且最终只收一个 JSON 交付。
- delta_validation: 我已核对 prod 的 `/api/schedules/sch-20260407-a07b3094`、`/api/assignments/asg-20260407-103450-fb8ba8/status-detail?node_id=node-sti-20260407-8d910bd6`、`.running/control/runtime/prod/logs/events/schedules.jsonl` 和 `.running/control/runtime/prod/.test/schedule_smoke_baseline.latest.json`，确认这次 13:50 smoke 通过，并把报告落到 `logs/runs/production-smoke-baseline-20260407-1350-20260407-135242.md`。

### 2026-04-07T14:04:32+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 这轮真实派发的 `[持续迭代] workflow / 2026-04-07 10:43:00` 要求我按 prod 真相推进 active 版本最高优先问题，并显式保证下一轮连续入口不断链。
- delta_validation: 我已把焦点收窄到 `V1-P0 / V1-P1` 的自迭代补链问题，修正 `verify_assignment_stale_running_self_iteration.py` 的隔离 runtime 假 agent 注入方式，随后完成 `verify_self_iteration_backup_schedule_on_smoke_block.py`、`verify_assignment_stale_running_self_iteration.py` 与 `workflow gate` 复核；其中两条定向验收通过，`workflow gate` 报告额外保留了一个与本轮补链无关的 `developer_workspace_bootstrap=workspace_dirty` 子项，并同步更新了 `docs/workflow/governance/PM版本推进计划.md` 与 `logs/runs/self-iteration-backup-schedule-20260407-140432.md`。

### 2026-04-07T14:12:09+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你继续要求我优先真实 `7*24` 连续推进，不接受把修复只留在本地；而现网在这轮处理中也暴露出重复保底 schedule 会把全局主图再次搅乱的风险。
- delta_validation: 我已把这组自迭代补链修复提交为 `a856e5c fix(schedule): keep workflow backup wake queued` 并推到 `workflow_code/main`，随后完成 `test` 部署和 `prod candidate 20260407-141033` 刷新；现网侧也已把重复保底 schedule 收成单条 future 入口。当前 `/api/status` 显示 `[持续迭代] workflow` 已自动把下一轮续到 `2026-04-07T14:25:00+08:00`，保底入口保留到 `2026-04-07T14:41:00+08:00`。

### 2026-04-07T14:29:56+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你明确要求后续不要让我长期单打独斗，并说明之后会在当前窗口持续追问版本状态。
- delta_validation: 我已把这条协作口径写进 `state/user-preferences.md`，并实际在现网全局主图里给 `workflow_devmate / workflow_bugmate / workflow_testmate / workflow_qualitymate` 各挂了一条并行任务，交付目标统一回到 `workflow`；现场也暴露出一个新的工程问题：并行小伙伴执行链本身还不够稳，派发后 prod 一度掉线。我已先恢复看门狗与 `8090` 服务，后续会优先把“小伙伴执行稳定性”收成版本状态的一部分，而不是只盯主线代码任务。

### 2026-04-07T15:01:01+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你追问“下一次运行是什么时候，我看 token 没有消耗”，要求我给出精确到当前现场的运行口径，而不是沿用上一轮记忆。
- delta_validation: 我已重新核对 `prod` 的 `/healthz`、`/api/status`、`/api/schedules`、`/api/assignments/asg-20260407-103450-fb8ba8/graph`、Windows 进程和任务审计，确认原来的 `14:25` 与 `14:41` 已经触发但只留下两个 `ready` 节点、没有真实 provider 进程，所以 token 不增长；随后我用 `pm-main` 已验证主线里的 self-iteration helper 直接回写 live prod schedule，把新的主线 future trigger 补到 `2026-04-07T15:29:00+08:00`，新增正确命名的保底唤醒到 `2026-04-07T15:59:00+08:00`。我还试了受支持的 `POST /api/assignments/asg-20260407-103450-fb8ba8/dispatch-next`，但 20 秒内未返回且没有新 provider 进程，说明当前“无 token 消耗”的直接阻塞已经收窄到 dispatch 路径本身。 

### 2026-04-07T15:05:16+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮追问的核心不只是“下一次运行几点”，而是要我把“为什么不耗 token”从现象追到真实执行层，并当场把主线重新拉起来。
- delta_validation: 我已先删除空白保底 ready 节点 `node-sti-20260407-8a302e24`，把 future trigger 收口为主线 `2026-04-07T15:30:00+08:00` 与保底 `2026-04-07T15:59:00+08:00`；随后绕过 live prod 上卡住的 `dispatch-next` HTTP 壳，直接用本地 `workflow_app.server.bootstrap.web_server_runtime.dispatch_assignment_next(root, ...)` 对当前 prod runtime 做一次止血派发，成功拉起 `run_id=arun-20260407-150401-e4e9e8`。当前 `/api/status` 已显示 `running_task_count=1`、`workflow` 主线节点 `node-sti-20260407-e6a6162e` 为 `running`，说明 token 现在应该开始重新消耗；现网剩余风险主要是 schedule 文案显示仍有编码漂移，但不阻塞当前主线执行与 future trigger 保留。

### 2026-04-07T15:08:59+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你问的是“现在为什么不耗 token”，所以我不能把刚进入 `starting/running` 的中间态当最终结论，必须继续盯到 provider 是否真的拉起。
- delta_validation: 我追加核对了 `run_id=arun-20260407-150401-e4e9e8` 的 `run.json`、Windows 进程与 `/api/status`，确认这次手动派发虽然写下了 `dispatch` 审计和 `run_id`，但 `provider_pid` 一直是 `0`、没有任何 `codex exec` 进程真正出现，随后 `workflow` 节点又被任务中心收口成失败；因此当前 token 依然不会继续消耗。现网当前准确状态是：主线 future trigger 仍保留在 `2026-04-07T15:30:00+08:00`，保底 future trigger 保留在 `2026-04-07T15:59:00+08:00`，`healthz` 与看门狗仍正常，真正未收口的是“provider 为什么没有启动”的执行链问题。

### 2026-04-07T15:36:37+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你继续追问“好像没触发”，说明你需要的是“15:30 这次到底有没有命中”的一句准话，而不是我继续用上一条中间态解释。
- delta_validation: 我刚按 `2026-04-07 15:35~15:36 +08:00` 的 live prod 真相重新核对了 `/api/status`、`/api/schedules` 和全局主图 `asg-20260407-103450-fb8ba8`。结论是：`sch-20260407-4c67199b` 确实已经在 `2026-04-07T15:30:00+08:00` 命中，且新建了 `ready` 节点 `node-sti-20260407-03861bea`；但它只停在“已建单待调度”，没有真正拉起 provider，所以你体感上会觉得“像没触发”。当前真正保留的下一次 future trigger 只剩保底唤醒 `sch-20260407-d7b8f1d6 -> 2026-04-07T15:59:00+08:00`。

### 2026-04-07T16:12:30+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮追问“那需不需要修复一下”，实际是在要求我别停在现场解释，而要把 `dispatch -> provider` 这层静默失败真正收口成可恢复、可验证的工程修复。
- delta_validation: 我已经在 `.repository/pm-main` 补上 assignment 执行链修复：`_assignment_execution_worker` 外侧新增 top-level fail-closed guard，能把 `provider_start` 前异常显式写成 `provider_start_failed` 并把 run/node 收口成失败；同时把 `pm-manual-recovery` 的执行线程改成非 daemon，避免一次性本地 Python 宿主退出后把后台线程直接带死，留下 `run.json=starting/provider_pid=0/events 只有 dispatch` 的假运行。定向验证已通过：`python scripts/acceptance/verify_assignment_worker_guarded_fail_closed.py` 与 `python scripts/acceptance/verify_assignment_manual_recovery_thread_mode.py` 均返回 `ok=true`。

### 2026-04-07T16:34:30+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你继续强调“7*24 小时是系统运行的核心，务必要保证可靠性”，这轮要求已经从“把 bug 修掉”升级成“把修复真正推进到可发布候选，并顺手把会卡住后续协作的 Git/门禁链路也一并收口”。
- delta_validation: 我先修掉 `developer_workspace_bootstrap` 的 Git 误判：目标目录如果只是嵌在上层 PM 仓里，不再被认成“自己已经是 Git 仓”，这样 `workflow gate` 里的 `workspace_dirty` 假失败被收掉；同时我还发现上一次 gate 已把当前 `.repository/pm-main` 的 `origin` 误改成了隔离 fixture 仓，已手动修回真实 `workflow_code`。随后我把本轮修复提交为 `0e10afa fix(workflow): harden assignment recovery dispatch`，推回本地 `workflow_code/main`，并将 `workflow_code` 配成 `receive.denyCurrentBranch=updateInstead` 以支持各工作区直接回推 `main`。`test` 环境与 `prod candidate` 现已刷新到 `20260407-163227`，`test gate` 通过；但 `workflow_code -> GitHub origin/main` 因当前机器连不上 `github.com:443` 尚未推上去，现网 `prod` 仍停在旧版本 `20260407-121719`。

### 2026-04-07T16:50:17+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 15:59 的保底唤醒这次不是让我复述旧结论，而是要我按 live prod 真相回答“主链现在有没有断、下一步到底盯什么”，并且交付固定的 `workflow-pm-wake-summary`。
- delta_validation: 我已重新核对 `.running/control/envs/prod.json`、`.running/control/instances/prod.json`、`/healthz`、`/api/status`、`/api/schedules`、`/api/assignments/asg-20260407-103450-fb8ba8/graph`，以及 `node-sti-20260407-c2b6a494` 和 `node-sti-20260407-68b5075a` 的 `status-detail`。结论是：当前 prod 已运行在 `20260407-163227`；15:59 保底唤醒节点已真实 `provider_start` 并处于 `running`，16:06 的 `[持续迭代] workflow` 节点已建单 `ready`，所以主链此刻未断，但“当前运行节点结束后 ready 节点能否自动接棒”仍是下一步最该盯的 live 风险。

### 2026-04-07T16:54:35+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你已经明确授权“升级生产环境然后开始可靠的 7*24 小时运行”，这轮要求我不仅要把候选切进 `prod`，还要把“新版本是否真的把旧 ready 队列拉起来”钉成现网证据。
- delta_validation: 我已通过 `POST /api/runtime-upgrade/apply` 把 live `prod` 从 `20260407-121719` 升到 `20260407-163227`；`.running/control/envs/prod.json`、`.running/control/instances/prod.json` 和 `.running/control/prod-last-action.json` 三处版本/动作已一致。升级后我继续核对了 `/api/status`、`/api/assignments/asg-20260407-103450-fb8ba8/graph`、`run.json`、`events.log` 和 `Win32_Process(ProcessId=5496)`，确认旧版遗留的 `node-sti-20260407-c2b6a494` 已被新版本自动接成真实 `running`，并且 `node-sti-20260407-68b5075a` 仍保持 `ready` 待接棒；对应运行记录 `arun-20260407-164648-920813` 已出现 `provider_start` 与 `provider_pid=5496`，说明这轮现网已经从“只建单待调度”恢复到真实 7x24 运行面。

### 2026-04-07T17:26:24+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮的验收重点已经从“主链会不会断”继续收窄到“现网里旧 self-iteration / backup schedule 为什么还显示空白或问号”，也就是要求我把持续唤醒链的用户可见真相一起收住。
- delta_validation: 我已在 `pm-main` 的 `schedule_service.py` 补齐 schedule 文本 repair 的读写链，新增 `scripts/acceptance/verify_schedule_text_repair.py` 并通过；随后又用这版代码直接读取 live prod 的 `.running/control/runtime/prod/state/workflow.db`，确认 `sch-20260407-d7b8f1d6 / sch-20260407-4c67199b` 的 schedule list/detail/calendar 都能恢复成正确中文。当前主线节点 `node-sti-20260407-b63812e7` 仍在 `running`，下一次保底/主线入口保留在 `2026-04-07T17:40:00+08:00 / 2026-04-07T17:45:18+08:00`。

### 2026-04-07T17:41:31+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 这轮真实派发的 `pm持续唤醒 - workflow 主线巡检 / 2026-04-07 17:40:00` 要求我只按 live prod 真相判断主线是否还保有 future 入口，并在缺口出现时现场补链。
- delta_validation: 我已重新核对 `docs/workflow/governance/PM版本推进计划.md`、`docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`、`/healthz`、`/api/status`、`/api/schedules`、`/api/assignments/asg-20260407-103450-fb8ba8/graph`、当前节点 `status-detail` 与最近自迭代节点 `status-detail`。结论是：`prod` 仍在 `20260407-163227` 正常运行，`node-sti-20260407-fe7d16fe` 已于 `2026-04-07T17:40:30+08:00` 真实 `provider_start`，`[持续迭代] workflow` 未来入口 `sch-20260407-20001ab4` 仍保留到 `2026-04-07T17:45:00+08:00`，当前无需现场补链；下一次建议唤醒时间收口到 `2026-04-07T17:45:00+08:00` 这轮主线触发后再看 handoff 真相。

### 2026-04-07T17:45:02+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 我在交付前又做了一次临门 live 复核，避免把“马上要触发 17:45”误写成最终真相；你这类持续唤醒巡检更需要精确到当前分钟的绝对时间线。
- delta_validation: 我在 `2026-04-07T17:45:02+08:00` 再次核对 `/api/status`、`/api/schedules`、`/api/assignments/asg-20260407-103450-fb8ba8/graph` 与 `node-sti-20260407-6e7a76a8` 的 `status-detail`。结论是：17:45 的 `[持续迭代] workflow` 已命中并建出 `ready` 节点 `node-sti-20260407-6e7a76a8`，当前全局主图已变成 `1 running / 1 ready`；因此即使 future trigger 已转化成当前任务，主线入口依然存在，本轮仍无需手工补链。下一次建议唤醒时间收口到当前 17:40 运行节点完成后，优先复核这条 `17:45` ready 节点何时被真实 dispatch。

### 2026-04-07T17:42:51+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你看到界面像是“跑到 17:30 就停了”，说明你当前更关注的是持续唤醒链的真实时间线，而不是单纯看某个 schedule 的更新时间字段。
- delta_validation: 我已重新核对 `/api/status`、`/api/schedules`、`asg-20260407-103450-fb8ba8` 的 audit/node/run 真相。结论是：`17:30` 不是停住，而是 `17:10` 那轮 `[持续迭代] workflow` 在 `2026-04-07T17:30:14+08:00` 成功收尾并在 `17:30:33` 把下一轮主线/保底计划回写为 `17:45 / 17:40`；随后保底计划 `pm持续唤醒 - workflow 主线巡检` 已在 `2026-04-07T17:40:00+08:00` 命中，并拉起 `node-sti-20260407-fe7d16fe` 与 `run_id=arun-20260407-174021-f36f5d`。当前 `run.json` 显示 `provider_pid=35656`、`status=running`，而用户可见 API 仍显示下一条主线入口 `sch-20260407-20001ab4 -> next_trigger_at=2026-04-07T17:45:00+08:00`。

### 2026-04-07T18:02:22+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮继续要求真实 worker 只在当前工作区内推进 active 版本最高优先问题，并且交付必须既有证据、又不断掉下一轮唤醒链。
- delta_validation: 我已把 `schedule metadata repair` 从 `schedule_service.py` 中再拆出 `src/workflow_app/server/services/schedule_text_repair.py`，修正 `scripts/acceptance/verify_schedule_text_repair.py` 的当前时间依赖，随后完成 `py_compile`、`verify_schedule_text_repair.py`、`verify_dashboard_schedule_preview.py` 与 `workflow gate`。代码已提交 `7e2881a` 并推回 `workflow_code/main`，`test` 与 `prod candidate` 已刷新到 `20260407-180045`；截至 `2026-04-07T18:02:22+08:00`，live prod 仍保留 `18:04` 的 `[持续迭代] workflow` 与 `18:34` 的保底唤醒入口，因此本轮没有再额外挂协作任务。

### 2026-04-07T19:21:04+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 这轮真实派发的是 `生产 smoke 基线 20260407-1918 / 2026-04-07 19:18:00`，验收口径很收敛，只看 `schedule -> 建单 -> 自动派发 -> 计划详情回写` 这条真实执行链有没有闭环。
- delta_validation: 我已交叉核对 `/api/schedules/sch-20260407-aac1b0d1`、`/api/assignments/asg-20260407-103450-fb8ba8/status-detail?node_id=node-sti-20260407-0bed8c8d`、`.running/control/runtime/prod/logs/events/schedules.jsonl`、`.running/control/runtime/prod/.test/schedule_smoke_baseline.latest.json` 和 `C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/audit/audit.jsonl`。结论是：这次 `19:18` smoke 已完成 `trigger_hit -> create_assignment_node -> dispatch_requested`，计划详情可见 `asg-20260407-103450-fb8ba8 / node-sti-20260407-0bed8c8d`、`recent_trigger.result_status=running`、`updated_at=2026-04-07T19:19:01+08:00`；正式报告已落到 `logs/runs/production-smoke-baseline-20260407-1918-20260407-192104.md`。

### 2026-04-07T19:33:44+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你要求我把 7x24 的主线状态、自动升级口径和小伙伴是否真正参与过都说成 live 真相，而且记忆里的 `next` 要直接写出下一次触发时间，方便你判断闭环有没有继续跑。
- delta_validation: 我已重新核对 `prod` 的 `/healthz`、`/api/status`、`/api/schedules`、`/api/runtime-upgrade/status`、`.running/control/envs/prod.json`、`.running/control/instances/prod.json`、`.running/control/prod-last-action.json`、当前运行 `run.json` 与 `events.log`。结论是：`prod` 已运行在 `20260407-192451`，这版就是我通过现有无痛升级链路自动 apply 上去的；当前主线节点 `node-sti-20260407-e17eaf89` 对应 `run_id=arun-20260407-192706-a88570` 仍在真实执行，`provider_pid=1640`、`latest_event_at=2026-04-07T19:30:40+08:00`；下一次主线/保底触发分别是 `2026-04-07T19:57:00+08:00` 与 `2026-04-07T20:27:00+08:00`。四个小伙伴的工作区都存在且带 `.codex`/`AGENTS.md`，但今日日记 `2026-04-07.md` 都还没创建；全局 ticket 里他们在 `2026-04-07T14:22:51+08:00` 确实被派发过，只是后续分别落成 `exit=1`、`^C` 或 `recover stale running node without live execution`，所以没有留下自己的记忆增量。

### 2026-04-07T19:34:19+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 这轮真实派发的 `[持续迭代] workflow / 2026-04-07 18:21:00` 已经把重点重新压回 `V1-P0 / V1-P1` 的 live 真相：18:21 那次主线曾被 `smoke baseline expired` 卡死，而现在 prod 又已经切到 `20260407-192451`，我需要在不中断 7x24 接力的前提下，把“过期 smoke 不再硬拦主线”和“升级前先核真相”这两件事收进代码、验收和候选链。
- delta_validation: 我已在 `.repository/pm-main` 验证并保留这组修复：`verify_schedule_smoke_guard_scope.py` 确认自迭代节点在 `smoke baseline expired` 时会走 `degraded_expired_smoke`，`verify_assignment_self_iteration_plan_reference.py` 确认自迭代/保底计划模板已补上 `/api/runtime-upgrade/status -> /api/runtime-upgrade/apply` 检查与 `next` 时间要求；随后又跑通 `py_compile`、`python scripts/quality/check_workspace_line_budget.py --root .` 与 `workflow gate`，并将 `test/prod candidate` 刷到 `20260407-193228`。截至 `2026-04-07T19:34:19+08:00`，live `prod` 上 `node-sti-20260407-e17eaf89` 的 run `arun-20260407-192706-a88570` 仍在运行，下一次主线/保底入口保留在 `2026-04-07T19:57:00+08:00 / 2026-04-07T20:27:00+08:00`；但 `/api/runtime-upgrade/status` 仍会在 `/api/status` 显示 `1` 条运行任务的同时给出 `can_upgrade=true`，所以我这轮只刷新 candidate，不直接升级 `prod`。

### 2026-04-07T20:30:37+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 这轮真实派发的 `pm持续唤醒 - workflow 主线巡检 / 2026-04-07 20:26:00` 要求我只按 live prod 真相决定是否升级、是否补链，并把下一次主线时间写成可直接交付的结论。
- delta_validation: 我已读取 `docs/workflow/governance/PM版本推进计划.md`、`docs/workflow/requirements/需求详情-pm持续唤醒与清醒维持.md`，并交叉核对 `/api/status`、`/api/runtime-upgrade/status`、`/api/schedules`、`/api/assignments/asg-20260407-103450-fb8ba8/graph`、`/api/assignments/asg-20260407-103450-fb8ba8/status-detail?node_id=node-sti-20260407-6085ec1f`、`.running/control/envs/prod.json`、`.running/control/instances/prod.json`、`.running/control/prod-last-action.json`、`C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/nodes/node-sti-20260407-6085ec1f.json`、`C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/runs/arun-20260407-202650-c24346/run.json` 与 `events.log`。结论是：截至 `2026-04-07T20:30:37+08:00`，prod 仍运行在 `20260407-200414`，`running_task_count=1`、`can_upgrade=false`，当前保底节点仍在运行，而 `[持续迭代] workflow` 仍保留 `next_trigger_at=2026-04-07T20:37:00+08:00`，所以本轮无需补链或升级，只需输出证据并把 `20:37` 写入记忆 `next`。

### 2026-04-07T21:16:36+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 这轮 `21:07` 保底巡检不只要回答“现在能不能升级”，还要在 `[持续迭代] workflow` 的 `next_trigger_at` 已经被消费为空时，把主链是否仍连着、下一次保底时间是什么，钉成明确真相。
- delta_validation: 我已复核 `/api/status`、`/api/runtime-upgrade/status`、`/api/schedules`、当前 running/ready 节点文件、`arun-20260407-210748-60d88b/run.json`、`audit.jsonl` 与 `.running/control/runtime/prod/logs/events/schedules.jsonl`。截至 `2026-04-07T21:16:36+08:00`，prod 仍是 `20260407-200414`，`running_task_count=1`、`can_upgrade=false`；主线当前是 `node-sti-20260407-3ec1c5ec=running`、`node-sti-20260407-101db522=ready`。我已额外通过 `POST /api/schedules/sch-20260407-5ef5e5c8` 把保底巡检重挂到 `2026-04-07T21:37:00+08:00`（`audit_id=saud-20260407-1433d722`），避免 future 保底时间继续空白；同时也观察到 `node-sti-20260407-101db522` 在 `21:11:39~21:16:33` 间反复出现 `dispatch_requested -> trigger_resume_requested -> recover_assignment_node`，但仍未真正进入 `running`，这是下一轮最该追的风险。

### 2026-04-07T21:47:34+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 这轮 `21:37` 保底巡检要求我只按 live prod 真相判断是否升级或补链，而且你依然需要从记忆里的 `next` 直接看出主线/保底有没有继续滚动。
- delta_validation: 我已复核 `/healthz`、`/api/status`、`/api/runtime-upgrade/status`、`/api/schedules`、`.running/control/envs/prod.json`、`.running/control/instances/prod.json`、`.running/control/prod-last-action.json`、`C:/work/J-Agents/.output/tasks/asg-20260407-103450-fb8ba8/task.json`、当前 `running/ready` 节点文件、`arun-20260407-214401-a33916/run.json`、`arun-20260407-212312-7e0bee/run.json`、`audit.jsonl` 与 `schedules.jsonl`。其中 assignment graph / status-detail HTTP 接口在本轮 20 秒窗口内仍会超时，所以我回退到 task/nodes/runs/audit 文件真相；这些文件与 `/api/status`、`/api/schedules` 一致。截止 `2026-04-07T21:47:34+08:00`，prod 仍是 `20260407-200414`、`candidate=20260407-213849`、`running_task_count=1`、`can_upgrade=false`；当前主链保持 `node-sti-20260407-a7fd93ea=running`、`node-sti-20260407-cb9fc7de=ready`，而 `[持续迭代] workflow` / 保底巡检的 future 入口已经自动滚到 `2026-04-07T22:14:00+08:00 / 2026-04-07T22:44:00+08:00`，所以本轮无需再补链或升级。我已把结论落到 `logs/runs/workflow-pm-wake-summary-20260407-214734.md` 并同步写进今日日记。

### 2026-04-07T22:00:03+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮继续要求我按 live prod 真相推进 `V1-P0 / V1-P1`，在仍有 running 任务时不要误升级，而要把当前最影响 7x24 连续性的恢复风暴收成可发布补丁。
- delta_validation: 我已先钉实旧版 `prod=20260407-200414` 上 `node-sti-20260407-cb9fc7de` 在 `21:39:42~21:51:45` 间反复刷 `dispatch_requested -> trigger_resume_requested -> recover_assignment_node`，随后把 `runtime_upgrade` running gate fallback、`schedule` busy-slot quiet wait 和等待原因透传收口为提交 `a8015bd` 并推回 `workflow_code/main`。本轮完成 `check_workspace_line_budget`、`py_compile`、两条定向验收、`workflow gate`、`test` 部署和 `prod candidate=20260407-215842` 刷新；截至 `2026-04-07T22:00:03+08:00`，live `prod` 仍有 `node-sti-20260407-cb9fc7de=running`，主线/保底 next 保持 `2026-04-07T22:08:00+08:00 / 2026-04-07T22:38:00+08:00`。

### 2026-04-07T22:41:54+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 这轮 `22:38` 保底巡检要求我只按 live prod 真相决定是否升级或补链，而且需要把下一次主线时间写成绝对时间，方便你直接判断 7x24 链是不是还在滚动。
- delta_validation: 我已重读版本计划与持续唤醒需求，并核对 `/api/runtime-upgrade/status`、`/api/status`、`/api/schedules`、`sch-20260407-20001ab4`、`sch-20260407-5ef5e5c8`、当前 task/node/run/audit 文件、`.running/control/envs/prod.json`、`.running/control/instances/prod.json` 与 live `8090/8098` 监听真相。结论是：截至 `2026-04-07T22:41:54+08:00`，prod 仍是 `20260407-200414`、`candidate=20260407-215842`、`running_task_count=1`、`can_upgrade=false`，因此本轮未执行 apply；`[持续迭代] workflow` 仍保留 `2026-04-07T22:59:00+08:00` 的 future 入口，所以无需补链。我已把结论落到 `logs/runs/workflow-pm-wake-summary-20260407-224059.md`，并同步写进今日日记；同时也记录了 `instances/prod.json=8098` 与 live `8090` 的端口漂移告警。

### 2026-04-07T23:33:14+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 这轮 `23:29` 保底巡检继续要求我只按 live prod 真相决定是否升级或补链，而且要把主线/保底的绝对触发时间直接写进结论与记忆，方便你一眼判断 7x24 接力有没有继续滚动。
- delta_validation: 我已在 `2026-04-07T23:32+08:00` 重查 `/api/status`、`/api/runtime-upgrade/status`、`/api/schedules/sch-20260407-20001ab4`、当前 ticket/node/run/audit 真相；确认 `prod=20260407-200414`、`candidate=20260407-231904`、`running_task_count=1`、`can_upgrade=false`，当前无需 apply，也无需补链，因为 `[持续迭代] workflow` 的 future 入口仍保留到 `2026-04-07T23:50:00+08:00`。本轮结论已落到 `logs/runs/workflow-pm-wake-summary-20260407-233314.md`、`docs/workflow/governance/PM版本推进计划.md` 与今日日记。

### 2026-04-08T00:06:18+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你持续要求 7x24 主线不要只靠我单打独斗，所以小伙伴真实派发链一旦因为工作区上下文缺失而直接失败，就应该被视为当前版本的工程质量问题，而不是留到以后手工兜底。
- delta_validation: 我已在 `.repository/pm-main` 补上 assignment 派发前的 teammate memory bootstrap：目标工作区若声明 `.codex/memory/` 读链，就自动补齐 `全局记忆总览.md`、当月 `记忆总览.md` 和今日日记骨架；新增 `scripts/acceptance/verify_assignment_workspace_memory_bootstrap.py` 并接入 `workflow gate`。本轮完成 `check_workspace_line_budget`、`py_compile`、新验收、`workflow gate`，提交并推回 `workflow_code/main`（`8b51147`），随后刷新 `test/prod candidate` 到 `20260408-000353`。截至 `2026-04-08T00:06:18+08:00`，live `prod` 仍因当前主线节点运行中而 `can_upgrade=false`，保底唤醒入口保留在 `2026-04-08T00:20:00+08:00`。

### 2026-04-08T00:24:14+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 这轮保底巡检继续要求我只按 prod live 真相做判断，有运行中任务就不升级，而且要把下一次主线/保底的绝对触发时间写清楚，不能只口头说“主链未断”。
- delta_validation: 我已在 `2026-04-08T00:24:14+08:00` 复核 `/api/runtime-upgrade/status`、`/api/status`、`/api/schedules`、当前 ticket/node/run/audit 与 `schedules.jsonl`，确认 `node-sti-20260408-d5d29c5f` 正在运行、`running_task_count=1`、`can_upgrade=false`，因此本轮未执行 `apply`；同时 `[持续迭代] workflow` 仍保留 `2026-04-08T00:41:00+08:00` 的 future 入口，因此本轮也无需补链。结论已落到 `logs/runs/workflow-pm-wake-summary-20260408-002414.md`、`docs/workflow/governance/PM版本推进计划.md` 与 `.codex/memory/2026-04/2026-04-08.md`。

### 2026-04-08T00:54:05+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮继续要求我把“当前不能升级”与“还能继续推进哪条 V1 稳定性工作”分开说清楚，而且收尾必须同时保住绝对时间的下一次保底入口。
- delta_validation: 我已在 `2026-04-08T00:54:05+08:00` 复核 `/api/status`、`/api/runtime-upgrade/status` 与 `/api/schedules`，确认 live `prod` 仍由 `node-sti-20260408-e3941a63` 占用运行槽，`candidate=20260408-005244` 但 `running_task_count=1`、`can_upgrade=false`，因此本轮不直接 `apply`；同时我把 `workflow gate` 默认隔离 runtime 根改成唯一目录，消除了 `developer_workspace_bootstrap=workspace_not_git_repo` 的假性噪音，完成 `check_workspace_line_budget`、`py_compile`、整条 `workflow gate`，并将提交 `8611bf4` 推回 `workflow_code/main`，随后刷新 `test/prod candidate` 到 `20260408-005244`。下一次保底入口仍保留在 `2026-04-08T01:11:00+08:00`。

### 2026-04-08T01:15:56+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮保底巡检不仅要看“现在能不能升级”，还要求我在 `01:15` 主线 future 被消费后，继续按最新 live 真相判断主链有没有断，不能拿几分钟前的 future 结论硬收尾。
- delta_validation: 我已在 `2026-04-08T01:15:56+08:00` 复核 `/api/status`、`/api/runtime-upgrade/status`、`/api/schedules`、`schedules.jsonl`、`audit.jsonl`、当前 `run.json` 与新主线节点 `node-sti-20260408-378d2cc8.json`，确认 live `prod` 仍是 `20260407-200414`、`candidate=20260408-005244`、`running_task_count=1`、`can_upgrade=false`；同时 `01:15` 的 `[持续迭代] workflow` 已成功建出 `ready` 节点 `node-sti-20260408-378d2cc8`，当前全局主图收口成 `1 running + 1 ready`，因此这轮既不升级，也不补链，只把下一次保底观察点写到 `2026-04-08T01:20:00+08:00` 并落盘到 `logs/runs/workflow-pm-wake-summary-20260408-011647.md`。

### 2026-04-08T02:10:07+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮继续要求保底巡检只按 live prod 真相判断“能不能升级/要不要补链”，并把下一次主线/保底的绝对触发时间写进记忆和交付。
- delta_validation: 我已在 `2026-04-08T02:08:38+08:00 ~ 2026-04-08T02:10:07+08:00` 复核 `/api/status`、`/api/runtime-upgrade/status`、`/api/schedules`、`/api/schedules/sch-20260407-20001ab4`、`/api/schedules/sch-20260407-5ef5e5c8`、当前 ticket/node/run/audit 与 `schedules.jsonl`，确认 `prod=20260407-200414`、`candidate=20260408-015945`、`running_task_count=1`、`can_upgrade=false`，当前保底节点 `node-sti-20260408-fc2ef584` 正在运行，因此本轮未执行 `apply`；同时 `[持续迭代] workflow` 未来入口仍在 `2026-04-08T02:33:00+08:00`，所以无需补链。结论已落到 `logs/runs/workflow-pm-wake-summary-20260408-020838.md`、版本计划与今日日记。

### 2026-04-08T03:05:03+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮 `03:00` 保底巡检继续要求我只按 live prod 真相决定“能不能升级/要不要补链”，并且要把下一次主线时间写成绝对时间；最终交付仍然只收一个 JSON 对象。
- delta_validation: 我已在 `2026-04-08T03:02:12+08:00 ~ 2026-04-08T03:05:03+08:00` 复核 `/healthz`、`/api/status`、`/api/runtime-upgrade/status`、`/api/schedules`、`/api/schedules/sch-20260407-20001ab4`、`/api/schedules/sch-20260407-5ef5e5c8`、当前 ticket/node/run/audit 与 `schedules.jsonl`，确认 `prod=20260407-200414`、`candidate=20260408-024443`、`running_task_count=1`、`can_upgrade=false`，当前保底节点 `node-sti-20260408-c3cde83d` 正在运行，因此本轮未执行 `apply`；同时 `[持续迭代] workflow` 未来入口仍在 `2026-04-08T03:22:00+08:00`，所以无需补链。我也顺手把“核任务图要先过滤 `record_state=active`”沉淀进经验卡，并把结论落到 `logs/runs/workflow-pm-wake-summary-20260408-030503.md`、版本计划与今日日记。

### 2026-04-08T03:56:27+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮 `03:52` 保底巡检继续要求我只按 live prod 真相决定是否升级或补链，并把下一次主线/保底的绝对触发时间直接写进交付和记忆，最终仍只收一个 JSON 对象。
- delta_validation: 我已在 `2026-04-08T03:54:35+08:00 ~ 2026-04-08T03:56:27+08:00` 复核 `/healthz`、`/api/status`、`/api/runtime-upgrade/status`、`/api/schedules`、`/api/schedules/sch-20260407-20001ab4`、`/api/schedules/sch-20260407-5ef5e5c8`、prod 控制文件、当前 ticket/node/run/audit 与 `schedules.jsonl`，确认 `prod=20260407-200414`、`candidate=20260408-034009`、`running_task_count=1`、`can_upgrade=false`，当前唯一 running 节点就是本轮保底巡检 `node-sti-20260408-085a854e`；同时 `[持续迭代] workflow` 未来入口仍在 `2026-04-08T04:14:00+08:00`，无需补链。结论已落到 `logs/runs/workflow-pm-wake-summary-20260408-035627.md`、版本计划与今日日记。

### 2026-04-08T04:48:38+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮 `04:44` 保底巡检继续要求我只按当前绝对时间的 live prod 真相判断是否升级或补链，并把下一次主线/保底时间直接写进交付、版本计划和今日日记。
- delta_validation: 我已在 `2026-04-08T04:44:30+08:00 ~ 2026-04-08T04:48:38+08:00` 复核 `/api/status`、`/api/runtime-upgrade/status`、`/api/schedules`、`/api/schedules/sch-20260407-20001ab4`、`/api/schedules/sch-20260407-5ef5e5c8`、prod 控制文件、当前 ticket/node/run/audit 与 `schedules.jsonl`，确认 `prod=20260407-200414`、`candidate=20260408-043244`、`running_task_count=1`、`can_upgrade=false`，当前唯一 running 节点是本轮保底巡检 `node-sti-20260408-e1865eaa`；同时上一轮主线 `node-sti-20260408-a635881f` 虽在 `2026-04-08T04:35:38+08:00` 超时失败，但 `[持续迭代] workflow` 已自动续挂到 `2026-04-08T05:06:00+08:00`，因此这轮无需补链。我已把结论落到 `logs/runs/workflow-pm-wake-summary-20260408-044838.md`、`docs/workflow/governance/PM版本推进计划.md` 与 `.codex/memory/2026-04/2026-04-08.md`。

### 2026-04-08T05:19:39+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你持续要求任务中心/定时任务只按 live 真相展示，不接受已经终态且再也不会触发的 `once` 计划继续混在 active preview/count 里。
- delta_validation: 我已在 `.repository/pm-main` 的 `schedule_service.py` 补上 exhausted `once` plan repair，新增 `scripts/acceptance/verify_schedule_exhausted_once_plan_repair.py` 并接入 `workflow gate`；本轮完成 `check_workspace_line_budget`、`py_compile`、两条 schedule 定向验收、`workflow gate`、提交 `11f7da2` 并推回 `workflow_code/main`，随后安全停掉旧 `test` 进程并刷新 `test/prod candidate` 到 `20260408-051809`。截至 `2026-04-08T05:19:39+08:00`，live `prod` 仍因 `node-sti-20260408-59614e1a` 运行中而 `can_upgrade=false`，保底入口保留在 `2026-04-08T05:36:00+08:00`。

### 2026-04-08T05:40:51+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮 `05:36` 保底巡检继续要求我只按当前绝对时间的 live prod 真相决定是否升级或补链，并把下一次主线/保底时间直接写进交付、版本计划和今日日记。
- delta_validation: 我已在 `2026-04-08T05:38:48+08:00 ~ 2026-04-08T05:40:51+08:00` 复核 `/api/status`、`/api/runtime-upgrade/status`、`/api/schedules`、`/api/schedules/sch-20260407-20001ab4`、prod 控制文件、当前 ticket/node/run/audit 与 `schedules.jsonl`，确认 `prod=20260407-200414`、`candidate=20260408-051809`、`running_task_count=1`、`can_upgrade=false`，当前唯一 running 节点是本轮保底巡检 `node-sti-20260408-a5675f74`；同时 `[持续迭代] workflow` 未来入口仍在 `2026-04-08T05:58:00+08:00`，因此无需补链。我已把结论落到 `logs/runs/workflow-pm-wake-summary-20260408-054051.md`、`docs/workflow/governance/PM版本推进计划.md` 与 `.codex/memory/2026-04/2026-04-08.md`。

### 2026-04-08T06:32:13+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮 `06:28` 保底巡检继续要求我只按 live prod 真相决定是否升级或补链，而且要把下一次主线/保底绝对时间直接写进交付和记忆，避免“主链未断”只停留在口头判断。
- delta_validation: 我已在 `2026-04-08T06:30:46+08:00 ~ 2026-04-08T06:32:13+08:00` 复核 `/api/status`、`/api/runtime-upgrade/status`、`/api/schedules/sch-20260407-20001ab4`、当前 ticket/node/run/audit 与 `schedules.jsonl`，确认 `prod=20260407-200414`、`candidate=20260408-061833`、`running_task_count=1`、`can_upgrade=false`，当前唯一 running 节点是本轮保底巡检 `node-sti-20260408-6f7b2ae8`；同时 `[持续迭代] workflow` 已保留 `2026-04-08T06:50:00+08:00` 的 future 入口，因此这轮无需补链。我已把结论落到 `logs/runs/workflow-pm-wake-summary-20260408-063213.md`、`docs/workflow/governance/PM版本推进计划.md` 与 `.codex/memory/2026-04/2026-04-08.md`。

### 2026-04-08T06:57:58+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮 `06:50` 主线执行继续要求我只按 live prod 真相判断是否升级，并且在当前有 running 节点时 fail-closed，不把“candidate 已包含修复”误写成“prod 已经接管”；同时仍要把下一次保底时间写成绝对时间，保证 7x24 不断链。
- delta_validation: 我已在 `2026-04-08T06:57:58+08:00 ~ 2026-04-08T06:58:12+08:00` 复核 `/api/status`、`/api/runtime-upgrade/status`、`/api/schedules`、当前 `run.json`、`audit.jsonl`、`prod-candidate.json`、最新门禁报告与 `pm-main` 最近提交，确认 live `prod` 仍是 `20260407-200414`、`candidate=20260408-061833`、`running_task_count=1`、`can_upgrade=false`，当前 running 节点是 `node-sti-20260408-bb040ccc`；同时 `20260408-061833` 已包含 `0ea5233/26684e1` 两条关键修复并通过 `workflow-gate-acceptance-20260408-061716`。我据此更新了版本计划、连续迭代报告与今日日记，并明确当前不续挂小伙伴真实任务，避免在旧 prod 上重放已知失败；下一次保底入口仍为 `2026-04-08T07:20:00+08:00`。

### 2026-04-08T07:46:25+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮 `07:20` 保底巡检继续要求我只按 live prod 真相决定是否升级或补链，而且要把下一次主线/保底绝对时间、候选版本证据和 `memory_ref` 一起写清楚。
- delta_validation: 我已在 `2026-04-08T07:44:04+08:00 ~ 2026-04-08T07:46:25+08:00` 复核 `/api/status`、`/api/runtime-upgrade/status`、`/api/schedules/sch-20260407-20001ab4`、`/api/schedules/sch-20260407-5ef5e5c8`、prod 控制文件、当前/上一轮 node/run/audit 与 `schedules.jsonl`，确认 live `prod=20260407-200414`、`candidate=20260408-073535`、`running_task_count=1`、`can_upgrade=false`；当前唯一 active running 节点是本轮保底巡检 `node-sti-20260408-cad685a9`，而 `07:19` 主线失败后已把下一次主线/保底入口续挂为 `2026-04-08T08:12:00+08:00 / 2026-04-08T08:42:00+08:00`。我已把结论落到 `logs/runs/workflow-pm-wake-summary-20260408-074625.md`、版本计划与今日日记。

### 2026-04-08T08:24:57+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮继续要求我在“当前还不能升级”的情况下也要给出真实可执行的连续推进闭环，不能只说等空窗，而要把下一次保底入口和升级接力都挂成可追踪真相。
- delta_validation: 我已在 `.repository/pm-main` 新增 `scripts/apply_prod_candidate_when_idle.py` 与 `scripts/acceptance/verify_apply_prod_candidate_when_idle.py`，并把新验收接入 `workflow gate`；随后完成 `check_workspace_line_budget.py`、`py_compile`、新验收、`workflow gate`，提交并推回 `workflow_code/main`（`d6d468e fix(workflow): auto-apply prod candidate when idle`），再停掉旧 `test` 进程并刷新 `test/prod candidate` 到 `20260408-082257`。截至 `2026-04-08T08:24:57+08:00`，live `prod` 仍因当前主线节点 `node-sti-20260408-3e5c5ab6` 运行中而 `running_task_count=1 / can_upgrade=false`，所以我没有直接 apply；但我已真实启动 watcher 进程 `PID=21240`，日志在 `.repository/pm-main/logs/runs/prod-idle-upgrade-watcher-live-20260408-0823.md`，它会在首个 `running_task_count=0 && can_upgrade=true` 的空窗自动调用 `/api/runtime-upgrade/apply`。当前保底入口仍保留 `sch-20260407-5ef5e5c8 -> 2026-04-08T08:39:00+08:00`。

### 2026-04-08T10:06:33+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 这轮调度器 `probe` 明确要求我以 `workflow` 本人身份在目标工作区内完成任务、最终只交一个 JSON，并继续严格遵守本地 `AGENTS / SOUL / USER / MEMORY` 读链与今日日记更新。
- delta_validation: 我已完成完整读链核对，并用 `python .running/test/scripts/manage_codex_memory.py status --root .` 与 `python .running/test/scripts/manage_codex_memory.py verify-rollups --root .` 确认当前 `.codex` 记忆链和 `2026-04-07 -> .codex/memory/2026-04/记忆总览.md` 归档正常；同时根据 `git status --short --branch` 发现根目录 `continuous-improvement-report.md` 在当前工作树里处于缺失状态，所以我已按本轮 probe 现场重新生成该交付件，并把本轮总结追加到 `.codex/memory/2026-04/2026-04-08.md`。

### 2026-04-08T12:11:37+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮 `12:04` 保底巡检继续要求我只按 live prod 真相判断是否升级或补链，并把下一次主线或建议保底时间写成绝对时间，不接受“主链未断”的口头描述。
- delta_validation: 我已复核 `/healthz`、`/api/status`、`/api/runtime-upgrade/status`、`/api/schedules`、`/api/schedules/sch-20260407-20001ab4`、`/api/schedules/sch-20260407-5ef5e5c8`、prod 控制文件、当前 ticket/node/run/audit 与 `schedules.jsonl`。结论是：prod 已在 `20260408-115446` 且当前无可升级候选；`[持续迭代] workflow` 已续挂到 `2026-04-08T12:37:00+08:00`，因此本轮不升级也不补链。但 `node-sti-20260408-deec122c` 的 run `arun-20260408-120411-276809` 已因“运行句柄缺失”被取消，node 文件仍停在 `running` 且 audit 持续刷 `recover_stale_running`，说明 live 仍残留一条 schedule/node 终态回写分叉。我已把结论落到 `logs/runs/workflow-pm-wake-summary-20260408-121137.md`、版本计划与今日日记。

### 2026-04-08T14:16:16+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 这轮真实派发的 `pm持续唤醒 - workflow 主线巡检 / 2026-04-08 14:12:00` 继续要求我先做 exclusion 版升级复核，再用绝对时间确认主线 future 是否仍在，最终仍只收一个 JSON 交付。
- delta_validation: 我已复核 `/api/status`、`/api/runtime-upgrade/status`、`/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260407-103450-fb8ba8&exclude_assignment_node_id=node-sti-20260408-c9fc3c32`、`/api/schedules/sch-20260407-20001ab4`、当前 task/node/run/audit 真相，确认 `prod=20260408-131718` 且无更高 candidate，因此本轮不 `apply`；`[持续迭代] workflow` 仍保留 `2026-04-08T14:19:00+08:00` future 入口，也无需补链。结论已落到 `logs/runs/workflow-pm-wake-summary-20260408-141616.md`、`workflow-pm-wake-summary.md`、版本计划与今日日记。

### 2026-04-08T14:22:29+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 这轮真实派发的保底巡检在我收尾时又命中了新的 live 分叉：`14:19` 的主线已经失败并把 `[持续迭代] workflow` future 入口清空，所以我不能停在“14:19 还在”的中间态，而必须现场补链后再交付。
- delta_validation: 我已复核 `14:19` 后的 `/api/status`、`/api/runtime-upgrade/status`、`/api/schedules/sch-20260407-20001ab4`、`/api/schedules/sch-20260407-5ef5e5c8` 与最近 `run.json`，确认 `prod=20260408-131718`、`running_task_count=0`、`can_upgrade=false`、`candidate_is_newer=false`；随后直接 `POST /api/schedules/sch-20260407-20001ab4` 把主线 future 入口补回到 `2026-04-08T14:27:00+08:00`，并保留保底入口 `2026-04-08T14:49:00+08:00`。最新结论已落到 `logs/runs/workflow-pm-wake-summary-20260408-142229.md`、`workflow-pm-wake-summary.md`、版本计划与今日日记。

### 2026-04-08T15:18:00+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮继续要求我把 live 绝对时间真相、当前是否真的还有主线 future 入口，以及“为什么这轮不刷新 candidate”放在同一份交付里说清楚，不能把本地已验证修复误写成现网已接管。
- delta_validation: 我已在 `2026-04-08T15:18:00+08:00` 复核 `/api/status`、`/api/runtime-upgrade/status`、`/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260407-103450-fb8ba8&exclude_assignment_node_id=node-sti-20260408-fbd8c8bc`、`/api/schedules/sch-20260407-20001ab4`、`/api/schedules/sch-20260407-5ef5e5c8` 与当前 `run.json`，确认 live `prod=20260408-143350`，`14:59` 主线 `node-sti-20260408-fbd8c8bc` 仍在 `running`，`sch-20260407-20001ab4` 当前 `future_triggers=[]`，唯一已保住的未来入口是保底 `sch-20260407-5ef5e5c8 -> 2026-04-08T15:29:00+08:00`；同时我把 transient `stream disconnected before completion` 自动重试修复在 `pm-main` 本地完成 `line budget`、`py_compile`、定向验收与 `workflow gate` 验证，但因为 `.repository/pm-main` 还存在未接管的 `graph_model_and_payloads.py`、`running_state_reconciliation.py`、`verify_assignment_provider_liveness_guard.py` 与 `logs/` 并行脏改动，这轮不刷新 `test/prod candidate`，只先落版本计划、经验卡、连续迭代报告与今日日记。

### 2026-04-08T16:14:00+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮 `16:09` 保底巡检继续要求我先做 exclusion 版升级复核，再按当前绝对时间回答“主链有没有 future 入口、这轮到底要不要补链”，最终仍只收一个 JSON 交付。
- delta_validation: 我已复核 `/healthz`、`/api/status`、`/api/runtime-upgrade/status`、`/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260407-103450-fb8ba8&exclude_assignment_node_id=node-sti-20260408-263917f5`、`/api/schedules`、`/api/schedules/sch-20260407-20001ab4`、`/api/schedules/sch-20260407-5ef5e5c8`、prod 控制文件、当前 task/node/run/audit 与 `schedules.jsonl`，确认 live `prod=20260408-154825`、当前 running 节点为本轮保底巡检 `node-sti-20260408-263917f5 / arun-20260408-160921-24ecc3`，而 exclusion 复核后升级门禁收口为 `running_task_count=0 / candidate_is_newer=false / blocking_reason=no_candidate / can_upgrade=false`，所以这轮不 `apply`；同时 `[持续迭代] workflow` 仍保留 `2026-04-08T16:30:00+08:00` 的 future 入口，因此也无需补链。我已把结论落到 `logs/runs/workflow-pm-wake-summary-20260408-161400.md`、`workflow-pm-wake-summary.md`、版本计划与今日日记。

### 2026-04-08T17:06:36+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮 `17:00` 保底巡检继续要求我先做 exclusion 版升级复核，再用绝对时间确认 `17:19` 主线 future 是否仍在，并且最终只交一个 JSON 产物。
- delta_validation: 我已复核 `/healthz`、`/api/status`、`/api/runtime-upgrade/status`、`/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260407-103450-fb8ba8&exclude_assignment_node_id=node-sti-20260408-4d7d733f`、`/api/schedules`、`/api/schedules/sch-20260407-20001ab4`、`/api/schedules/sch-20260407-5ef5e5c8`、prod 控制文件、当前 task/node/run/events/audit 与 `schedules.jsonl`，确认 live `prod=20260408-164211`、当前唯一 active running 节点为本轮保底巡检 `node-sti-20260408-4d7d733f / arun-20260408-170020-2f88cd`；exclusion 复核后升级门禁收口为 `running_task_count=0 / candidate_is_newer=false / blocking_reason=no_candidate / can_upgrade=false`，因此本轮不 `apply`；同时 `[持续迭代] workflow` 仍保留 `2026-04-08T17:19:00+08:00` 的 future 入口，因此也无需补链。我已把结论落到 `logs/runs/workflow-pm-wake-summary-20260408-170636.md`、`workflow-pm-wake-summary.md`、版本计划与今日日记。

### 2026-04-08T17:40:48+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮继续要求我在当前主线已经真实 running 的情况下，也要按 live prod 真相推进 active 版本最高优先任务，并保证下一次可执行入口不断链，而不是只停在“等这轮跑完”。
- delta_validation: 我已复核 `/healthz`、`/api/status`、`/api/runtime-upgrade/status`、带 `exclude_assignment_ticket_id=asg-20260407-103450-fb8ba8&exclude_assignment_node_id=node-sti-20260408-8b322e0c` 的升级复核、`/api/schedules/sch-20260407-20001ab4`、`/api/schedules/sch-20260407-5ef5e5c8`、`/api/assignments/asg-20260407-103450-fb8ba8/graph` 与 `status-detail`。结论是：live `prod=20260408-171450`，当前主线 `node-sti-20260408-8b322e0c` 仍在运行；排除它后升级门禁仍收口为 `blocking_reason=no_candidate / can_upgrade=false`。同时我已在全局主图续挂 4 个 fresh ready 节点给 `workflow_bugmate / workflow_devmate / workflow_testmate / workflow_qualitymate`，当前图真相为 `1 running + 4 ready`，保底唤醒仍保留到 `2026-04-08T17:49:00+08:00`；但默认 `status-detail` 仍会选到旧失败节点 `node-sti-20260407-8d910bd6`，这条真相源分叉还需继续收口。

### 2026-04-08T18:00:09+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮 `17:49` 保底巡检继续要求我在 exclusion 复核之外，还要把“其他 running helper 是否仍占槽”和“主线/保底 future 是否已经回写”同时钉成 live 真相，最终仍只交一个 JSON 对象。
- delta_validation: 我已在 `2026-04-08T17:57:02+08:00 ~ 2026-04-08T18:00:09+08:00` 复核 `/healthz`、`/api/status`、`/api/runtime-upgrade/status`、`/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260407-103450-fb8ba8&exclude_assignment_node_id=node-sti-20260408-98a52773`、`/api/schedules`、`/api/schedules/sch-20260407-20001ab4`、`/api/schedules/sch-20260407-5ef5e5c8`、`/api/assignments/asg-20260407-103450-fb8ba8/graph` 以及 prod 控制文件、当前 task/node/run/audit 与 `schedules.jsonl`，确认 live `prod=20260408-171450`、`current=candidate=20260408-171450`、`running_task_count=3`；排除当前保底节点后仍有 `2` 个 running helper（`workflow_bugmate` 与 `workflow_testmate`），因此这轮既不能 `apply`，也无需补链。同时主线与保底 future 已分别续挂到 `2026-04-08T18:20:00+08:00 / 2026-04-08T18:50:00+08:00`。结论已落到 `logs/runs/workflow-pm-wake-summary-20260408-180009.md`、`workflow-pm-wake-summary.md`、版本计划与今日日记。

### 2026-04-08T18:59:29+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮 `18:50` 保底巡检不只要求我确认主线 future 还在，还要求我在 active 版本当前 baseline 上把闲置的小伙伴泳道重新挂回全局主图，避免 7x24 只剩 `workflow` 自己转。
- delta_validation: 我已复核 `/api/status`、`/api/runtime-upgrade/status`、`/api/runtime-upgrade/status?exclude_assignment_ticket_id=asg-20260407-103450-fb8ba8&exclude_assignment_node_id=node-sti-20260408-fb574035`、`/api/schedules/sch-20260407-20001ab4`、`/api/schedules/sch-20260407-5ef5e5c8` 与 `/api/assignments/asg-20260407-103450-fb8ba8/graph`，确认 live `prod=20260408-180347`、排除当前巡检节点后升级门禁为 `no_candidate`、主线 future 仍在 `2026-04-08T19:16:00+08:00`；随后又通过 `POST /api/assignments/asg-20260407-103450-fb8ba8/nodes` 补挂 `workflow_bugmate / workflow_devmate / workflow_testmate / workflow_qualitymate` 四条 `ready` 节点，使当前图真相收口为 `1 running + 4 ready`。

### 2026-04-08T19:23:06+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮持续迭代继续要求我把 active 版本的 baseline、candidate、当前 running 槽和下一次触发时间写成同一份 live 真相，不接受把 test candidate 误写成 prod 已接管。
- delta_validation: 我已复核 `prod=20260408-180347`、`candidate=20260408-191653`、`running_task_count=5`、默认 `status-detail` 仍落旧失败节点 `node-sti-20260407-8d910bd6`、以及 `8107c43 / test-gate-20260408-191653` 对应的变更证据，并把版本计划、连续迭代报告和今日日记统一更新到“工程质量探测 / 变更控制”的同一口径。

### 2026-04-08T20:15:03+08:00
- preference_ref: state/user-preferences.md
- delta_observation: 你这轮 `19:46` 保底巡检继续要求我只按当前分钟的 live prod 真相判断是否升级或补链，而且当主线 schedule 没有 `future_triggers` 时，也要明确区分“主链已断”与“当前版本 ready 入口已在图里”，不能只盯 future 一列下结论。
- delta_validation: 我已在 `2026-04-08T20:15:03+08:00` 复核 `/healthz`、`/api/status`、`/api/runtime-upgrade/status`、带 `exclude_assignment_ticket_id=asg-20260407-103450-fb8ba8&exclude_assignment_node_id=node-sti-20260408-90ac411d` 的升级复核、`/api/schedules/sch-20260407-20001ab4`、`/api/schedules/sch-20260407-5ef5e5c8`、`/api/assignments/asg-20260407-103450-fb8ba8/graph`、默认/显式 `status-detail` 与 prod 控制文件，确认 live `prod=20260408-191653`、当前图真相为 `1 running + 5 ready`；虽然两条 schedule 当前都 `future_triggers=[]`，但 `[持续迭代] workflow` 已保留 `node-sti-20260408-eaa62c26=ready` 作为当前版本主线入口，所以这轮不补链、不升级，只把结论落到巡检报告、版本计划和今日日记。
