# PM 治理分层与历史目录规则

## 适用范围
- PM 自我治理
- 版本推进节奏
- 每日例行任务
- 版本日级留痕
- 7x24 主线/保底提示词

## 稳定经验
- `PM版本推进计划.md` 必须保持稳定，只承接治理原则、版本路线图、职责边界和企业级节奏；不能继续混写日级现场和临时待办。
- `PM当前版本计划.md` 只保留当前活跃版本的最新有效判断；当天推进、调整、拆分和后移决策，统一写入 `pm/versions/<version>/history/YYYY-MM/YYYY-MM-DD.md`。
- 每日任务是否完成，不能靠口头判断；更稳的默认是直接看 `pm/daily-execution-history/YYYY-MM-DD.md` 是否存在。
- 每日任务和每轮 PM 主线必查项必须分开。更稳的默认是：每日任务只保留“每天只需要执行一次”的动作；每轮主线必查项的稳定定义、当前需求状态表和退出门槛放进 `pm/versions/<version>/版本计划.md`，`PM当前版本计划.md` 只保留 active 指针和单份当前快照；每轮执行结果统一写入 `history/`，不再按时间堆叠回正文。
- `pm/daily-execution-history/` 只做轻量执行结果目录，只保留最近 `7` 份；超过后从最旧文件开始删除。
- 更稳的默认不是把版本计划和版本历史拆在两处，而是直接把一个版本收成一个目录：`pm/versions/<version>/版本计划.md + history/YYYY-MM/YYYY-MM-DD.md`。这样同一版本的排期正文和推进历史始终在同一目录里维护。
- 既然版本目录下的 `history/` 已经承接版本日级现场更新，更稳的默认是不再额外维护一套 `PM版本推进现场更新` 或 `pm-version-live` 体系，避免同一层信息出现两个真相源。
- 当 active 版本已经出现核心需求 `已超时`，且 `prod candidate` 超过 `48h` 仍未刷新为更高版本时，更稳的默认是立刻进入 `治理恢复态`：优先形成新 candidate；若仍不能形成，就把当前版本明确写成 `blocked / closeout_pending / switch`，并停止沿用 `99% + 重设 ETA` 作为默认口径。
- 当 `.codex/memory/**/*.md + pm/versions/<version>/history/**/*.md + logs/runs/*.md` 已经能覆盖“对话连续性 + 版本现场 + 运行证据”时，根目录 `state/session-snapshot.md` 默认就是重复快照。更稳的默认是停止把它当成必维护项，只在用户明确要求或确有系统级兼容需求时才保留/更新。
- PM 当前状态快照一旦要被 runtime/status/prompt 解析，就不能把机器读链绑死在单一中文措辞上。像 `当前最高价值泳道已切到 / 继续保持 / 已更新为 / 临时切到`、`生命周期阶段已切到 / 继续保持`、`baseline 已更新为` 这类治理文案变体，也必须被解析层和 acceptance 一起覆盖，否则 live `/api/status` 和后续 schedule prompt 会重新出现字段空洞。
- PM 当前状态快照里的 lane 行也不能继续写成“已从 `A` 切到 `B`”这类双反引号结构。更稳的默认是只保留当前最终值，例如 `当前最高价值泳道已切到 `发布推进``；否则 `load_pm_version_status()`、`verify_pm_version_truth_source.py` 和 `TC-PM-003` 会把 lane 读空，即使版本真实状态已经写对。
- 切换 active 版本时，不能只改 `PM当前版本计划.md` 的引用。更稳的默认是同步给新的 `pm/versions/<active_version>/版本计划.md` 补上“当前状态快照”和需求级 `状态 / 进度 / ETA / 超时` 字段，否则 `pm_version_status` 会把 lane/lifecycle/baseline 读空，gate 也会继续按旧 `V1` 假设报错。
- 当 `V2-R1 / V2-R2` 这类 PM 治理需求正式进入 active 版本后，默认 gate 不能只盯 runtime/prod 真相；还要同步补上 `pm/daily-execution-history + pm/daily-learning-reports` 结构探针，以及 `PM当前版本计划.md <-> active 版本计划.md` 的当前快照一致性探针。否则版本看起来在推进，daily/history/view 这几条线仍会长期悬空。
- 当 `V2-R1` 进一步进入“自动补档/历史清理实现”阶段后，更稳的默认不是覆盖式重写已有 `pm/daily-execution-history/YYYY-MM-DD.md`。应只在今日日文件缺失时自动补出结构化骨架，并把 `daily-execution-history + daily-learning-reports` 的保留窗口统一收成最近 `7` 份；已有人工日级结论保持原样，自动化只负责补缺和清理。
- 当 `V2-R1` 已经把自动补档和保留清理落到文件/脚本层后，更稳的默认不是把它继续藏在 `pm/` 目录里。应同步把 `pm_daily_governance_status` 接到 `/api/status` / `/api/dashboard`，并在任务中心 workboard 里直接展示 daily history、学习报告缺口和清理候选；否则 PM 会误以为“R1 已经落地”，但真实工作面仍然看不到治理真相。
- 当 today `pm/daily-execution-history/YYYY-MM-DD.md` 已存在、但 helper 学习报告还没回流齐全时，latest daily 的合法状态就是 `in_progress`，不是结构性失败。更稳的默认是：`verify_pm_daily_execution_governance.py` 只在 latest status=`completed` 时强制五份核心学习报告齐全；而 `pm_daily_governance_service.py` 自动补档时也要同步补上 `ui_optimization_check`，避免验收把“执行中”误判成治理缺陷。
- 当 helper 因 workspace 边界不能直写 `pm/daily-learning-reports/YYYY-MM-DD/<agent_id>.md` 时，PM 治理读链不能继续只盯 today learning dir 的现存文件，也不能假设真实学习报告一定会投到 `delivery/workflow/*`。更稳的默认是：`pm_daily_governance_service.py` 先在当前 PM workspace 自己的 `state/runtime-config.json -> artifact_root/delivery/*/DELIVERY_INFO.json` 下识别 `workflow-target` 与 `self-target` 两类 helper 回流；若某条真实学习任务缺了 `DELIVERY_INFO`，再回退到 `tasks/*/nodes/*.json + result_ref` 读取同日成功节点里的 `artifact_markdown`；随后由 `refresh_pm_daily_governance.py` 把对应正文投影回 today learning dir。与此同时，artifact root 解析范围必须锁在当前 PM workspace 本身，不能沿父目录继续捡外层 workspace 的 runtime-config，否则 acceptance fixture 会误吃真实 `.output` 数据。
- 当 helper 学习节点被 watchdog / stale recovery 收成 `failed` 或 `cancelled`，但 `result_ref` 里已经保留了完整结构化学习报告时，PM daily governance 不能继续只认 `status=succeeded`。更稳的默认是：`_discover_result_ref_learning_reports()` 允许读取这类 terminal node 的 `result_ref`，而 assignment finalize 在命中 learning report 后还要 best-effort 触发 `maybe_sync_pm_daily_governance_after_assignment_result()`，把 today learning reports 尽快投影回 `pm/daily-learning-reports/YYYY-MM-DD/`；否则 UI 会看到学习结果有效，治理目录却长期只剩 `delivery_projection_pending`。
- helper 学习报告即使已经通过 `delivery` 或 `result_ref` 回流，PM 投影层也不能继续把原始自由 Markdown 原样落到 `pm/daily-learning-reports/YYYY-MM-DD/<agent_id>.md`。更稳的默认是：投影时补齐 `date / agent_id / learning_task / source_type / source_ref / learned_points / applied_to_project / next_action` 这组结构字段，再把原始正文挂到 `original_report`；否则 `verify_pm_daily_execution_governance.py` 会把“有真实报告但缺元数据”的现场误判成 learning report 不合格，`workflow gate` 也会稳定卡在 PM daily execution governance。
- 识别 delivery inbox 里的 helper 学习报告时，不能只把 `task_name` 里是否包含 `每日学习任务` 当唯一判据。更稳的默认是：允许真实 helper 主任务使用自由标题，但要同时要求“当日日期”命中 `task_name` 或 `delivered_at`，再把 `artifact_label / markdown 正文` 作为辅信号；否则一边会漏掉当天自由标题的真实报告，另一边又会把旧日期的学习报告误投影到今天。
- `pm/expertise/material-reviews/README.md` 与模板就位后，不能继续把 `material-reviews/YYYY-MM/README.md` 留成纯手工创建。更稳的默认是提供受支持的 `refresh_pm_expertise_material_reviews.py` 自动补齐当前月脚手架，并把这条月度目录 contract 接进 `V3-R3` 的 acceptance/gate；否则“外部资料先评审再入库”会长期停在口头规则。
- `pm_daily_governance_service.py` 里的 required learning agents 不能永久写死成固定五人。当 `workflow_ucdmate` 这类可选角色已经在当天通过真实交付进入正式协作口径时，更稳的默认是：先把它纳入 today daily 的 required set，再继续看它有没有对应学习报告；如果仍缺报告，today daily 必须保持 `in_progress`，不能因为核心五人齐了就误报 `completed`。
- `state/user-preferences.md` 作为单一事实源时，更稳的默认不是维护超长编号清单。优先保留高信号、当前仍生效的偏好，逐轮具体流水与详细来源放回 `.codex/memory/**/*.md`、版本历史和运行留痕，避免偏好文件本身再次膨胀成难读的半归档仓。
- 当前活跃版本必须有 scope freeze。新增内容只有在“直接属于当前目标 / 直接阻塞当前推进 / 高杠杆治理项”时才允许插入；否则默认转入下一版本或 backlog。
- 当 active 版本里的质量判断需求已经拿到“首条闭环样本 + 后果回写”时，更稳的默认不是继续在同一 active 版本里扩第二条同义 sample surface。应先把这条闭环写回当前版本真相，再把下一条专业判断 surface 明确移交给 next planned 版本；否则 active 版本会被样本治理持续扩胖，planned 版本又会继续停在抽象占位。
- 当前活跃版本和后续版本的排期，不能只停在抽象标题。更稳的默认是：至少写到“具体需求点 + 责任人 + 协作方”的层级。
- PM 的日常经营默认按 `质量 / 效率 / 工作区小伙伴维护 = 4 / 4 / 2` 平衡推进，避免长期只巡检、不推进，或只扩功能、不治基线。
- 如果只写“每轮要检查是否派发小伙伴”，默认还不够强。更稳的默认是把并行提效补成硬规则：写清并行触发条件、最小派发目标、连续不派发的失效判定，以及每轮必须回写的 `parallel_candidate_count / parallel_dispatched_count / active_helper_tasks / parallel_block_reason`；否则 PM 很容易继续单线程推进。
- 7x24 提示词也必须服从这套结构：先读稳定总计划、当前版本计划和每日任务清单；再检查当天 daily history 是否存在；当天版本推进先写 version history，只有主判断变化时才回写当前版本计划。
- PM 的 `7x24` 轮次不能只做“观察风险”。更稳的默认是：每轮至少落 `1` 项推进性修改；若识别到 live 风险，第一优先动作就是在受支持范围内尝试治理、修复、派发、调度调整或发布收口。单纯写 `history / logs / 今日日记 / 风险摘要` 不算有效推进。
- planned version 的 `activation readiness` 不能只看字段/schema 是否齐全。更稳的默认是：切版前专用 activation gate 还要同时校验 `draft:` probe、`blocking_items`、`activation_readiness` 本身，以及真实 probe 文件是否已经绑定到 `.repository/<developer_id>/scripts/acceptance/` 这类开发工作区代码面；否则 PM 看板会把“文档写得很完整”误报成“下一版已经 ready”。
- 当 planned version 已经从“schema 完整但仍 fail-closed”推进到“next activation ready”时，更稳的默认不是继续保留 `draft:` probe 名占位。应把每条 activation-gate 需求点都替换成真实 acceptance script，并同步把 `verify_pm_version_board_view.py` 这类看板验收断言切到 ready 侧；否则版本文件、版本看板和验收脚本会长期互相打架。
- 当 `prod` 已自动切到新的 runtime baseline，或当前轮刚把新 candidate 刷到 `test/prod candidate` 后，`PM当前版本计划.md` 与当前 active 版本文件里的“当前状态快照”必须同步追平最新 baseline。否则 `verify_pm_version_truth_source.py` 和 `verify_pm_current_version_snapshot_alignment.py` 会直接把 gate 卡住，哪怕真正出问题的不是代码实现而只是文档快照滞后。
- 当 active 版本的退出门槛已经在 live prod 上满足时，不能继续让旧 blocker 文案把版本留在上一版。更稳的默认是：先用受支持 probe 或直接 prod readback 复核关键退出信号，再同步更新 `PM当前版本计划.md`、当前版本计划/矩阵和下一版本 activation gate；若下一版本的 smoke / probe binding 也已到位，就在同轮直接切版，而不是继续沿用“等旧 candidate apply / 等旧 readback”这类已经过时的 switch blocker。
- 当 helper 的 blocker 结论只引用 `logs/current-root.html`、`logs/current-workflow-web-client.js` 这类带日期的本地快照时，更稳的默认不是直接把它写回 active blocker。应先用 current prod 的 `/api/dashboard`、`/api/status`、`/static/workflow-web-client.js` 和一条 live regression probe 交叉核实；若 served bundle 与 live API 已经转绿，旧 helper 结论只能当 `stale evidence`，不能继续阻塞 active requirement。
- 当 next planned 版本的 activation gate 失败原因里已经明确出现 `unbound_probe_refs` 时，更稳的默认不是继续扩写 blocker 说明，也不是马上再派 helper 去猜下一步。应先把 planned version 里那批 placeholder probe/evidence 名称替换成真实可回读路径（脚本、版本资产或证据文件），再回读 `/api/status.pm_version_board.activation_summary` 看 gate 是不是已经从“路径没绑上”收缩成真正剩余的 implementation/live evidence 缺口；否则 PM 很容易把“还缺真实路径”误当成“还缺更多主题”，版本会在同一层假 blocker 里空转。
- 当 next-version blocker 已经收窄成“quiet non-builtin sample 缺 exact live evidence”这类样本缺口时，更稳的默认不是继续把 recheck_trigger 写成口头说明。应让现有 live regression probe 提供 `require_quiet_project` 这类 fail-closed 模式：在 prod 只读 host 上样本缺失就结构化返回 blocked，在 test host 上允许 bootstrap fixture 跑成 green，并把同一条 probe 直接写回版本文件作为后续重检路径。
- `pm_version_board_service.load_pm_version_board()` 不能只算 future activation readiness。只要 `PM当前版本计划.md` 已经写出 `当前版本判断已更新为：version_transition_decision=... / switch_blockers=... / recheck_trigger=...`，`/api/status.pm_version_board.activation_summary` 也要把这些字段同步对外；否则主线/巡检 prompt 合同已经要求每轮显式 stay|switch，任务中心版本看板和 API 却继续给空值。
- `PM当前版本计划.md` 或 active 版本文件里的 `version_transition_decision=... / switch_blockers=... / recheck_trigger=...` 代码 span 不能再夹带额外反引号片段，也不要在 value 里继续写新的 `foo=` 结构。更稳的默认是让整段 decision hint 只保留一对外层反引号，内部若要提需求点、版本号或 candidate 标识就写成纯文本；否则 `_CURRENT_VERSION_DECISION_RE` 会在第一段内嵌反引号处截断，而 key-value 解析也会把 value 里的 `candidate=` 之类误吸成新字段，最终让 `pm_version_board.activation_summary.switch_blockers / recheck_trigger` 变空或被截断，连 `verify_pm_version_board_view.py` 都会误报版本治理缺口。
- 当 `TC-AWAKE-*` 这类 PM 侧专项 wrapper 需要复用既有 acceptance 时，不要假设每个子脚本都会回结构化 JSON。更稳的默认是沿用 `workflow_gate_probe_registry.py` 的判定口径：`returncode=0` 先算通过，只有在子脚本真的输出 JSON 时再校验 `ok`；同时像 `run_acceptance_assignment_self_iteration_schedule.py` 这类自迭代验收的断言，也要跟随当前主线 `done_definition` 的真实合同词，例如“当前泳道、生命周期阶段”“至少 1 项推进性修改”，不要继续写死旧的“版本计划”措辞。
- 当用户对 `workflow(pm)` 的交互口径已经给出稳定负反馈，例如“太像值班播报器”，更稳的默认不是只把它记进 `state/user-preferences.md`、版本 history 或日记。应同步把这条体验要求固化到 `self_iteration_prompt_templates.py` 的 mainline / patrol 提示词、`schedule_text_repair.py` 的 required tokens，以及一条专门的 acceptance probe；否则旧 schedule snapshot 仍会沿着旧播报腔继续运行，版本也会在“口头知道要改”与“实际调度仍没改”之间分叉。
- 当 active 版本已经建立，而下一个版本目录仍不存在时，更稳的默认不是继续等用户手工提醒或临时手建目录。应提供受支持的 next-version bootstrap：至少自动补齐 `pm/versions/V{N+1}/版本计划.md`、`需求映射与覆盖矩阵.md`、当日 `history/YYYY-MM/YYYY-MM-DD.md`，并同步更新 `PM当前版本计划.md` 的 active 指针相关字段与 `PM版本目录导航.md`；同时这条脚本默认要幂等，避免二次执行把已有版本骨架覆盖掉。
- 仅仅在 `PM版本推进计划.md` 里写“每个版本都必须安排最低配置泳道”还不够。更稳的默认是：当前 active 版本文件和 next planned 版本文件里都要直接出现 `最低配置泳道` 映射表，`PM当前版本计划.md` 还要显式写出 `mandatory_lane_guard / missing_mandatory_lanes`；后续再把这条校验接成 7x24 fail-closed gate。否则 PM 很容易在 active 版本推进时又把 `UCD/界面优化`、`下一迭代需求排期` 或 `小伙伴提升计划` 漏掉，直到用户追问才暴露。
- `mandatory_lane_guard` 一旦正式实现，不能只停在 planned-version 文档或单条 acceptance 脚本里。更稳的默认是：`pm_version_board_service.load_pm_version_board()`、`verify_planned_version_activation_readiness.py`、`verify_planned_version_activation_gate_binding.py` 和 `verify_pm_version_board_view.py` 至少要同时消费 `active + next planned` 两侧的最低配置泳道与 next-version planning；否则 `/api/status` 会继续只给 `next_activation_ready`，却读不出 guard 到底是不是已经真正生效。
- 当用户已经明确“`workflow(pm)` 的职责是给其他运维项目提供功能基座，而不是替其他项目做 PM/运维决策”时，更稳的默认不是继续在 next version 里替具体项目规划 PM/运维合同。应把后续版本收口到平台能力：项目生命周期 API、通用 PM/controller/member contract、扁平化工作面、mandatory-lane gate、性能基线；具体项目如何运维，则交给对应项目 PM 去定义。
- 当某条版本需求只完成了“首批 canonical 闭环”而界面上大多数对象仍显示 `待补充 / metadata incomplete / metrics unavailable` 时，更稳的默认不是把它写成“整体完成”。应显式把口径拆成：`首批基础闭环 completed` 与 `全量覆盖 pending`；否则用户一眼就会看出界面大面积待补，却在版本计划里看到 completed，这种口径分裂会反复伤信任。
- 版本 AAR 不能只由“需求超时”触发。只要版本关闭后被用户指出承诺项/体验项漏收、completed 需求仍有实质工作面后移、范围漂移挤进下一版激活修复，或出现 `7x24` 断链、ghost running、升级真相分叉等生产事故，就要补 AAR 或写清 no-AAR 判定；AAR 必须产出后续排期调整和防复发动作，并同步写回当前/后续版本计划，不能只停留在事后说明。

