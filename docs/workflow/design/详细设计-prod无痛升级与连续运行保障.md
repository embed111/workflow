# 详细设计-prod无痛升级与连续运行保障

## 1. 目标
1. 回答当前正式环境升级是否已经可以“不影响定时任务和正在运行任务”。
2. 给出一条适配 `workflow` 当前单机三环境架构的无痛升级演进路线。
3. 把“7x24 连续运行 + 正式升级 + 定时任务 + 任务执行”统一到同一套运行真相源和恢复策略上。

## 2. 当前结论
1. 现在还做不到“不影响正在运行任务”的正式升级。
2. 当前正式升级只能做到：
   1. `running_task_count = 0` 时快速切换到新 candidate。
   2. 若切换后健康检查失败，回滚 app 副本。
   3. 若升级前后进程异常退出，依赖 supervisor/watchdog 再拉起 Web。
3. 当前正式升级也还不能严格保证“不影响定时任务”。
   1. 已命中的 trigger 会落盘，但 trigger 后续的“建单 / 派发 / 回写”仍然依赖当前进程内线程。
   2. Web / runtime 重启期间，如果线程未完成，后续只能靠恢复扫描补做，不是天然无损连续。

## 3. 当前实现事实

### 3.1 升级门禁现状
1. `runtime_upgrade.py` 在 `POST /api/runtime-upgrade/apply` 前，会先读取：
   1. 会话运行数 `active_runtime_task_count`
   2. assignment 运行数 `get_assignment_runtime_metrics(...).running_task_count`
2. 只要 `running_task_count > 0`，就直接阻断升级。
3. 这说明当前产品语义是：
   1. 不尝试保护运行中任务跨升级连续执行。
   2. 而是要求“先等运行中任务清空，再升级”。

### 3.2 升级切换路径现状
1. `runtime_upgrade_service.write_prod_upgrade_request()` 只负责写 `prod-upgrade-request.json`。
2. 随后 `schedule_runtime_shutdown()` 触发当前 Web 进程退出，退出码是 `73`。
3. `.running/prod/scripts/start_workflow_env.ps1` 里的 supervisor 进程检测到这个退出码后：
   1. 读取 candidate
   2. 拷贝 candidate app 到 `deploy_root`
   3. 更新 manifest / deployment metadata
   4. 启动新版本
   5. 健康检查
   6. 失败时回滚
4. 这里的关键事实是：
   1. 当前是“停旧进程 -> 切 app -> 起新进程”的切换，不是双进程平滑切流。
   2. 运行中任务如果依赖旧 Web 进程内状态，升级时必然受影响。

### 3.3 定时任务现状
1. `schedule_service.run_schedule_scan()` 命中计划后，只把 `trigger_hit` 快速落盘。
2. 真实的 `create_node / dispatch / writeback` 在 `_start_schedule_trigger_processing()` 启的后台线程里继续跑。
3. 这解决了“慢建单把 scan 卡死”的问题，但线程仍然挂在当前进程里。
4. 因此当前定时任务的连续性语义是：
   1. 命中过了，基础留痕能保住。
   2. 后续处理若被重启打断，需要恢复扫描或 detail 读取来补偿。
   3. 不是天然的跨升级不中断。

### 3.4 运行中 assignment task 现状
1. assignment execution worker 现在由当前 runtime 进程内的执行链调起。
2. 虽然已有：
   1. stale run recovery
   2. final_result/result.json 文件恢复
   3. schedule 自迭代续挂
3. 但这些都属于“失败后收口 / 重启后恢复真相”，不是“新进程接管旧进程中的活任务”。
4. 当前还没有：
   1. 独立于 Web 进程生命周期的任务 worker supervisor
   2. 可迁移的 execution lease / ownership
   3. 运行中子进程的跨升级 re-attach 协议

## 4. 为什么现在做不到无痛升级
1. 升级门禁语义本身就是“有运行中任务就不让升”，而不是“边跑边升”。
2. schedule trigger processing 仍是进程内线程，不是持久化 job worker。
3. assignment 执行句柄仍主要依赖当前进程，不是外部可接管 worker。
4. 顶栏 `running_task_count` 与 workboard/file 真相仍然可能错位，说明运行真相源还没有完全统一。
5. `prod` supervisor 目前能解决“掉了再拉回”，但不能解决“不中断切流”。

## 5. 无痛升级目标定义

### 5.1 最终目标
1. 正式升级时，不中断已命中的定时任务。
2. 正式升级时，不中断正在运行的 assignment task。
3. 页面端只出现极短重连或完全无感切换。
4. 升级失败时可自动回退，且不丢运行真相。

### 5.2 分阶段目标
1. Phase A：先做到“有任务时不升级，但升级前主动 drain 且不丢定时触发”。
2. Phase B：再做到“升级 Web 不影响 schedule trigger processing”。
3. Phase C：最后做到“升级 Web 不影响正在运行的 assignment task”。

## 6. 推荐演进方案

### 6.1 Phase A：有损最小化，不假装无痛
- 目标：先把当前方案从“硬阻断升级”升级成“可控 drain + 不丢 trigger”。
- 方案：
  1. 升级前进入 `upgrade_draining` 状态。
  2. `schedule scan` 继续允许命中并写 trigger，但暂停新的 dispatch。
  3. 任务中心停止分派新的 ready 节点，只允许当前 running 自然收尾。
  4. 所有 drain 期间新命中的 schedule 只落 `trigger_hit/queued`，升级后新进程补做 processing。
