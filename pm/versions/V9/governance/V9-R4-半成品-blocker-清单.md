# V9-R4 半成品 blocker 清单

- version: `V9`
- requirement_id: `V9-R4`
- created_at: `2026-04-23T02:15:31+08:00`
- owner: `workflow(pm)`

## 1. 默认 blocker
- 只有主题词，没有真实 probe/evidence 路径
- 只有 planned 文档，没有 helper batch、run report 或 live evidence
- 结论写成“ready/可切版”，但 `/api/status.pm_version_board.activation_summary` 仍显示 hard fail
- 版本判断已经切到下一版 blocker，却没有同步把当前版与下一版 history/plan 追平

## 2. 当前命中的 blocker
- `V9-R1 / V9-R3 / V9-R4` 之前都存在 placeholder refs
- `V9` 仍缺 implementation/live evidence，因此本轮即使补完 binding 资产，也不能误报 `next_activation_ready=true`
- `V9-R2` 当前在 `test/current=20260423-133937` 上已经可读，但 `api_catalog_live_regression` 仍因 `host-root` 截图超时留在旧 baseline，导致 compare.status=blocked

## 3. 放行条件
- placeholder refs 已替换成真实路径
- 至少一条 helper batch 已经起跑并指向这些绑定资产
- `blocking_items` 改写成当前真正剩余的 implementation/live evidence 缺口

## 4. 不放行条件
- 只补 history / logs / 今日日记
- 只新增抽象文档，不形成 activation 绑定或 helper 承接
- 只说“下一步做 R1/R3/R4”，但没有任何实际派发或路径落点
- 明知 sample surface 已经在部署态可读，却因为 harness 附属证据失败而继续把 compare 误报成“待观察”
