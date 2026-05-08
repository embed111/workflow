# V8 测试设计评审索引

## 当前状态
- 历史 gate、probe 和 live regression 继续作为真实测试证据使用。
- 但按新流程，后续仍在推进的需求还要把“测试设计为什么这样配、哪些场景算准入、哪些场景是回归组”正式沉在这里。

## 当前待补清单
| 需求点 | 当前状态 | 后续正式文件建议 |
| --- | --- | --- |
| `V8-R1` | 已有 gate/probe，待补测试设计评审 | `V8-R1-lifecycle-contract-测试设计评审.md` |
| `V8-R2` | 已完成测试设计评审，当前继续补 controller cadence live chain | `V8-R2-platform-role-contract-测试设计评审.md` |
| `V8-R3` | 已完成测试设计评审；current slice 由 focused regression + workflow gate 锁定 | `V8-R3-flat-surface-phase2-测试设计评审.md` |
| `V8-R5` | 已完成测试设计评审，当前验证口径为 fixture + gate + live auto fallback | `V8-R5-performance-baseline-测试设计评审.md` |