- 成本：低到中。
- 收益：先解决“升级前后 schedule 漏触发 / 重复触发 / 误派发”的主要风险。
- 局限：仍然不能在有 running task 时真正升级。

### 6.2 Phase B：把 schedule trigger 从进程内线程改成可恢复 job
- 目标：让定时任务在 Web 升级时不断链。
- 方案：
  1. 新增持久化 `schedule_trigger_jobs` 或复用现有 trigger 表增加 `lease_owner / lease_until / processing_stage`。
  2. `_start_schedule_trigger_processing()` 不再只起内存线程，而是：
     1. 抢 lease
     2. 跑一步记一步 stage
     3. 新进程可续接未完成 stage
  3. 对 `create_node / dispatch / writeback` 全链做幂等。
  4. supervisor 拉起新版本后先跑一次 trigger recovery，再开放正常 scan。
- 成本：中。
- 收益：可以做到“Web 升级不影响定时任务”。
- 风险：幂等和 lease 做不好会带来重复建单/重复派发。

### 6.3 Phase C：把 assignment execution 从 Web 生命周期里剥离
- 目标：让正在运行的任务不被 Web 升级打断。
- 方案：
  1. 引入独立的 assignment worker supervisor。
  2. Web 只负责：
     1. 建立 execution request
     2. 更新 run 状态
     3. 展示和调度
  3. 真正的任务执行进程由 worker supervisor 托管，升级 Web 不杀 worker。
  4. run record 持久化 `worker_owner / process_handle / heartbeat / lease`。
  5. 新 Web 进程只需重新 attach 到 run record，不需要接管旧 Python 子进程的内存对象。
- 成本：高。
- 收益：这是“真正无痛升级不影响运行中任务”的关键前提。
- 风险：要处理 worker 与 Web 的一致性、失联、孤儿进程、重复消费。

### 6.4 Phase D：单机蓝绿切换
- 目标：让页面侧尽量无感。
- 方案：
  1. 新版本先在备用端口起健康实例。
  2. 旧实例进入 drain。
  3. 通过 supervisor/前置代理切换 `8090 -> new listener`。
  4. 旧实例在 drain 完成或超时后退出。
- 成本：中到高。
- 收益：页面侧更接近无感。
- 前提：
  1. Phase B 先完成，否则 schedule 线程还是会丢。
  2. 若想不影响 running task，Phase C 也要完成。

## 7. 推荐落地顺序
1. 先做 Phase A。
   1. 这是当前代码base最小扰动、收益最高的第一步。
2. 再做 Phase B。
   1. 这样可以先保证“升级不丢定时任务”。
3. 最后做 Phase C。
   1. 不拆执行 worker，就不可能真正保证“升级不影响运行中任务”。
4. Phase D 视资源决定是否跟进。
   1. 如果页面短重连可以接受，D 可以晚于 C。

## 8. 对“现在能不能做到”的明确回答
1. 现在不能做到“正式环境升级不影响定时任务以及正在运行的任务”。
2. 现在只能做到：
   1. 在无运行中任务时升级。
   2. 升级失败时自动回滚 app 副本。
   3. 重启后依赖恢复逻辑收口 schedule/run 真相。
3. 若要先拿一个短期改进目标，我建议优先承诺：
   1. 先做到“升级不丢 schedule trigger”。
   2. 再做到“升级不影响 running task”。

## 9. 小伙伴分工建议
1. `workflow(pm)`
   1. 负责总方案、阶段切换、门禁定义、版本计划维护和最终升级决策。
2. `workflow_devmate`
   1. 负责 Phase A 的 drain 模式、升级门禁、manifest/runtime 状态流收口。
3. `workflow_bugmate`
   1. 负责 Phase B/C 的高风险恢复链：trigger lease、job 恢复、执行句柄/worker 失联场景。
4. `workflow_testmate`
   1. 负责升级场景回归矩阵：
      1. 无任务升级
      2. drain 中升级
      3. schedule 命中时升级
      4. running task 时升级
      5. 回滚后恢复
5. `workflow_qualitymate`
   1. 负责：
      1. 升级前后质量闸口
      2. 定时任务/任务中心/运行真相一致性巡检
      3. 24 小时升级后观察项

## 10. 当前推荐任务包
1. `V1-P5` 升级 drain 模式与升级前冻结新派发
   1. owner: `workflow_devmate`
   2. 目标：升级期间不再新增 dispatch，但 schedule 命中不丢。
2. `V1-P6` schedule trigger 持久化恢复模型设计与最小实现
   1. owner: `workflow_bugmate`
   2. 目标：重启后 trigger processing 可续接。
3. `V1-P7` 正式升级连续性回归矩阵
   1. owner: `workflow_testmate`
   2. 目标：把升级场景从“人工拍脑袋”变成固定 smoke。
4. `V1-P8` 升级前后运行真相一致性巡检
   1. owner: `workflow_qualitymate`
   2. 目标：顶栏、workboard、run 文件、schedule detail 四处口径一致。

## 11. 当前轮执行建议
1. 当前先不要承诺“正在运行任务无痛升级已完成”。
2. 当前对外口径应明确为：
   1. 已有快速升级 + 回滚。
   2. 仍未实现 running task 无损接管。
   3. 下一阶段先做 drain + trigger 无损，再做 worker 解耦。
