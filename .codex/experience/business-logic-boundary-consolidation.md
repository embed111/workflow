# 业务逻辑边界收口经验

## 适用范围
- 服务层业务逻辑已经被大量拆成 `*_parts`、support runtime 或 manifest bundle
- 为了通过行数门禁持续 split，但调用链、入口和领域职责反而变得更难追踪
- `assignment / schedule / role creation / project / runtime truth` 这类跨域链路出现修一处漏一处、性能慢链路或读写真相分叉

## 稳定经验
- 不要把“文件变小”直接当成“业务逻辑变清楚”。如果同一条业务流程被拆到多个 part，却仍依赖隐式全局符号、manifest 顺序或跨模块私有函数，那么复杂度只是从单文件内部转移到了调用链和装配层。
- 处理这类问题时，优先做“领域边界和用例入口收口”，而不是继续横向新增 helper 文件。更稳的默认是先画出 `用户动作 -> application use case -> domain service -> repository/projection -> response` 的主链，再决定哪些 part 合并、哪些 part 私有化、哪些入口废弃。
- `exec_local_parts(...)` 这类把多个文件执行进同一 module globals 的拆片方式，只适合短期解超大文件压力；长期业务核心不应继续依赖隐式全局符号。后续重构应逐步迁到显式 import、显式 `__all__`、TypedDict/dataclass contract 和 application facade。
- 跨域链路要先定唯一写入口和唯一读模型。例如 `schedule trigger -> assignment node -> dispatch -> run truth -> status/readback` 这类链路，不能让 schedule、assignment、project、runtime-upgrade 各自投影一份状态后再靠补丁对齐。
- 行数门禁后续应同时配合“边界门禁”：新增 split 必须说明 owner domain、公开入口、禁止反向依赖和最小 probe；否则只会把 Mandatory Gate blocker 平移成业务理解成本。

## 最小处理顺序
1. 冻结高频主链：先选最近真实出事故或最高价值的链路，不做全仓一次性大重构。
2. 建业务地图：列出主入口、写入口、读模型、状态字段和跨域依赖。
3. 建 application facade：API 层和其他域只调 facade，不直接碰 part 内部函数。
4. 收口状态机：把状态枚举、状态转换和终态判定集中到一个 contract runtime。
5. 收口存储与投影：把写模型和 read model 明确分层，避免多个模块重复拼装同一份真相。
6. 补定向 probe：每次收口只锁当前主链的红灯/绿灯，不用全量回归替代架构判断。

## 已踩过的坑
- 坑 1：为了让超长文件退出行数门禁，连续新增 support part，但没有同步收口公开入口和依赖方向，后续排障时反而要跨更多文件追同一条业务流。
  - 避免方式：split 必须带 use-case 入口和 contract probe；没有入口收口的 split 只能算临时止血。
- 坑 2：多个读面分别计算运行状态，导致 `run / node / project / status` 对同一件事给出不同真相。
  - 避免方式：先确定 terminal truth 和 projection owner，再让其他读面消费同一份投影，不再各自猜状态。
