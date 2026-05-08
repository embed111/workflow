# Continuous Improvement Report

## 判断
- `version_transition_decision=stay(V5)`。当前更高价值的仍是 `V5-R5 / 工程质量探测 / 发布边界收口`，不该回去重复上一轮的 `prod/live member-route` 负向试探。

## 本轮推进
- 我把 `workflow_env_common.ps1` 里的 JSON/路径基础函数抽成了新 helper `scripts/workflow_env_json_and_paths.ps1`，让 `workflow_env_common.ps1` 只保留环境编排与部署动作。
- 我补了 `scripts/acceptance/verify_workflow_env_common_split.py`，先把旧结构跑成红灯，再和 `verify_powershell_script_parse.py` 一起把拆分后的结构锁住。
- 最新 `line budget` 仍然 fail-closed，但 `workflow_env_common.ps1` 已从 `2222` 行降到 `1808` 行，并退出 `first_batch_targets`；当前首批冻结对象已切到 `assignment_center_render_runtime.js / index_training_loop_panels.css / schedule_service.py`。

## 取舍
- 我没有重复上一轮的 supported live API probe，因为当前 prod baseline 还没进入新 candidate；继续试只会重复负向证据，不会让版本前进。
- 我先把这批已验证代码提交成 `a504d46 refactor(env): 抽离 workflow_env JSON 与路径基础 helper`，再用受支持的 `fetch + ff-only merge` 把 `../workflow_code` 追平到同一提交。直接 `git push origin main` 被本机根仓 `updateInstead` 返回的 `Working directory has unstaged changes` 拒绝，但根仓同步已经完成，不再把它留成 blocker。

## 下一动作
- 下一刀优先在 `assignment_center_render_runtime.js / index_training_loop_panels.css / schedule_service.py` 里选可独立验证的切片，继续压 `V5-R5`。
- 等 `line budget / workflow gate` 转绿后，我再部署 `test`、刷新 `prod candidate`，然后重跑同一条 supported live member-route proof。

## 证据
- `root_sync_state=clean_synced / ahead_count=0 / dirty_tracked_count=0 / untracked_count=0 / workspace_head=code_root_head=a504d46`
- 验证：
  - `.repository/pm-main/.test/20260420-004616-827/report.md`
  - `.repository/pm-main/.test/20260420-005130-947/report.md`
  - `.repository/pm-main/.test/20260420-005140-853/report.md`
  - `.repository/pm-main/.test/reports/WORKSPACE_LINE_BUDGET_REPORT.json`
- `memory_ref=.codex/memory/2026-04/2026-04-20.md`

- preference_ref: state/user-preferences.md
- delta_observation: 我这轮对工程门禁的推进继续有效，但当前更值钱的是“把首批冻结对象逐个挪出第一梯队”，而不是重复现网负向 probe。
- delta_validation: 下一轮优先在 `assignment_center_render_runtime.js / index_training_loop_panels.css / schedule_service.py` 中选一刀继续压 line budget，并在 gate 转绿后再回到 prod/live member-route 正向证据。
