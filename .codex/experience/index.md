# 经验索引

## 先读这里
- 本文件是每轮正式工作前的经验入口。
- 先读“必读经验”，再按需扩展阅读其他经验卡。
- 经验卡只记录可复用模式、踩坑复盘与规避动作，不记录单次流水账。

## 必读经验
- `runtime-upgrade-and-agent-monitoring.md`
- `schedule-trigger-closure.md`

## 经验文件
- `runtime-upgrade-and-agent-monitoring.md`
  - 适用范围： 正式升级、长任务 agent 调用、部署副本启动、浏览器 acceptance 稳定性
  - 原因： 最近多次触发升级卡住、长任务超时、部署副本配置漂移、stale pid 误拦截部署、watcher 等待窗口过短导致快照刷新漏跑，以及 provider 退出后 finalize 假 running；本轮又补进了“节点已终态或已删，但 stale `run.json` 仍把 ghost running 挂住”“assignment probe 若继续开 realtime stream/poller，或 probe 模式下还放着 workflow/runtime/policy 后台轮询，会把 `msedge --headless` 首张截图挂死”“api catalog live regression 在 API/list/detail 已通过时，Edge `--dump-dom` 或截图超时只能降级成 browser evidence warning，不能把接口合同误打红”“原型测试图里的占位代理节点不能无依赖待派发，否则会反复 dispatch_failed 缺工作区”“repair-ghost-running 的慢响应不能被 watcher 直接记成 request_failed 终态”“ghost-repair settle 的重复状态日志不能刷满值班日志”“assignment finalize 的 workspace memory writeback 不能被长 `result_summary/warning/failure` 打爆”“watchdog repair 不能被 finalize 锁卡到客户端超时，必要时要旁路恢复 terminal truth”“status-detail 要走 `/api/assignments/{ticket_id}/status-detail?node_id=...`，不要猜成 node 子路径”“当 live 里看起来 running 但 token 不增长时，要拆成 finalize 尾巴 / ready-dispatch 老化 / provider_start 空窗三段分别判因”，以及“failed/cancelled 节点若保留诊断 `result_ref`，node-level role quality 不能再直接投影 failed run 的 `pass` 评分”的稳定修复口径，属于高复用高风险经验
  - 更新时间： 2026-05-05
- `workspace-line-budget-mandatory-gate.md`
  - 适用范围： `workspace line budget`、`workflow gate`、`runtime release gate`、工程质量强制门禁治理
  - 原因： 这轮把行数探测从“只报不拦”正式升级成强制门禁，补进了“checker 改退出码不等于 gate 真会拦”“workflow gate / runtime release gate 必须显式改读 `mandatory_gate_pass`”“真实 workspace 上的预期失败本身就是门禁生效证据”“当 `Mandatory Gate` 已成为 active blocker 时，要把首批冻结对象稳定写回 `first_batch_targets`”以及“前端 runtime split 后，layout/workboard probe 要按 `bundle_manifest.json` 校验整包 JS，不要继续盯旧单文件”；这轮又补进了“workboard split 之后，detail/drawer surface 也要继续抽离成独立 bundle part，并用 dedicated split probe 锁住 manifest 装配顺序与函数迁移”“`index.html` 这类超长单页骨架可用 marker + manifest + HTML partial fail-closed 装配，在不引入新模板引擎的前提下退出首批冻结对象”“role-creation stage-flow JS split 之后，detail/stage/profile/hover-float CSS surface 也要继续拆成 dedicated manifest part”“training loop overview 的 create/workbench CSS 也要拆成 dedicated manifest part，而不是继续堆在主 overview CSS 里”“pm daily governance 的 learning-report discovery/projection runtime 要拆到独立 support module，并用 dedicated split probe + TC-PM-001/002 一起兜回归”“`role_creation_service_parts/session_commands.py` 命中门禁时，要把 cleanup/complete 生命周期抽成独立 manifest part，并用 split probe + live recovery probe 一起兜导入绑定”“`role_creation_service_parts/session_queries_and_internal_tasks.py` 命中门禁时，要把 list/detail query surface 与 delete-state projection 抽成独立 `session_query_surface.py`，并用 split probe + live recovery probe 一起锁导入绑定”“`schedule_trigger_runtime.py` 超线时，要把 trigger progress/supersede/processing-lock helper 抽到独立 runtime，并用 dedicated split probe + recovery/pending-replace/smoke-block probes 一起兜回归”“`graph_model_and_payloads.py` 继续超线时，要把 execution prompt/result/process helper 抽成独立 contract runtime，并用 dedicated split probe + prompt/runtime metrics probe 一起兜回归”，以及“role-quality 读面如果出现 `result.json` 为空、`status-detail` 非空，不要继续空转补第二条 live proof；先修 worker 结果归一化的 node 上下文，再用同一路径 probe 锁住”“`project_task_summary` 这类项目 contract 读面不能只靠 UI 手看或单次 live proof；要让 dedicated probe 正式接进 `workflow gate` 并同时断言关键字段和 registry 绑定”，还有“`measure_assignment_dashboard_latency.py` 这类手工点测脚本若要进入 gate，必须改成 runtime-root/runtime-config 自发现 + 多次采样 summary + verify probe 绑定，而不是继续靠人工参数和一次性 stdout”，以及“当 request-object 新切片会把贴线的 `*_parts` 文件重新顶过 Mandatory Gate 时，要先把 dataclass/coerce/helper 抽到独立 support runtime，再用 targeted contract probe + line-budget report 一起兜住旧债出队和主文件不过线”的口径，后续会反复复用
  - 更新时间： 2026-05-08
