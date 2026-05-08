# PM治理目录

## 定位
- 本目录是 `workflow` 项目里 `pm` 自我治理、版本推进和日常节奏的顶层真相源。
- 当前固定拆成四层：
  - 稳定总计划
  - 当前活跃版本自动引用
  - 每个版本的独立目录
  - 每日任务与每日执行结果

## 治理结构
- `PM版本推进计划.md`
  - 稳定总计划。
  - 维护治理原则、版本路线图、PM 职责边界与企业级推进节奏。
- `PM版本推进注意事项.md`
  - 版本推进中的高信号遗漏点、补洞口径和后续版本细化要求。
  - 只记录稳定注意事项，不写单轮流水。
- `PM版本目录导航.md`
  - 单独维护版本目录导航、状态与路径索引。
- `PM当前版本计划.md`
  - 当前活跃版本自动引用文件。
  - 维护 `active_version`、`active_version_file` 和单份当前状态快照。
- `versions/<version>/版本计划.md`
  - 该版本的完整计划正文。
- `versions/<version>/需求台账.md`
  - 当前版本的细粒度需求台账。
  - 维护 `current_stage / next_gate / plan_start / plan_end / stage_risk / evidence_ref`。
- `versions/<version>/阶段看板.md`
  - 当前版本的阶段看板真相源。
  - 用来回答“每条需求现在处于哪个阶段、卡在哪一门、下一步谁接”。
- `versions/<version>/迭代甘特图.md`
  - 当前版本的计划视图。
  - 由需求台账和阶段看板派生，不单独发明事实。
- `versions/<version>/history/YYYY-MM/YYYY-MM-DD.md`
  - 该版本的日级推进、调整、后移和排期记录。
- `versions/<version>/aar/YYYY-MM/YYYY-MM-DD-<requirement_id>.md`
  - 该版本因需求延期、预计完成时间失准或明显偏差触发的版本 AAR。
- `versions/<version>/clarifications/*.md`
  - 需求澄清记录。
- `versions/<version>/design-reviews/*.md`
  - 方案设计评审记录。
- `versions/<version>/test-reviews/*.md`
  - 测试设计评审记录。
- `versions/<version>/demos/*.md`
  - 功能演示与准入验收记录。
- `PM每日任务清单.md`
  - 每天只需要完整执行 `1` 次的固定动作。
- `daily-execution-history/YYYY-MM-DD.md`
  - 每日任务执行结果。
  - 通过“当天文件是否存在”判断当天是否已完成一轮每日任务。
  - 只保留最近 `7` 份。
- `daily-learning-reports/YYYY-MM-DD/<agent_id>.md`
  - 每个小伙伴当天真实输出的学习报告。
  - 不接受 PM 代写空壳摘要；默认需要来自对应 helper 的真实派单、真实工作区产物或明确的本人学习输出。
- `expertise/`
  - 专家成长治理目录。
  - 维护 `自我学习提升方法.md`、`专业能力总表.md`、`问题-方法映射总表.md`、角色理论库建设清单和外部资料评审入口。
- `templates/version-governance/*.md`
  - 版本治理模板目录。
  - 用于创建 `需求台账 / 需求澄清 / 方案评审 / 测试设计 / 功能演示 / 阶段看板 / 甘特图` 的标准骨架。

## 目录治理原则
1. `PM版本推进计划.md` 是最高治理准则，默认稳定，不能被日级现场反复改写。
2. `PM当前版本计划.md` 只保留当前活跃版本引用和单份状态快照，不承接当前版本完整排期正文。
3. 一个版本对应一个目录，版本计划正文、需求台账、阶段看板、甘特图和版本推进历史都放在同一目录下维护。
4. 每日任务只保留“每日 `1` 次”的动作；每轮 PM 主线必查项的定义、当前需求状态表和退出门槛统一放在当前活跃版本对应目录下的 `版本计划.md` 中，但执行结果不得按时间堆叠回写正文。
5. 版本推进、后移、ETA 重估、切版判断和发布边界真相，统一写入 `versions/<version>/history/YYYY-MM/YYYY-MM-DD.md`。
6. 标准需求默认不得直接从版本条目跳进开发。
   - 至少要经过：`需求台账 -> 需求澄清 -> 方案设计评审 -> 测试设计评审 -> 开发 -> 功能演示 -> 测试 -> 发布收口`
   - 只有热修、gate 补洞、兼容性修补这类快车道任务，才允许压缩中间环节
