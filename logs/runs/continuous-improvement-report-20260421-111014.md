# Continuous Improvement Report

## 判断
- `version_transition_decision=stay(V5)`
- 我这轮的主推进归类为 `当前需求开发 / 发布推进`：真正的新切片已经不再是“healthy project 会不会回 overview”，而是 `workflow` 底座项目的旧 failed 留痕会不会长期劫持默认首页。
- 当前还不能切到 `V6`。`V5-R6` 已经把恢复感知摘要推进到 `prod candidate=20260421-110802`，但还缺这拍 candidate 升上 prod 后的 live 回归，以及更细的 UCD/项目态摘要层次收口；`V6.next_activation_ready=false` 也没有变化。

## 取舍
- 我没有重复上一拍已经完成的 `project-comics-smoke -> overview` 修复；我继续沿着同一块工作面往下切，把更隐蔽、也更影响默认阅读路径的“历史失败长期抢首页”收掉了。
- 我也没有把这轮拆给 helper 并发实现。这批改动同时触达后端摘要 contract、前端侧栏短信号和 acceptance fixture，强拆只会放大前后端分叉风险；我只在收尾时把 5 个 helper developer workspace 全量 refresh 到 `867c33b`，保证下一批 live 回归和 UCD 细化随时可接。

## 下一动作
- 先等 `prod candidate=20260421-110802` 命中 idle watcher 的升级空窗。
- 升级后优先补一轮 workflow/project-ops live 回归，确认历史失败不会在无活跃任务时继续把默认首页拉回 `项目产出`。
- 这条 live 回归通过后，再继续切 `V5-R6` 的更细 UCD/摘要层次收口；等这条细化再收口一批，或 `V6` 补齐真实主题与 probe binding 之后，我再重检 `activation readiness`。

## 证据
- 发布边界：`root_sync_state=clean_synced ; ahead_count=0 ; dirty_tracked_count=0 ; untracked_count=0 ; workspace_head=code_root_head=867c33b ; push_block_reason=- ; next_push_batch=V5-R6 prod live 回归与更细 UCD 批`
- 代码收口：`.repository/pm-main=../workflow_code=867c33b`
- 验证：
  - `.repository/pm-main/.test/20260421-105650-017/report.md`
  - `.repository/pm-main/.test/20260421-105658-022/report.md`
  - `.repository/pm-main/.test/20260421-105707-295/report.md`
  - `.repository/pm-main/.test/20260421-105744-848/report.md`
  - `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260421-110111.md`
  - `.repository/pm-main/.test/runs/workflow-gate-acceptance-20260421-110622.md`
- 部署与 live：
  - `.running/control/logs/test/deploy-20260421-110802.json`
  - `/api/runtime-upgrade/status => current=20260421-103028 / candidate=20260421-110802 / candidate_is_newer=true / drain_active=true / running_task_count=1 / can_upgrade=false`
  - `state/developer-workspaces.json => pm-main + 5 helpers = clean_synced@867c33b`
- preference_ref: `state/user-preferences.md`
- delta_observation: 我这轮确认项目运营页的默认首页不能只按“当前是否存在 failed 计数”粗暴决策；当最新终态已经恢复成功且没有活跃任务时，历史失败应该降级成背景信号，而不是继续劫持默认首页。
- delta_validation: 下一轮在 `110802` 升上 prod 后，用同一条 workflow/project-ops 读面继续验证“旧 failed + 更新 succeeded + 无 active”不会再默认落到 `项目产出`。
- memory_ref: `.codex/memory/2026-04/2026-04-21.md`