## 已踩过的坑
- 坑 1：把稳定总计划、当前版本、live 快照和当日待办混写在同一份文档里，结果主计划持续无限增长，版本边界越来越模糊。
  - 避免方式：固定拆成“稳定总计划 / 当前版本计划 / 每日任务清单 / 每日执行结果 / 版本历史 / 现场总览”。
- 坑 2：每天是否完成例行任务只能靠记忆或对话判断，后续很难自动化衔接。
  - 避免方式：通过 `daily-execution-history` 的当天文件存在性做单一判断，并写清 `7` 份保留规则。
- 坑 3：把“小伙伴派发、后移判断、版本排期”等每轮都要看的事情误写进每日任务，结果每日任务越来越重，也越来越不真实。
  - 避免方式：每日任务只保留每日一次动作；每轮判断统一进入 `PM当前版本计划.md`。
- 坑 4：版本新增需求没有冻结边界，导致当前版本不断补塞、无限延期。
  - 避免方式：对当前版本执行 scope freeze，新想法先记入版本日级文件，再判断转入下一版本或 backlog。
- 坑 5：后续版本只有抽象标题，没有具体功能点和责任人，导致排期无法讨论、无法提前准备。
  - 避免方式：把后续版本至少写到“需求点 + 责任人 + 协作方”的粒度。
