# 运营项目概念收口与 V5 排期

- timestamp: `2026-04-18T11:56:22+08:00`
- preference_ref: `state/user-preferences.md`
- scope: `concept-governance / version-planning`

## 本轮结论
- `workflow` 定位正式上提为长期持续运行的项目底座。
- “运营项目”成为产品中的一等实体。
- `7x24` 默认唤醒对象统一收口为“项目主控角色”。
- 当前任务看板后续收口为通用执行面；项目特有信息后续进入独立项目看板。
- 这条能力不插入当前 `V4`，正式挂到 `V5-R4`。
- 为控制不同项目消耗，`V5-R4` 额外纳入“项目下一棒接力间隔可在界面调整”。

## 本轮产物
- `docs/workflow/requirements/需求详情-运营项目与项目主控角色模型.md`
- `pm/versions/V5/版本计划.md`
- `pm/versions/V5/需求映射与覆盖矩阵.md`
- `pm/versions/V5/history/2026-04/2026-04-18.md`
- `pm/versions/V4/history/2026-04/2026-04-18.md`

## 增量观察
- delta_observation: 用户已稳定确认后续产品应按“底座 -> 运营项目 -> 项目主控角色/领域角色 -> 项目看板/通用任务看板”分层，不再把 `PM` 写死成唯一主控名，也不把项目类型限定为软件团队。
- delta_validation: 后续进入实现前，先为 `V5-R4` 补项目模型字段合同、项目看板最小字段、接力间隔交互合同和项目模板最小 probe。
