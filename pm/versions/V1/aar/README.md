# V1 版本 AAR

## 定位
- 本目录用于保存 `V1` 中因需求延期、预计完成时间失准或明显偏差触发的版本 AAR。
- 只有命中“需求完成时间超时”或同级别偏差时才写，不把普通日常推进流水灌进 AAR。

## 路径规则
- 路径模式：`pm/versions/V1/aar/YYYY-MM/YYYY-MM-DD-<requirement_id>.md`
- 同一天若多个需求超时，可以有多份 AAR

## 触发条件
- 某个需求点超过上一轮承诺的 `预计完成时间`
- 本轮没有先重设 ETA，而是直接进入延期状态
- 或虽然未显式超时，但已出现明显判断偏差，需要正式复盘

## 最低内容
- `requirement_id`
- `previous_eta`
- `current_status`
- `delay_reason`
- `misjudgment`
- `signals_missed`
- `corrective_actions`
- `next_eta`
