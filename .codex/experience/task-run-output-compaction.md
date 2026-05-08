# 任务运行输出精简经验

## 适用范围
- 任务中心真实执行 trace
- 节点详情里的运行批次展示
- `stdout/stderr/events` 体积控制与 token 成本收口

## 稳定经验
- 任务中心运行详情不要默认回传 `prompt/stdout/stderr/result` 全文。后端应只回预览文本，并附“已截断 + 引用路径”提示；完整内容留给磁盘引用路径按需查看。
- `stdout/stderr/events.log` 这类 trace 文件要加体积上限，否则一次长输出就会同时拖慢落盘、详情接口和前端渲染。当前验证过的保守上限可先用：
  - `stdout.txt`: `96KB`
  - `stderr.txt`: `96KB`
  - `events.log`: `128KB`
- capped `events.log` 不能把尾部裁成坏 UTF-8。更稳的默认是：写入侧只保留完整字符边界，读取侧也按 `errors='ignore'` 容忍被上限裁断的尾巴；否则同一条 running run 会在 `latest_event` 仍然存在时，把 `status-detail.event_count/events` 整体打回 `0/[]`，前端和 smoke 都会被误导成“运行详情空白”。
- `events.log` 不能直接把 stdout 事件里的整段 JSON detail 原样写回去；应先做 detail 压缩，只保留有限层级、有限字段和有限字符串长度。
- 前端标题要明确写成“预览”，不要继续标“完整提示词/最终结果”，否则用户会误以为当前面板看到的就是全文。
- `/api/status` 这类 workboard 预览也不能直接透传节点里的完整 `failure_reason / success_reason`；更稳的默认是只给短预览，把完整文本继续留在 `status-detail / result_ref`。否则 self-iteration 失败节点一旦保留结构化结果或旧提示词，状态面板 payload 就会被历史大段文本重新撑胖。
- assignment worker 的最终 `artifact_markdown` 也必须有服务端长度保护。像 `2026-04-27 02:02/02:46` 主线失败里，报告正文过长会在 worker bootstrap 阶段直接打成 `artifact_markdown too long`，让本该成功的 7x24 轮次失败；更稳的默认是产品侧截断/落引用，agent 侧在相关修复进入 prod 前主动把交付报告控制在短正文内。
- `artifact_files` 是交付投影的源文件清单，不是“我本轮写过的所有文件”。如果某个文件必须继续留在 role workspace 或 PM workspace 中作为长期源资产，就不要把它放进 `artifact_files`；否则 delivery 收集后可能按清理策略移走源文件。更稳的默认是：保留型源文件写入目标 workspace，最终报告只在 `artifact_markdown` 引用路径，`artifact_files=[]`。
- helper role workspace 的根目录不要被临时报表和结果文件长期占满。更稳的默认是：真实产物写入已有子目录；若模型仍在根目录生成新的 `.md/.json/.html/.txt/.log` 顶层文件，finalize 应按本轮前后快照把新增文件归档到 `logs/root-artifact-archive/<date>/<run_id>/`，避免 helper 根目录逐渐变成垃圾场。

## 已踩过的坑
- 坑 1：只压接口、不压磁盘 trace，会让页面轻一点，但 `stdout.txt/events.log` 还是继续膨胀，慢问题和存储问题都没真正收口。
  - 避免方式：同时做“落盘上限 + 接口预览”双收口。
- 坑 2：把 `events.log` 复用到带时间戳的普通文本 append helper，会破坏 JSONL 结构，后续 tail/解析全部失效。
  - 避免方式：`events.log` 单独走 raw append；可以限体积，但不能额外包时间戳前缀。
- 坑 3：`events.log` 达到体积上限后，如果尾部提示文案直接按原始 bytes 硬切，UTF-8 会被裁断；后续 `_tail_assignment_run_events()` 一读就抛解码异常，`status-detail` 和 live browser probe 会一起把 `event_count` 误报成 `0`。
  - 避免方式：截断时只写完整 UTF-8 前缀；读取时也按容错解码保留可解析前缀，不要因为尾部坏字节把整份 trace 判空。
- 坑 4：只压 `stdout/stderr/events`，但不压最终交付字段，会让“运行过程可读”却在最终收尾时失败。
  - 避免方式：`result_summary / artifact_markdown / warnings / failure_reason` 都按同一套长度预算处理，超限内容写引用路径；在新修复尚未 apply 到 prod 前，本轮报告优先保持短而完整。
- 坑 5：把需要保留在角色工作区的案例卡源文件列进 `artifact_files`，会让 delivery 投影成功但源工作区文件被清理，PM 读面误以为“交付成功等于源资产保留”。
  - 避免方式：保留型角色资产一律用目标 workspace 文件真相验收；交付报告只返回短摘要和路径引用，`artifact_files` 留空，除非该文件本身就是临时交付件且允许被收集清理。