- `dual-repo-boundary-and-dev-workspace-bootstrap.md`
  - 适用范围： `workflow / workflow_code` 双仓边界、开发工作区 bootstrap、代码仓受保护根
  - 原因： 新一轮代码与 agent 分离改造已经形成稳定边界与 Git 使用约束；同时补充了 bugfix mirror scoped patch、prod 热修回放、PM 仓代码副本清理约束、release boundary 跨轮滞留时的根仓同步优先级、developer workspace registry 的 live Git 真相回写口径，以及本地非 bare `workflow_code` push 被 `updateInstead` 误拦时的 fetch+ff-only 收口口径
  - 更新时间： 2026-04-27
- `task-run-output-compaction.md`
  - 适用范围： 任务中心运行 trace、节点详情输出、`stdout/stderr/events` 体积控制
  - 原因： 任务运行详情默认回传全文会直接拖慢页面和消耗 token；最终 `artifact_markdown` 若不设长度保护，还会把 7x24 主线 bootstrap 直接打成失败；本轮又补进“需要继续保留在 role workspace 的源文件不要列入 `artifact_files`，否则 delivery 投影后可能清理源资产”的口径，这类收口策略后续会持续复用
  - 更新时间： 2026-04-27
- `schedule-trigger-closure.md`
  - 适用范围： `定时任务 -> 任务中心` 命中建单、pm/`workflow` 周期唤醒、自迭代失败恢复、stale recovery 与 follow-up dispatch 串行化
  - 原因： schedule 命中链路如果同步等慢建单/派发，极易留下 `trigger_hit` 半断裂现场；同时 stale recovery 若在 finalize 里递归 dispatch，会把同 ticket 派发锁直接卡死；另外看门狗如果只看 future 入口，也会漏掉 `0 running + ready 堆积` 的假健康。这轮又补进了“assignment finalize 不能把 workspace memory / pm daily / prod upgrade / follow-up dispatch 全压在全局 ticket 锁里，否则一条 helper finalize 就会把整张全局主图拖成假待派发”“worker 要把 `0 running + ready 已老化` 正式当成 ready-dispatch starvation 并主动补一次 dispatch recovery”，以及“当前治理口径下不再创建/续挂用户可见的 legacy `pm持续唤醒 - workflow 主线巡检`，失败恢复要直接 update 原 `[持续迭代] workflow` 主线一次性计划并用 probe 断言不再产出 patrol schedule”“禁用 legacy patrol 后还要同步清理已落成的 ready/queued 巡检节点，否则旧节点仍会抢跑”“旧 patrol 读面兼容壳也要删除，不能继续保留 false/null 字段误导后续实现”，以及“任意终态必须生成下一棒”不能继续散落在 schedule/finalize/recovery/dispatch/watchdog 多段副作用里，后续要收成 durable handoff outbox + 单一幂等 worker 的稳定口径；这轮又补进了“rolling once 主线错过命中分钟时不能被 exhausted-once repair 当普通计划退休，下一次 scan 要 catch-up hit”“ready-dispatch recovery 不能在 schedule worker 主循环里同步调用 dispatch-next，必须异步化并用 slow dispatch probe 断言 worker 快速返回”，以及“终态 trigger recovery 不能只修 trigger/plan，还必须回填 durable handoff 并 drain 到下一次 rolling once schedule；红灯用例要先证明缺少 handoff，再绿灯断言 handoff scheduled 与 plan next_trigger_at 同步更新”的口径。这类闭环、恢复和巡检口径后续会持续复用
  - 更新时间： 2026-04-28
- `module-parts-runtime-binding-and-role-memory-scaffold.md`
  - 适用范围： 拆片服务模块的离线验收、角色工作区记忆脚手架、私有 helper 直调验证
  - 原因： `role_creation_service` 这类 module-parts 服务直接导入时，运行时符号默认未绑定；如果验收绕过 runtime 绑定去裸调 helper，会得到误导性的 `NoneType` 故障；这轮又补进了“角色专业能力前置合同要直接从 assigned agent 运行态工作区的 `state/role-assets` 取方法入口，不要误去 developer workspace 壳里找 role-assets，离线 probe 也要自建临时 role workspace + role-assets”的稳定口径
  - 更新时间： 2026-04-21
