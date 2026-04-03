# 正式升级与长任务监控经验

## 适用范围
- `prod` 正式升级链路
- 可能超过 3 分钟的 agent 调用
- 部署副本启动与运行时配置同步
- 工作区升级 banner 与训练优化 create 态前端回归

## 稳定经验
- 长任务 agent 调用不要使用固定总超时。只要子进程仍在正常运行并持续有状态，就继续等待；只有进程异常或无结果且无运行迹象时才判失败。
- 长耗时验收脚本不能只依赖底层默认 HTTP 超时或静默轮询。只要单步可能超过几十秒，就要补阶段 checkpoint、heartbeat 日志和 partial summary 落盘；否则用户体感会变成“Codex 直接退了”，即使真实问题只是脚本无输出或请求超时。
- 开发环境验证 agent 调用时，优先通过环境变量覆写注入 mock，并在验收脚本或开发环境内隔离，禁止让 mock 配置进入 `test/prod` 正式链路。
- 正式升级优先走受支持接口 `POST /api/runtime-upgrade/apply`，由 `scripts/start_workflow_env.ps1` 托管进程接管切换、健康检查与回滚，不要手工拷贝覆盖运行目录。
- 部署副本启动前，要用 manifest/runtime descriptor 回写 `.runtime` 内的关键配置，尤其是 `agent_search_root`、`artifact_root`、`task_artifact_root`，否则部署副本容易沿用旧路径。
- 升级 banner 这类顶部浮层不能只看接口返回或 DOM 节点是否存在；必须补真实截图。字段赋值前一旦有前端异常，页面会留下“标题还在、正文全空”的假渲染。
- 训练优化 create 态不要直接复用 status 态的完整能力卡。create 阶段信息密度更高，中部主列又更窄，应该用更紧凑的草案卡和更短的对话文案。
- 训练优化 create 态要判断“是否真正铺满父容器”，不能只看 `composer_bottom_gap/right_bottom_gap=0`。必须同时对照“创建角色”界面的壳体模型，确认 `detail_body` 与 `chat_shell` 顶底完全对齐、底部 composer 用 `border-top` 直接贴底、右侧由外层 panel 承担壳体而不是内层再套一张大卡片。
- 拼接式前端 CSS 一旦上游文件少一个 `}`，后续样式文件会被级联污染，表面症状往往落在下游页面。训练优化样式回归时，要同时检查合并后的 `/static/workflow-web.css` 和 probe 里的计算样式，不要只盯当前 CSS 文件。
- `scripts/start_workflow_env.ps1` 这种长驻 supervisor 脚本一旦已经启动，就会把当时的逻辑常驻在内存里。后续只改磁盘文件不会影响当前正在跑的 supervisor；如果本轮修的是升级/健康检查逻辑，必须先重启 `prod` 的 supervisor，再重新发起正式升级。

## 已踩过的坑
- 坑 1：把长任务 agent 调用按固定 180 秒超时处理，首轮策略分析会因为真实执行时间不稳定而大量误判失败。
  - 避免方式：改成“进程存活监控 + 结果收敛”，并增加单独验收用例覆盖长调用。
- 坑 2：页面提示“正式升级正在切换中”后卡住，前端重连态没有根据后端终态及时消退。
  - 避免方式：重连与成功态统一以后端 `/api/runtime-upgrade/status` 的 `request_pending`、`last_action`、当前版本为准，不使用前端本地粘滞态当真相源。
- 坑 3：部署副本切换后仍沿用旧 runtime 配置，导致工作区路径或产物路径漂移。
  - 避免方式：启动部署副本前显式同步 runtime-config，并在正式升级后核对 manifest、instance、healthz 三处状态是否一致。
- 坑 4：升级 banner 只渲染出标题和空白骨架，误以为是后端没返回数据，实际是前端 refs 漏登记后在赋值前抛异常。
  - 避免方式：给 banner 结构节点做完整 refs 登记；修这类浮层时同时检查“字段赋值”和“display/aria-hidden”是否被硬编码覆盖。
- 坑 5：训练优化 create 态复用 status 卡片后，中部能力卡文本堆叠、右侧预览又挤占宽度，真实截图看起来像“样式没生效”。
  - 避免方式：create 态单独收口卡片结构，优先保证主阅读区单列可读；右侧演进图在 create 态取消大 `min-width` 横向挤压。
- 坑 6：上游 CSS 文件语法断裂后，`workflow-web.css` 里后续训练优化规则虽然还能看到文本片段，但浏览器计算样式已经回退成默认块级布局，导致中部输入区和右侧铺满同时失效。
  - 避免方式：训练优化布局异常时，优先检查拼接后的 `/static/workflow-web.css` 是否在当前文件前一段出现未闭合规则；再用 `tc_probe=1` 输出 `display/clientHeight/scrollHeight` 验证真实生效情况。
- 坑 7：布局探针已经显示 gap=0，但真实截图仍然像“没有铺满”，根因是中部和右侧仍在使用“卡片套卡片”的嵌套壳，视觉上和创建角色单壳体完全不是一个模型。
  - 避免方式：出现这类反馈时，不要继续微调 `padding/gap/max-height`；直接把训练优化 create 态改成创建角色同款的“头部固定 + 中间滚动 + 底部贴底 composer / 右侧 outer panel + inner scroll”结构，再重新截图验证。
- 坑 8：已经把 `start_workflow_env.ps1` 的升级健康检查超时修到磁盘了，但正式环境仍然继续按旧的 60 秒逻辑回滚，原因不是补丁没生效，而是当前 `prod` supervisor 进程早就把旧脚本加载进内存了。
  - 避免方式：凡是修正式升级 supervisor 逻辑，补丁落盘后都要先重启 `prod` 的 `start_workflow_env.ps1` 进程，再重试 `/api/runtime-upgrade/apply`；不要直接假设现网 supervisor 会热加载脚本改动。
- 坑 9：角色创建 creating 清理删除链路里，脚本先补做 starter task 的交付/完成，再等待 delete 开放；如果这段没有 heartbeat，十分钟内都可能没有任何输出，外部观察者会误判成“整体退出”。
  - 避免方式：验收脚本对“本地慢步骤 + 慢 HTTP 请求”都加 heartbeat；同时不要复用底层固定 180 秒 HTTP 超时，改用可配置长超时。
- 坑 10：验收脚本继续断言“cleanup 后 assignment graph 必须 404”，但产品真实语义已经变成“图可能为空而非物理删除”，会制造假失败。
  - 避免方式：每次优化产品清理语义后，同步回看 acceptance 断言；只断言用户可感知/契约级结果，不把历史内部实现细节当成稳定门禁。

## 最小检查清单
1. 升级前确认 `/api/runtime-upgrade/status` 返回 `can_upgrade=true` 且 `running_task_count=0`。
2. 升级后确认 `/healthz` 恢复、`current_version` 已切到候选版本、`request_pending=false`。
3. 再核对 `.running/control/envs/prod.json`、`.running/control/prod-last-action.json`、`.running/control/instances/prod.json` 三处版本一致。
4. 涉及升级 banner 或训练优化布局时，补一组真实截图，不接受只看 DOM/接口。
