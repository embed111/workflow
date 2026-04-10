# 经验索引

## 先读这里
- 本文件是每轮正式工作前的经验入口。
- 先读“必读经验”，再按需扩展阅读其他经验卡。
- 经验卡只记录可复用模式、踩坑复盘与规避动作，不记录单次流水账。

## 必读经验
- `runtime-upgrade-and-agent-monitoring.md`

## 经验文件
- `runtime-upgrade-and-agent-monitoring.md`
  - 适用范围： 正式升级、长任务 agent 调用、部署副本启动
  - 原因： 最近多次触发升级卡住、长任务超时、部署副本配置漂移，以及 stale pid 误拦截部署，属于高复用高风险经验
  - 更新时间： 2026-04-10
- `dual-repo-boundary-and-dev-workspace-bootstrap.md`
  - 适用范围： `workflow / workflow_code` 双仓边界、开发工作区 bootstrap、代码仓受保护根
  - 原因： 新一轮代码与 agent 分离改造已经形成稳定边界与 Git 使用约束；同时补充了 bugfix mirror scoped patch、prod 热修回放、PM 仓代码副本清理约束，以及 release boundary 跨轮滞留时的根仓同步优先级
  - 更新时间： 2026-04-09
- `task-run-output-compaction.md`
  - 适用范围： 任务中心运行 trace、节点详情输出、`stdout/stderr/events` 体积控制
  - 原因： 任务运行详情默认回传全文会直接拖慢页面和消耗 token，这类收口策略后续会持续复用
  - 更新时间： 2026-04-05
- `schedule-trigger-closure.md`
  - 适用范围： `定时任务 -> 任务中心` 命中建单、pm/`workflow` 周期唤醒、自迭代失败恢复、stale recovery 与 follow-up dispatch 串行化
  - 原因： schedule 命中链路如果同步等慢建单/派发，极易留下 `trigger_hit` 半断裂现场；同时 stale recovery 若在 finalize 里递归 dispatch，会把同 ticket 派发锁直接卡死；另外保底巡检如果只看 future 入口，也会漏掉 `0 running + ready 堆积` 的假健康。这类闭环、恢复和巡检口径后续会持续复用
  - 更新时间： 2026-04-09
- `module-parts-runtime-binding-and-role-memory-scaffold.md`
  - 适用范围： 拆片服务模块的离线验收、角色工作区记忆脚手架、私有 helper 直调验证
  - 原因： `role_creation_service` 这类 module-parts 服务直接导入时，运行时符号默认未绑定；如果验收绕过 runtime 绑定去裸调 helper，会得到误导性的 `NoneType` 故障
  - 更新时间： 2026-04-08

## 更新规则
- 新经验优先补到已有经验卡；仅当主题明显不同再新建文件。
- 每次新增经验卡时，同步更新“必读经验”或“经验文件”引用。
- 如果只是一次性现象、还没验证稳定结论，不进入经验卡，只留在当日日记。