- 坑 6：当 `PM当前版本计划 + version-history` 已经能覆盖版本现场时，继续额外维护“现场更新总览/月度现场总览”，只会制造重复维护和真相分叉。
  - 避免方式：删除这套额外入口，让 `PM当前版本计划` 只保留单份状态快照，日级现场统一归 `version-history`。
- 坑 7：版本计划在 `versions/`、版本推进历史在顶层 `version-history/`，虽然逻辑上能跑，但维护时还是容易分神和漏改。
  - 避免方式：直接把版本历史并回对应版本目录，让一个版本对应一个目录。
- 坑 8：PM 治理文案已经改成了“生命周期阶段已切到 / 继续保持 / baseline 已更新为”，但 runtime 解析和 acceptance 还停在旧正则，结果 `/api/status.pm_version_status` 把 `lifecycle_stage / baseline` 读成空值，连带后续 prompt 也可能丢字段。
  - 避免方式：PM 当前状态快照的正则和 acceptance 默认要兼容当前已落地的中文变体，不要把读链写成只认一种句式。
- 坑 9：当前版本快照里的 lane 文案一旦从“当前最高价值泳道为”改成“已切到 / 继续保持 / 临时切到”，旧 prod 代码会把 `/api/status.pm_version_status.lane` 直接读空；如果只改候选代码而不先做 live 兼容句式回拉，现网看板会在升级前一直缺字段。
  - 避免方式：lane 正则和 acceptance 默认也要覆盖 `为 / 继续保持 / 已切到 / 已更新为 / 临时切到` 五种句式；命中 live 字段空洞时，先用当前版本文件的兼容句式把现场拉回，再把永久修复推成 candidate。
