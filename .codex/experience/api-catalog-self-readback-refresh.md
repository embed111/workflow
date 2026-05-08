# 接口目录 self-readback compare 刷新经验

## 适用范围
- `platform interface catalog` 的 self-readback compare 读面
- `api_catalog_live_regression` / `v6-r2-interface-center-live-regression.md` 这类证据驱动的 compare 刷新
- `platform.interfaces.list/detail` 在 live 运行中的缓存一致性

## 稳定经验
- `platform_interface_catalog_service._catalog_snapshot` 不能只按 `runtime_root` 做缓存键。只要 self-readback compare 依赖当前 `current_version`、gate 报告和最新 `quality/live regression artifact`，缓存键就必须显式带这些 freshness 信号；否则新 artifact 落地后，compare 会一直卡在旧 `stale_per_probe_results`，直到进程重启才显影。
- 更稳的默认是把 route/probe registry 继续单独缓存，但让目录 snapshot 额外吃一个由 self-readback runtime 提供的 `snapshot_token`，至少覆盖：
  - `current_version`
  - 当前 gate report 路径与 mtime
  - quality readback artifact 路径与 mtime
  - live regression artifact 路径与 mtime
- 只补代码还不够；要用定向 probe 锁住“同一路径下先读到 stale artifact，再原地改成 version-matched artifact 后，不手工 `cache_clear` 也能从 `blocked/stale` 自动翻成 `ready`”。当前稳定回归入口是 `scripts/acceptance/verify_api_catalog_self_readback_closure.py`。
- stale live regression artifact 不能继续被 `latest_evidence` 或 `build_platform_interface_catalog_consumption_entry()` 投成 ready。更稳的默认是：旧 artifact 只保留在 `compare.per_probe_results` 里作为 `stale_per_probe_results` blocker，而 `latest_evidence.report_refs` 与项目运营摘要只暴露当前 baseline 对得上的 live artifact；如果还没有 version-matched 证据，就显式退成 `partial/warn`，不要继续把旧路径挂给用户当最近 ready 证据。
- 当 live regression 证据从旧的 markdown 扩成结构化 `summary.json` 时，不能只让 `compare` 认新文件；`latest_evidence`、`project_task_summary.interface_catalog_entry` 和相关 consumption entry 也要复用同一条 version-matched artifact resolution。否则现场会出现“`compare` 已 ready，但 `latest_evidence / project summary` 还停在 partial”的分叉真相。更稳的默认是：先把 live artifact 解析统一收口到 `resolve_self_interface_artifact_refs()`，再让 `metrics/latest_evidence/compare` 共用同一条 baseline-matched live path，并继续用 `verify_api_catalog_self_readback_closure.py` 锁住 refresh fixture 的三处一致性。
- `test/current` 每次刷新到新 baseline 后，都不能假设旧的 exact `api_catalog_live_regression` 会自动继续代表当前版本。像 `2026-04-22 19:03 +08:00` 这轮现场里，`platform.interfaces.detail` 仍挂着旧 `20260422-182822` summary，直到我对 `8092` 重跑 `verify_api_catalog_live_regression.py --expected-version 20260422-183414`，`latest_evidence / compare` 才一起从 `stale_per_probe_results` 翻回 `ready`。更稳的默认是：每次 `test/current` 刷到新版本后，都补一条 exact live regression，并立刻回读 `8090/8092 /api/platform/interfaces/platform.interfaces.detail` 确认两处读面同时 ready。
- `verify_api_catalog_live_regression.py` 的 `host-root` 截图不能继续当成 compare review 的硬门。像 `2026-04-23 13:40 +08:00` 这轮现场里，`8092` 的 list/detail 和 interface-center live probe 其实都已可读，但 headless Edge 在根页截图上卡满 `90s`，整条 compare 会被误冻成 `reject`。更稳的默认是：根页截图只保留为 best-effort 辅助证据；真正的 fail-closed 仍只看 `root_html shell + platform.interfaces.list/detail + interface-center live probe` 三条合同，并用定向 fallback probe 锁住“根页截图超时也不会拖死 live regression”。
- 只把 developer workspace `.test` summary 发现逻辑写成 `_REPO_ROOT.parent` 还不够。开发工作区里这条路径会落到真实 `.repository`，但 deployed runtime 里同样写法只会指到 `.running`，结果 `8090/8092` 继续卡旧 summary。更稳的默认是：artifact search root 同时吃 `current_runtime_source_root().parent`，让部署副本按 `WORKFLOW_RUNTIME_SOURCE_ROOT` 反解真实 developer workspace；隔离 acceptance fixture 若要求 `interface_catalog_entry=ready`，也要自带本地 live-regression summary，别让更晚的外部 summary 抢掉读面。
- 只要已经把某次 version-matched live regression 冻成平台自己的稳定证据，就不能继续让 `platform.interfaces.list/detail` 的 `latest_evidence.report_refs` 和 `compare.per_probe_results[].report_ref` 指向 helper 工作区的 `.test/.../summary.json`。像 `2026-04-24 17:45 +08:00` 这轮现场里，`workflow_testmate` 已经跑出 `20260424-174453` 的 fresh summary，但当前读面仍优先吸 `workflow_qualitymate/.test/20260424-160454-315/...`，导致 helper 临时目录被误当成长久真相。更稳的默认是：把 fresh summary 先发布到 `.running/control/reports/api-catalog-live-regression-<current_version>.json`，再让 self-readback runtime 优先这条 stable target；若 stable target 缺失，再回退到 workspace-local `.test` summary。定向回归仍用 `scripts/acceptance/verify_api_catalog_self_readback_closure.py` 锁住“stable target 优先 workspace-local”，并用 `verify_api_catalog_live_regression.py --base-url http://127.0.0.1:8092 --expected-version <current_version>` 验证 live `report_ref` 已切到 `.running/control/reports/...`。

