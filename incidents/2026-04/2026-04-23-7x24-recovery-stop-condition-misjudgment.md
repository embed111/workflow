# 生产事故记录 | 2026-04-23 | 7x24 恢复收尾条件误判导致连续运行未恢复

- incident_id: `INC-20260423-7x24-recovery-stop-condition-misjudgment`
- severity: `SEV-2`
- environment: `prod`
- detected_at: `2026-04-23T20:38:00+08:00`
- detected_by: `workflow(pm)`
- related_version:
  - `prod_target_version=20260423-202504`
  - `related_fix_commit=1294ca9`
- related_requirement:
  - `V9-R4`
- status: `resolved`
- resolution_time: `2026-04-23T21:21:47+08:00`
- resolution_policy: `must_restore_before_close`
- aar_policy: `defer_until_version_close`
- aar_target_version: `V9`

## 1. 事故摘要
- 在完成代码修复、门禁、`test` 部署和 `prod` 直发后，没有继续把 `7x24` 的恢复条件验到最后。
- 我把“deploy success / manifest 已更新 / PM 快照已刷新”误当成完成条件，导致 `prod` 的 `8090` listener 没恢复时就结束了那一轮。

## 2. 用户面影响
- 形式上看起来像“修复已经上线”，但 `7x24` 实际没有恢复。
- 用户侧会看到：
  - `8090` 不可达
  - `healthz` 不可读
  - 主线/保底下一棒没有真正恢复
- 这属于连续运行保障失效，不只是一次部署尾部疏漏。

## 3. 根因判断
- 直接技术故障属于另一张事故卡：
  - `INC-20260423-prod-runtime-config-permission-denied`
- 这张事故卡记录的是治理/执行层面的独立问题：
  - 收尾条件定义错误
  - 把“发布成功”误当成“7x24 已恢复”
  - 没有继续核对 `8090 healthz + /api/status + mainline/patrol 出口`
- 它是一次流程事故，而不是纯代码事故。

## 4. 正确收尾条件
- 只要触碰 `prod` 停机、重启、直发部署或 supervisor 恢复，收尾必须同时满足：
  - `http://127.0.0.1:8090/healthz` 可读
  - `http://127.0.0.1:8090/api/status` 可读
  - 至少存在一条 `mainline` 或 `patrol` 出口
- 任何一个条件未满足，都不能把这一轮记成“恢复完成”。

## 5. 当前处理要求
- 这张事故卡原本保持 `open`，直到 `7x24` 真的恢复。
- 当前已完成恢复：
  - 清掉重复的 `prod` supervisor
  - 只保留一条新的权威 `pm-main` supervisor
  - 重新确认 `8090 /healthz`、`/api/status`、`/api/schedules` 可读
- 当前后续重点不再是“把 listener 拉起来”，而是避免再因为错误 stop condition 或重复 supervisor 进入同类事故。

## 6. 关联事故
- 技术故障事故：
  - `incidents/2026-04/2026-04-23-prod-runtime-config-startup-permission-denied.md`
- 当前事故是它的“恢复失守”派生事故，不可合并省略。

## 7. 后续避免方向（供版本结束 AAR 展开）
- 把 `7x24` 的收尾条件从“发布链完成”提升成“运行态恢复完成”。
- 所有涉及 `prod` 的值守、修复、直发、升级动作，必须显式带上：
  - listener 验证
  - healthz 验证
  - status 验证
  - mainline/patrol 出口验证
- 把这条规则沉成稳定经验与版本 AAR，而不是继续依赖单轮记忆。

## 8. AAR 约束
- 当前不在本事故卡里直接展开完整 AAR。
- `V9` 结束后，必须补做：
  - `pm/versions/V9/aar/YYYY-MM/<date>-7x24-recovery-stop-condition-misjudgment.md`
- AAR 必须回答：
  - 为什么这次会把错误的 stop condition 当成完成条件
  - 如何把 `7x24` 恢复硬门变成正式操作口径
  - 如何避免“技术事故修了，但连续运行没真正恢复”的二次事故再次出现
