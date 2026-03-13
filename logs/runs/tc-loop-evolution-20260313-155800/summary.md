# Training Loop Evidence (20260313-155800)

- base_url: http://127.0.0.1:18090
- db_path: C:/work/J-Agents/workflow/.runtime/state/workflow.db
- server_stdout: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-155800/server_stdout.log
- server_stderr: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-155800/server_stderr.log

## API
- concurrent_agents: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-155800/api/concurrent_training_agents.json
- create_plan: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-155800/api/create_plan.json
- loop_before: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-155800/api/loop_before.json
- enter_next_round: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-155800/api/enter_next_round.json
- loop_after_enter: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-155800/api/loop_after_enter.json
- rollback_round_increment: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-155800/api/rollback_round_increment.json
- loop_after_rollback: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-155800/api/loop_after_rollback.json
- training_audit_log: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-155800/api/training_audit_log_loop_actions.json

## Screenshots

- 任务状态-三列结构与当前概览: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-155800/screenshots/01_status_overview.png
  url: http://127.0.0.1:18090/?tc_loop_mode=status&tc_loop_tab=overview&tc_loop_task=tq-20260313-155805-303477&tc_loop_node=tq-20260313-155805-303477&tc_loop_search=tc-loop-evidence+20260313-155800
- 任务状态-工作集变化页签: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-155800/screenshots/02_status_workset.png
  url: http://127.0.0.1:18090/?tc_loop_mode=status&tc_loop_tab=workset&tc_loop_task=tq-20260313-155805-303477&tc_loop_node=tq-20260313-155805-303477&tc_loop_search=tc-loop-evidence+20260313-155800
- 任务状态-历史记录页签与右侧节点详情: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-155800/screenshots/03_status_history.png
  url: http://127.0.0.1:18090/?tc_loop_mode=status&tc_loop_tab=history&tc_loop_task=tq-20260313-155805-303477&tc_loop_node=tq-20260313-155805-303477&tc_loop_search=tc-loop-evidence+20260313-155800
- 创建任务-两列结构与基础信息页签: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-155800/screenshots/04_create_basic.png
  url: http://127.0.0.1:18090/?tc_loop_mode=create&tc_loop_tab=basic
- 创建任务-启动确认页签与提交区: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-155800/screenshots/05_create_launch.png
  url: http://127.0.0.1:18090/?tc_loop_mode=create&tc_loop_tab=launch
- 创建任务-中栏滚动到底部: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-155800/screenshots/06_create_scroll_bottom.png
  url: http://127.0.0.1:18090/?tc_loop_mode=create&tc_loop_tab=launch&tc_loop_scroll=bottom
- 任务状态-中栏滚动到底部: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-155800/screenshots/07_status_scroll_bottom.png
  url: http://127.0.0.1:18090/?tc_loop_mode=status&tc_loop_tab=history&tc_loop_task=tq-20260313-155805-303477&tc_loop_node=tq-20260313-155805-303477&tc_loop_search=tc-loop-evidence+20260313-155800&tc_loop_scroll=bottom
- 进入下一轮后-演进图与队列变化: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-155800/screenshots/08_after_enter_next_round.png
  url: http://127.0.0.1:18090/?tc_loop_mode=status&tc_loop_tab=overview&tc_loop_task=tq-20260313-155909-780979&tc_loop_node=tq-20260313-155909-780979&tc_loop_search=tc-loop-evidence+20260313-155800
- 回退本轮新增后-演进图与右侧面板: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-155800/screenshots/09_after_rollback_round_increment.png
  url: http://127.0.0.1:18090/?tc_loop_mode=status&tc_loop_tab=history&tc_loop_task=tq-20260313-155909-780979&tc_loop_node=rb-tq-20260313-155909-780979&tc_loop_search=tc-loop-evidence+20260313-155800
