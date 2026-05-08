# V9-R2 接口目录首批 assignment 控制面覆盖方案评审

- version: `V9`
- requirement_id: `V9-R2`
- reviewed_at: `2026-04-23T07:48:00+08:00`
- owner: `workflow(pm)`
- collaborators: `workflow_devmate / workflow_testmate / workflow_qualitymate`

## 1. 背景
- `platform.interfaces.list/detail` 的 self-readback compare 已经回到 `ready`，`V9-R2` 不再卡在 stale compare。
- 当前目录里仍有大批 `assignments` 接口停在 `metadata_status=incomplete / metrics_status=unavailable`，直接影响主线派单、状态详情、节点管理和当前 live 排障。
- 这轮不追求全量 122 条一次吃完，先切一批和 active 版本直接相关、可当天验证的 `assignment` 控制面接口。

## 2. 首批覆盖范围
- `get:assignments`
- `post:assignments`
- `get:assignments.settings.concurrency`
- `post:assignments.settings.concurrency`
- `get:assignments.settings.execution`
- `post:assignments.settings.execution`
- `post:assignments.test.data.bootstrap`
- `get:assignments.param1`
- `get:assignments.param1.status.detail`
- `post:assignments.param1.dispatch.next`
- `post:assignments.param1.nodes`
- `delete:assignments.param1.nodes.param2`

## 3. 方案判断
- 先用 registry 补齐正式目录元数据，而不是继续让这些接口停在代码发现占位。
- 首批只要求 `metadata_status=complete` 和可读的 request/response/root-guard 合同；`metrics` 暂不伪装成 ready，保持 `unavailable/partial` 的真实口径。
- 同轮补一条 focused acceptance，锁住这批 interface_id 和关键字段，不把这轮成果只留在人工手看。

## 4. 风险与护栏
- 风险：一口气扩太大，会把 `V9-R2` 重新做成“大而空”的目录重写。
- 护栏：
  - 只做首批 12 条控制面接口
  - 不碰 metrics 聚合链
  - 必须落自动化 probe，防止回退成 `待补目录元数据`

## 5. 评审结论
- `go`
- `V9-R2` 从这轮开始正式进入“首批 assignment 控制面覆盖实现”，下一步由 `workflow_devmate` 承接 registry + probe 落地。
