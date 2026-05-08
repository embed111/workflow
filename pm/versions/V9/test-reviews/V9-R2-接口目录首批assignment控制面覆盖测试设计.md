# V9-R2 接口目录首批 assignment 控制面覆盖测试设计

- version: `V9`
- requirement_id: `V9-R2`
- reviewed_at: `2026-04-23T07:48:00+08:00`
- owner: `workflow(pm)`

## 1. 回归目标
- 证明首批 `assignment` 控制面接口已经脱离 `metadata incomplete`，不再只靠代码发现占位。
- 保持 `platform.interfaces.list/detail` 既有 self-readback compare 不回退。

## 2. 本轮断言
- 接口目录列表里能直接找到首批 12 条 `assignment` 控制面 interface_id。
- 至少抽查以下 detail payload：
  - `get:assignments`
  - `get:assignments.param1.status.detail`
  - `post:assignments.param1.dispatch.next`
  - `post:assignments.param1.nodes`
  - `delete:assignments.param1.nodes.param2`
- 抽查 detail 时至少断言：
  - `metadata_status=complete`
  - `summary/description` 非空
  - `root_guard.mode=required`
  - `request_body/response_fields` 已有正式说明

## 3. 测试资产
- 继续沿用 `verify_api_catalog_contract.py`
- 如需补首批 batch 断言，可在同脚本内扩展，不新造平行 smoke

## 4. 评审结论
- `pass`
- 本轮以 focused acceptance 锁住首批 interface metadata，metrics/evidence 扩面留给后续批次。