- 坑 10：把 active 版本从 `V1` 切到 `V2` 时，如果新版本文件还停在“planned 模板态”，没有同步补上当前状态快照和需求级 ETA，`verify_pm_version_truth_source.py` 这类探针会先读到 `active_version=V2`，再因为 lane/lifecycle/baseline 为空直接 fail；同时 runtime `/api/status.pm_version_status` 也会只剩 runtime baseline，没有文档真相。
  - 避免方式：切版动作要成对执行：`PM当前版本计划.md` 更新引用的同时，立即把新 active 版本计划升级成“可被 parser 和 prompt 直接消费”的激活态，并把 acceptance 对 `source_path` 的断言改成跟随 `active_version_file`，不要再写死 `V1`。
- 坑 11：当前版本快照如果把 lane 写成“已从 `bug 修复推进` 切到 `发布推进`”这类双反引号变体，`workflow gate` 会把 `lane` 读空，进而卡在 `pm_version_truth_source / TC-PM-003 / snapshot_alignment`，即使真正缺的只是文案结构。
  - 避免方式：当前版本快照的 lane 行只保留当前最终状态一个反引号值，例如 `当前最高价值泳道已切到 `发布推进``；若需要保留前一泳道，写进 history，不要写回 snapshot 行本身。
- 坑 12：active 版本已经超期、`prod candidate` 长时间没更新，却继续在版本正文里维持 `99% + 重设 ETA`，还把每轮质量债消费写成“即将 closeout”，会同时污染排期真相和发布判断。
  - 避免方式：一旦同时命中“核心需求超期 + 无更高 candidate 超过 48h + 仍有持续代码改动”，立刻进入治理恢复态；先收口当前可发批次，若仍不能形成新 candidate，就把版本写成 `blocked / closeout_pending`，并补版本 AAR。

## 最小检查清单
1. 当前轮是否只在该写的文件里写对应层级的内容。
2. 今天的 `daily-execution-history/YYYY-MM-DD.md` 是否已经存在。
3. 今天若发生版本推进或调整，是否已经写入 `versions/<version>/history/YYYY-MM/YYYY-MM-DD.md`。
4. 当前活跃版本是否仍保持合理体量，没有继续无控制扩面。
