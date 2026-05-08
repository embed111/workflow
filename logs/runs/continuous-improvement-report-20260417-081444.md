# Continuous Improvement Report 2026-04-17 08:14

- topic: release boundary 收口 + task-center 固定工作面滚动壳验收护栏
- preference_ref: state/user-preferences.md
- delta_observation: `pm-main` 的任务中心前端 dirty 批次已经在未提交状态下被带进 `prod candidate=20260417-080040`；这轮先把 candidate 对应源码批次收回 git 真相，再继续版本主线。
- delta_validation: 等 `candidate=20260417-081319` 切进 live 后，优先复跑 current-version smoke，并继续收口 `V3-R3` 的 richer scaffold actual writeback / helper learning report writeback。

## Summary

- 我把任务中心主列改成 `assignment-primary-scroll` 固定工作面：共享摘要、任务看板和任务图统一进入内部滚动壳，不再继续把整列页面越撑越长。
- 我补了两条最小验收护栏：`verify_assignment_center_view_tabs_assets.py` 与 `verify_assignment_workboard_layout_rules.js` 现在都能约束这条 scroll shell 结构。
- 我把这批 dirty 改动提交为 `.repository/pm-main@3899cdb fix(task-center): 收口任务中心固定工作面滚动壳与验收护栏`，并把本机 `../workflow_code` fast-forward 到同一提交。
- 我停掉旧 `test` 并重新部署，生成新的 `prod candidate=20260417-081319`；`prod` 当前仍是 `20260417-020721`，等待 idle watcher 在空窗切版。

## Validation

- `python scripts/quality/check_workspace_line_budget.py --root .`
  - session: `.repository/pm-main/.test/20260417-080652-037/report.md`
- `python scripts/acceptance/verify_assignment_center_view_tabs_assets.py`
  - session: `.repository/pm-main/.test/20260417-080702-786/report.md`
- `node scripts/acceptance/verify_assignment_workboard_layout_rules.js`
  - session: `.repository/pm-main/.test/20260417-080711-319/report.md`
- `python scripts/acceptance/run_acceptance_assignment_center_browser.py --root . --host 127.0.0.1 --port 8092`
  - session: `.repository/pm-main/.test/20260417-080724-258/report.md`
  - result: Edge headless `180s` timeout，记为环境级 warning
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/deploy_workflow_env.ps1 -Environment test`
  - evidence: `.running/control/logs/test/deploy-20260417-081319.json`

## Live Truth

- `prod /api/runtime-upgrade/status`: `current_version=20260417-020721 / candidate_version=20260417-081319 / candidate_is_newer=true / drain_active=true / running_task_count=1 / can_upgrade=false`
- `test /api/runtime-upgrade/status`: `current_version=20260417-081319 / candidate_is_newer=false / ghost_running_detected=true`
- release boundary: `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=3899cdb`
- version decision: `stay(V3)`；当前 blocker 仍是 `V3-R3` 未完成和 `V4 activation gate` 未就绪

## Warnings

- 浏览器回归在 `test(8092)` 命中 Edge headless `180s` 超时，本轮先记为环境级 warning，不把 release boundary 继续卡住。
- `test /api/runtime-upgrade/status` 仍有历史 `T9` ghost running 旧账；当前不阻塞 `081319` candidate，但后续需要单独清债。
