# PM版本目录导航

## 定位
- 本文件只负责维护 `pm/versions/` 下各版本目录的导航、状态与路径索引。
- 本文件不承接治理原则、企业级推进节奏、职责边界或日级现场判断；这些内容统一留在 `pm/PM版本推进计划.md`。
- 本文件也不替代当前 active 版本快照；当前活跃版本指针仍以 `pm/PM当前版本计划.md` 为准。

## 当前版本目录
| 版本 | 状态 | 版本计划 | 说明 |
| --- | --- | --- | --- |
| `V1` | `completed` | `pm/versions/V1/版本计划.md` | 工程质量基线与 7x24 运行稳态 |
| `V2` | `completed` | `pm/versions/V2/版本计划.md` | 交付效率、PM 治理自动化、需求映射收口与 UCD 接棒准备 |
| `V3` | `completed` | `pm/versions/V3/版本计划.md` | 小伙伴专业治理、测试资产覆盖维护与学习闭环 |
| `V4` | `completed` | `pm/versions/V4/版本计划.md` | UCD 深改与低维护价值功能重构 |
| `V5` | `completed` | `pm/versions/V5/版本计划.md` | 高价值新功能与长期能力扩展，并行承接工程质量门禁验收 |
| `V6` | `completed` | `pm/versions/V6/版本计划.md` | 系统基座接口发现与能力目录 |
| `V7` | `completed` | `pm/versions/V7/版本计划.md` | 接口能力消费接线与证据聚合 |
| `V8` | `completed` | `pm/versions/V8/版本计划.md` | 多项目功能基座生命周期 contract 与扁平化工作面二期 |
| `V9` | `completed` | `pm/versions/V9/版本计划.md` | 多项目功能基座 contract 落地与接口目录全量覆盖 |
| `V10` | `completed` | `pm/versions/V10/版本计划.md` | 多项目工作面 residual 收口、接口目录扩面与专业判断体系首版 |
| `V11` | `completed` | `pm/versions/V11/版本计划.md` | 多项目工作面二期、跨项目 compare/readback 与专业判断闭环 |
| `V12` | `completed` | `pm/versions/V12/版本计划.md` | 角色创建、项目点火与运行真相修复 |
| `V13` | `active` | `pm/versions/V13/版本计划.md` | 全仓逻辑边界与冗余实现根治 |
| `V14` | `planned` | `pm/versions/V14/版本计划.md` | 治理成果产品化、性能收口与协作效率二期 |
## 维护规则
1. 当新增版本目录、切换版本状态、调整版本说明或改变版本路径时，更新本文件。
2. 当只发生日级推进、ETA 变化、需求拆分或现场阻塞时，不更新本文件；这些变化统一写回：
   - `pm/PM当前版本计划.md`
   - `pm/versions/<version>/版本计划.md`
   - `pm/versions/<version>/history/YYYY-MM/YYYY-MM-DD.md`
3. 若自动 bootstrap 下一版版本骨架，默认同步补齐本文件。