## 已踩过的坑
- 坑：把 compare 仍旧 blocked 直接归因为“还缺 live regression artifact”，却忽略了服务端 snapshot 已经把旧 artifact 结果缓存住。这样就算后面补了新 artifact，现网读面还是会继续显示旧 blocker，误导 PM 以为 helper 没做对。
  - 避免方式：先区分“真的缺 artifact”还是“artifact 已更新但 snapshot 没刷新”。一旦 compare 依赖文件真相，缓存键必须随文件 freshness 变化，而不是只靠人工重启。
- 坑：只修 `compare.status=blocked`，却放任 `latest_evidence.status` 和 project summary 继续显示 ready。这样用户表面上看到“接口目录已 ready”，实际 compare 里仍挂着旧 baseline blocker，最终会把 stale 证据重新当成现网真相。
  - 避免方式：self-readback 的 ready 投影必须和当前 baseline 对齐；ready 与 stale 不能同时出现在同一条最近证据摘要里。
- 坑：只看到 `workflow gate` 或 `project_ops_live_regression` 已经对新 candidate 转绿，就误以为 `platform.interfaces.detail` 的 self-readback compare 也会自动追到同一 baseline。像 `2026-04-22 19:03 +08:00` 这轮现场里，`test/current` 已是 `20260422-183414`，但读面仍挂着旧 `20260422-182822` exact summary。
  - 避免方式：每次 `test/current` 刷到新 baseline 后，都补一条 `verify_api_catalog_live_regression.py --base-url http://127.0.0.1:8092 --expected-version <current_version>`，再回读 `8090/8092 /api/platform/interfaces/platform.interfaces.detail` 确认 `latest_evidence / compare` 同步 ready。
- 坑：隔离 acceptance runtime 如果只种 `v6-r2-interface-center-live-regression.md`，而不种本地 live summary，后来新增的 developer workspace summary 搜索面就会把更晚的外部 summary 捞进来，导致本地 fixture 明明没问题却被误判成 stale/partial。
  - 避免方式：这类 probe fixture 要么显式种一条 baseline-matched `summary.json`，要么把 artifact roots 限定到本地，不要默认依赖“外部现在还没有更晚 summary”。