7. 每轮正式执行后，PM 都要对当前活跃版本的每个需求点做一次：
   - 进度评估
   - 最近更新时间
   - 预计完成时间评估
   - 是否超时判断
   - 必要时的版本 AAR 决策
   - 上述评估的当前有效结果，只更新到 `版本计划.md` 的单份需求状态表和单份当前状态快照；本轮过程、证据、争议和时间序列统一写入 `history/`。
8. 若某个需求点已经超过上一轮承诺的预计完成时间，且没有被明确重设 ETA，本轮必须补一份版本 AAR，路径默认写入：
   - `pm/versions/<active_version>/aar/YYYY-MM/YYYY-MM-DD-<requirement_id>.md`
   - 若当前 active 版本已存在核心需求 `已超时`，且 `prod candidate` 超过 `48h` 仍未刷新为更高版本，本轮必须进入 `治理恢复态`：
   - 优先形成新 candidate，或明确写成 `blocked / closeout_pending / switch`
   - 不得继续沿用 `99% + 重设 ETA` 作为默认口径
   - `PM当前版本计划.md` 与当日 `history` 必须显式写出恢复动作和阻塞真相
9. 每日学习任务不再停留在“提示一下”：
   - PM 每天要给每个小伙伴指派明确学习任务
   - 每个小伙伴都要留下自己的学习报告
   - 学习报告默认写入 `pm/daily-learning-reports/YYYY-MM-DD/<agent_id>.md`
   - PM 不得代写空壳学习报告
10. 当前版本不允许持续膨胀；新内容只有在“直接属于当前目标 / 直接阻塞当前推进 / 高杠杆治理项”时，才允许纳入当前版本。
11. 记忆库和每日任务不能混淆：
   - 记忆库每一轮都要更新
   - 每日任务每天只需要执行 `1` 次
12. `7x24` 持续迭代轮次不允许纯观察：
   - 每轮至少要完成 `1` 项推进性修改
   - 单纯写 `history / logs / 今日日记 / 观察摘要` 不算推进性修改
   - 命中风险后，默认先执行 `1` 项受支持的缓解 / 治理 / 修复 / 派发 / 调度调整动作；只有确实没有安全动作可做时，才允许把本轮记为 `blocked`
13. 当前活跃版本的进展展示默认遵循“双视图”：
   - `阶段看板.md` 回答阶段、门禁、阻塞和责任人
   - `迭代甘特图.md` 回答时间窗口、依赖和里程碑

## 推荐更新顺序
1. 先把运行证据、接口结果和过程判断落到：
   - `logs/runs/*.md`
   - `.codex/memory/YYYY-MM/YYYY-MM-DD.md`
2. 若当天还没执行过每日任务，先在合适窗口完成一轮，再写入：
   - `pm/daily-execution-history/YYYY-MM-DD.md`
3. 若当天发生了版本推进、调整、后移、ETA 重估或超时判断，写入：
   - `pm/versions/<active_version>/history/YYYY-MM/YYYY-MM-DD.md`
4. 若某个需求点已超时并触发反思，补写：
   - `pm/versions/<active_version>/aar/YYYY-MM/YYYY-MM-DD-<requirement_id>.md`
5. 若当天完成了小伙伴学习任务，补写：
   - `pm/daily-learning-reports/YYYY-MM-DD/<agent_id>.md`
6. 若当天发生了能力方向调整、方法替换、案例淘汰或外部资料纳入判断，更新：
   - `pm/expertise/自我学习提升方法.md`
   - `pm/expertise/专业能力总表.md`
   - `pm/expertise/问题-方法映射总表.md`
   - `pm/expertise/material-reviews/YYYY-MM/*.md`
7. 若当前活跃版本的主判断发生变化，再更新：
   - `pm/PM当前版本计划.md`
8. 若版本的具体需求点、责任人、进度、预计完成时间、进入前提、退出门槛或阶段门禁变化，再更新：
   - `pm/versions/<version>/版本计划.md`
9. 若阶段看板、需求台账或甘特图变化，再更新：
   - `pm/versions/<version>/需求台账.md`
   - `pm/versions/<version>/阶段看板.md`
   - `pm/versions/<version>/迭代甘特图.md`
10. 只有治理原则、路线图、版本目录结构变化时，才更新：
   - `pm/PM版本推进计划.md`
11. 若版本目录导航、状态或说明变化，再更新：
   - `pm/PM版本目录导航.md`
12. 若识别出稳定的版本规划遗漏点、版本映射缺口或后续版本细化门槛，再更新：
   - `pm/PM版本推进注意事项.md`
