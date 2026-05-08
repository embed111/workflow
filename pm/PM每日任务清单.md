# PM每日任务清单

## 1. 文档定位
- 本文件只写“每天只需要完整执行 `1` 次”的固定动作。
- 本文件不是 PM 主线每轮执行清单。
- 本文件不是版本推进计划，也不是版本现场更新记录。
- 当天是否已经执行过每日任务，只看 `pm/daily-execution-history/YYYY-MM-DD.md` 是否存在。

## 2. 与记忆库、PM主线的边界
1. 记忆库是每一轮都要更新：
   - `.codex/memory/YYYY-MM/YYYY-MM-DD.md`
2. 每日任务是每天只需要完整执行 `1` 次：
   - 通过 `pm/daily-execution-history/YYYY-MM-DD.md` 判断
3. PM 主线每轮都要检查的事情，不写在这里，统一看：
   - `pm/PM当前版本计划.md` 的“每轮 PM 主线必查项”
4. 典型的“每轮都要检查、但不属于每日任务”的事项包括：
   - 当前版本最高优先级需求点是否有变化
   - 是否需要派发、续挂、恢复或调整小伙伴
   - 是否识别到新的高杠杆功能或低维护价值重构项
   - 当前版本内容是否需要后移到后续版本

## 3. 每日执行结果目录规则
- path: `pm/daily-execution-history/YYYY-MM-DD.md`
- completion_rule: 当天文件存在 = 当天每日任务已完整执行 `1` 次
- pending_rule: 当天文件不存在 = 当天每日任务尚未完整执行
- retention_rule: 目录只保留最近 `7` 份历史文件
- cleanup_rule: 超过 `7` 份时，从最旧文件开始删除
- boundary_rule: 该目录只回答“今天的每日任务做没做”，不替代版本历史、运行留痕和记忆文件

## 4. 每日任务

### D1. 每日 `1` 次系统 7x24 运维质量检查
- 目的：保证每天至少有一轮系统级运维质量检查，确认 7x24 体系不是假健康。
- 默认执行时机：每日首轮正式工作前；若当天首轮未做，后续需要找合适窗口补做。
- 最低完成定义：
  - 已检查当前是“继续推进”还是“保持暂停”
  - 已核对 `/healthz`
  - 已核对 `/api/status`
  - 已核对 `/api/runtime-upgrade/status`
  - 已核对 `/api/schedules`
  - 已运行或回读代码质量流水线：`python .repository/pm-main/scripts/quality/run_code_quality_pipeline.py --root .repository/pm-main`
  - 已确认代码工作区 `post-commit` 质量扫描 hook 是否仍安装；若未安装，记录原因或重新安装
  - 若代码质量流水线 `status=fail/warn`，已写清首批质量债务是否进入当前版本排期或后续版本
  - 必要时已直读 `run.json / events.log / node.json`
  - 已形成当日运维质量结论，而不是只抄接口结果
- 主要证据落点：
  - `logs/runs/*.md`
  - `pm/daily-execution-history/YYYY-MM-DD.md`
  - `.codex/memory/YYYY-MM/YYYY-MM-DD.md`

### D2. 团队内每个小伙伴每日学习任务与学习报告
- 目的：保证 `pm` 和每个小伙伴每天都有一次真实的学习/修炼任务与真实输出，而不是只靠口头提示或假学习。
- 默认执行时机：每日 `1` 次；若当天还未执行，需要在 PM 主线某一轮里补齐。
- 覆盖对象：
  - `workflow(pm)`
  - `workflow_devmate`
  - `workflow_testmate`
  - `workflow_qualitymate`
  - `workflow_bugmate`
  - `workflow_ucdmate`（若已进入正式协作口径）
- 最低完成定义：
  - 已给每个对象分配明确的当天学习任务，而不是泛泛口头提示
  - 已为每个对象留下自己的学习报告
  - 每个学习任务都已绑定 `pm/expertise/专业能力总表.md` 里的能力项
  - 每个学习任务都已遵守 `pm/expertise/自我学习提升方法.md` 当前策略，而不是临时自由发挥
  - 每份学习报告都带有来源说明，例如：对应 helper run、对应工作区输出、或 `workflow(pm)` 本人的真实学习产物
  - 若本轮学习引用了外部资料，已经同步写入 `pm/expertise/material-reviews/YYYY-MM/*.md` 的评审结论，不能只在学习报告里口头引用
  - PM 不得代写 `workflow_devmate / workflow_testmate / workflow_qualitymate / workflow_bugmate / workflow_ucdmate` 的空壳学习报告
  - 已把学习任务、报告路径和例外说明落到当天执行结果中
- 主要证据落点：
  - `pm/daily-execution-history/YYYY-MM-DD.md`
  - `pm/daily-learning-reports/YYYY-MM-DD/<agent_id>.md`
  - `pm/expertise/专业能力总表.md`
  - `pm/expertise/自我学习提升方法.md`
  - `pm/expertise/material-reviews/YYYY-MM/*.md`
  - `pm/versions/<version>/history/YYYY-MM/YYYY-MM-DD.md`
  - `.codex/memory/YYYY-MM/YYYY-MM-DD.md`

### D3. 每日 `1` 次界面优化 / UCD 优先级复核
- 目的：保证界面优化不是偶发插单，而是每天至少有一轮明确的 UCD 复核、优先级判断和责任人接线。
- 默认执行时机：每日 `1` 次；优先放在系统运维质量检查之后、正式推进前。
- 最低完成定义：
  - 已明确今天最值得推进的界面 / UCD 问题，不接受只写“继续优化体验”
  - 已判断这轮是由 `workflow(pm)` 直接推进、交给 `workflow_ucdmate` 诊断，还是交给 `workflow_devmate` 实现
  - 已给出至少一条当前界面优化的验收口径，例如：滚动结构、固定工作面、信息层级、交互一致性、文案降噪中的哪一项
  - 若当天已经存在 `workflow_ucdmate / workflow_devmate` 的界面优化任务或交付，已把任务编号、交付件或阻塞原因写入当天执行结果
  - 不把纯视觉润色当成默认目标；优先处理影响使用效率和可扫读性的结构问题
- 主要证据落点：
  - `pm/daily-execution-history/YYYY-MM-DD.md`
  - `pm/versions/<version>/history/YYYY-MM/YYYY-MM-DD.md`
  - `logs/runs/*.md`
  - `.codex/memory/YYYY-MM/YYYY-MM-DD.md`

### D4. 每日执行结果落盘
- 目的：让“今天的每日任务是否已经执行过”可以直接通过目录判断。
- 默认执行时机：完成 `D1`、`D2` 和 `D3` 后立即执行。
- 最低完成定义：
  - 已写入 `pm/daily-execution-history/YYYY-MM-DD.md`
  - 写入后已检查历史数量，若超过 `7` 份则删除最旧文件
  - 文件内至少写清：当天系统运维质量检查结论、当天学习任务、界面优化/UCD 结论、覆盖对象、学习报告路径、例外说明
- 主要证据落点：
  - `pm/daily-execution-history/YYYY-MM-DD.md`
