# runtime read model fast path - 2026-04-26 14:06

- preference_ref: state/user-preferences.md
- delta_observation: 用户明确要求页面恢复卡顿与大粒度锁问题不仅要修，还要补用例并优化读写性能。
- delta_validation: 后续遇到页面恢复慢，先分层点测 `healthz/projects/status/graph/status-detail`，再确认读模型是否仍有写回副作用。

## 结论
- 已在 `.repository/pm-main` 修复 assignment graph/status-detail/overview/scheduler 的页面读路径：不再在页面读面执行 stale recovery、持 ticket mutation lock 或做全量 interface catalog backfill。
- 已限制 status-detail 的大文件读取：events 只读尾部 256KB，prompt/stdout/stderr/result 预览按字节上限读取。
- 已让前端启动恢复的 dashboard refresh 走 3.5s soft timeout，避免“正在恢复数据”把整页卡死。
- 已修复 prod idle watcher：`prod-idle-upgrade-watchdog` 发起 apply 后立即交还 supervisor，不再同步等 8090 恢复。

## 验证
- 新增用例：`scripts/acceptance/verify_assignment_read_model_fast_path.py`
- 完整 gate：`.repository/pm-main/.test/runs/workflow-gate-acceptance-20260426-135928.md`
- line budget：`.repository/pm-main/.test/20260426-135102-607/report.md`
- test 部署：`.running/control/logs/test/deploy-20260426-140042.json`
- prod candidate：`.running/control/prod-candidate.json` -> `20260426-140042`

## 发布边界
- 代码已提交并同步到本机 `workflow_code/main`：`fe5cc87 fix(runtime): 缩短升级 watcher 等待并加快任务读面`
- `test=20260426-140042` 已通过 gate。
- `prod current=20260426-120441`，`candidate=20260426-140042`，当前 `running_task_count=1`，所以未直接 apply prod。