- `pm-governance-separation-and-history-rules.md`
  - 适用范围： PM 自我治理、版本推进节奏、每日例行任务、版本日级留痕、7x24 提示词写回规则
  - 原因： 主计划一旦混入日级现场和临时待办，就会持续写脏并诱发版本无限膨胀；当前已经把稳定总计划、当前版本、每日执行结果和版本历史拆成稳定结构，同时补进了“failed/cancelled 但保留结构化学习结果的 helper report 也要被 PM daily 识别，并在 finalize 后 best-effort 投影回 today learning dir”，“active 版本退出门槛一旦在 live prod 上满足，就要同步刷新当前/下一版本 gate 与 switch blocker，必要时同轮直接切版”，以及“版本 AAR 必须服务排期优化和事故预防，并把调整写回版本计划”的稳定口径，需要长期复用
  - 更新时间： 2026-04-28
- `helper-dispatch-project-binding.md`
  - 适用范围： PM 在全局主图手工/受支持 API 派发 helper 节点、`workflow` 平台主线与多 project 并存现场
  - 原因： 这轮 live 证明了 `workflow_devmate` 这类兼任其他项目 controller 的角色，如果对平台主线 helper 节点继续使用 `project_binding_mode=auto`，会被自动绑到错误 project；同时 `dispatch-next` 客户端超时也不等于节点没起跑，后续需要优先读 node/run 文件真相。本轮又确认运营项目 PM 初始化时如果只给业务画像/记忆/方法卡、没有同步注入平台任务派发 runbook/API usage card，它只能写可交接载荷而不能真实给 writer/reviewer 建节点；无真实派发记录应归类为系统派发链缺口，不能误判成经营止损；本轮再补进“超时派发若已经有 provider_start 和活跃 pid，不要把活跃 helper 当 ghost 修，先对齐 node/run 状态事实面”，“手工 create_node 漏传 project_id 会生成空 project 绑定节点，后续必须显式传 `project_id=workflow`”，“手工指定项目不要传 `project_binding_mode=manual`，只传 `project_id=workflow`；status-detail 必须核对 selected_node.node_id，避免把默认选中节点误认为目标 helper”，以及“helper 接单/读链失败不是代码修复失败，优先恢复同一节点并用 status-detail/run 文件确认 live_execution 后再继续”的恢复口径
  - 更新时间： 2026-04-30
- `api-catalog-self-readback-refresh.md`
  - 适用范围： 接口目录 self-readback compare、`api_catalog_live_regression` 证据刷新、`platform.interfaces.list/detail` 的 live compare 读面
  - 原因： 这轮补进了“compare 读面不能只按 runtime_root 缓存；只要依赖 current_version + quality/live artifact，就必须把 freshness token 带进 snapshot key，否则新 artifact 落地也要等重启才显影”，并补齐了“`test/current` 刷到新 baseline 后还要对当前版本重跑 exact `api_catalog_live_regression`，否则 `platform.interfaces.detail` 会继续挂旧 summary”的稳定口径；当前已用 `verify_api_catalog_self_readback_closure.py` 锁住“不清缓存也能从 stale 自动转 ready”
  - 更新时间： 2026-04-22
- `workflow-latency-baseline-readback.md`
  - 适用范围： `workflow latency` live baseline、`metrics/cli-baseline-latency.json`、`metrics/workflow-latency-daily.json`、fixture gate + live sample 双轨口径
  - 原因： 这轮补进了“runtime_root/metrics 才是 live 真相、工作区 `metrics/` 只是镜像读面”“live mode 不能把 runtime 已 append 的样本再手动重复追加”“全失败 live sample 必须显式标 `failed/partial`，不能因文件非空就误写成 `ready`”以及“prod/test 同时返回 `real agent is not configured` 时，下一步优先判断补 `WORKFLOW_AGENT_*` 还是切 measurement path，而不是继续重复 point sample”的稳定口径
  - 更新时间： 2026-04-22
- `project-registry-continuity-and-quiet-probe.md`
  - 适用范围： 非内建项目 registry 连续性、quiet project live regression、prod 项目样本恢复、已退役项目 tombstone
  - 原因： 这轮把“`project-comics-smoke` 曾真实存在、但后续因手改 runtime state 被删掉”收成了 supported continuity recovery，并补进了“quiet project probe 不能把 test fixture 的 handoff/cooldown/window 参数误当成 prod 自然样本的硬合同”；本轮又补进“用户已明确退役的 smoke 项目不能再按历史 evidence 恢复，必须保留 archived tombstone + manual_pause，并从 workflow/release gate 中移除 continuity/readback 硬门”的口径
  - 更新时间： 2026-04-27
- `business-logic-boundary-consolidation.md`
  - 适用范围： 服务层业务逻辑被大量拆成 `*_parts`、support runtime 或 manifest bundle 后，调用链、入口和领域职责变得更难追踪
  - 原因： 当前代码树已经存在 `assignment_service_parts` 等大量拆片，近期又确认业务逻辑过散会拖慢修复和性能治理；后续不能把“文件变小”误当成“业务清楚”，应优先用 application facade、显式 contract、唯一写入口和读模型收口
  - 更新时间： 2026-04-25

## 更新规则
- 新经验优先补到已有经验卡；仅当主题明显不同再新建文件。
- 每次新增经验卡时，同步更新“必读经验”或“经验文件”引用。
- 如果只是一次性现象、还没验证稳定结论，不进入经验卡，只留在当日日记。

