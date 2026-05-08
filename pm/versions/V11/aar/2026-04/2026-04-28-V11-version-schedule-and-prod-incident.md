# V11 版本 AAR：排期漂移与生产事故复盘

- version: `V11`
- created_at: `2026-04-28T22:40:00+08:00`
- aar_type: `version_closeout / schedule_planning / production_incident_prevention`
- trigger: 用户指出旧版本也需要 AAR，且 AAR 目标应是优化版本排期、让版本排期更合理，并减少生产事故。
- related_history:
  - `pm/versions/V11/history/2026-04/2026-04-27.md`
  - `pm/versions/V11/版本计划.md`

## 1. 复盘结论
V11 需要 AAR。V11 虽然最终在 `2026-04-27T04:27:00+08:00` 切到 completed，但它的后半段已经明显从“多项目工作面二期 / compare/readback”漂移成了“V12 activation gate、ghost running、prod apply、artifact 截断、7x24 恢复”的生产稳定性收口。

当时的记录把多个需求写成“已完成 / 无 AAR”，这个判断太窄，只覆盖了单条需求是否超时，没有覆盖：
- 版本目标是否被后续生产事故吞掉。
- 当前版本是否承担了下一版本的激活修复成本。
- 是否需要调整后续版本排期来避免同类事故复发。

## 2. 发生了什么
- V11 原本目标是多项目工作面二期、跨项目 compare/readback 和专业判断闭环。
- 实际推进中，V11 后半段大量时间被用于 V12 activation gate、DTS-00011、ghost running、artifact 过长、prod candidate apply 和 7x24 恢复。
- `project-comics-smoke` continuity/readback 曾成为 V11/V12 gate 的 blocker，后续又被用户明确退役，说明当时把样本项目当硬连续性门禁的排期判断存在成本误判。
- 生产恢复期间多次出现 `starting/provider_pid=0`、`running_node_projected_terminal`、`ghost_running_detected`、`can_upgrade=false` 等信号，说明 V11 的发布和切版窗口没有预留足够的运行真相治理缓冲。

## 3. 错误判断
1. 把“需求未超时”误当成“不需要 AAR”。
   - 版本级 AAR 不应只由 ETA 超时触发，也应由生产事故、scope 漂移、切版反复和用户追问触发。
2. 把 V12 activation 修复挤进 V11 末段，却没有在 V11 closeout 时生成排期修正。
   - 这让 V12 刚启动就背上前置稳定性债务。
3. 把样本项目连续性当成硬门禁时，没有同步评估 token 成本和退役路径。
   - 后续用户要求停掉 `Comics Bootstrap Smoke`，证明这类样本项目必须有成本止损规则。
4. 生产事故修复后只写了运行留痕，没有把“以后排期如何改”写成版本级约束。

## 4. 漏看的信号
- `prod candidate` 多次因 running gate 无法 apply。
- ghost running 修复反复出现，但当时仍把它作为现场恢复，而不是版本排期风险。
- `V12.next_activation_ready=false` 多轮持续存在，说明 V11 收尾和 V12 激活之间没有足够明确的缓冲门。
- 用户多次关注 7x24 停止、项目接力失败、成本浪费和不必要门禁，说明版本计划没有把“运行成本”和“恢复复杂度”作为显式排期因子。

## 5. 排期调整
1. 后续每个版本 closeout 前增加 `version_closeout_aar_check`。
   - 若本版发生生产事故、切版反复、重大 scope 后移、用户追问遗漏项，即使没有 ETA 超时，也必须写 AAR。
2. 后续版本不得把“下一版 activation gate 修复”长期塞进当前版本末段。
   - 最多允许做 P0 止血；系统性修复必须明确进入下一版需求点或 backlog，并写清补偿窗口。
3. 样本/烟测项目不再默认成为长期硬门禁。
   - 若样本项目只服务一次性平台验证，必须同时给出退出条件、成本上限和 tombstone 策略。
4. `V13` 当前排期调整：
   - `V13-R4` 保持当前主链收口优先级，因为它已经在 review/test 门内。
   - `V13-R6` 必须承接 V11/V12 AAR 输出，把“扁平化配色与关键页面 UCD 收口”写成明确验收，不再只写抽象 view model 减法。
   - `V13-R7` 删除/legacy 批不得早于 R6 的关键 UCD 债务确认，否则容易继续删除/重构，却把用户可见债务留到后面。
5. `V14` 激活前必须读取 V11/V12 AAR。
   - 若 AAR 中列出的排期调整未被 V13 消费或明确豁免，V14 不应标成 ready。

## 6. 防生产事故动作
- 版本排期中必须单独保留 `prod apply / live recheck / ghost running repair / schedule handoff` 缓冲，不把它们藏在“发布推进”一句话里。
- 所有 runtime/schedule/upgrade 事故修复后，要同步判断是否需要新增或调整后续版本测试包。
- 对 `7x24` 连续运行相关缺陷，AAR 必须写清下一次如何通过 probe/gate 防复发，而不是只写“已恢复”。

## 7. 后续跟踪
- owner: `workflow(pm)`
- consuming_version: `V13`
- consuming_items:
  - `V13-R6`: 承接关键页面扁平化配色与 UCD 收口。
  - `V13-R7`: 删除 legacy/fallback 前读取本 AAR，避免删除动作掩盖仍未解决的用户可见债务。
  - `V14 activation`: 读取本 AAR 的排期调整完成情况。
