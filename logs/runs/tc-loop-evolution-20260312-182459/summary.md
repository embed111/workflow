# Training Loop Evidence (20260312-182459)

- base_url: http://127.0.0.1:18090
- db_path: C:/work/J-Agents/workflow/.runtime/state/workflow.db
- server_stdout: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260312-182459/server_stdout.log
- server_stderr: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260312-182459/server_stderr.log

## API
- concurrent_agents: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260312-182459/api/concurrent_training_agents.json
- create_plan: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260312-182459/api/create_plan.json
- loop_before: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260312-182459/api/loop_before.json
- enter_next_round: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260312-182459/api/enter_next_round.json
- loop_after_enter: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260312-182459/api/loop_after_enter.json
- rollback_round_increment: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260312-182459/api/rollback_round_increment.json
- loop_after_rollback: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260312-182459/api/loop_after_rollback.json
- training_audit_log: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260312-182459/api/training_audit_log_loop_actions.json

## Screenshots

- 任务状态-顶部五阶段流: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260312-182459/screenshots/01_status_steps.png
  url: http://127.0.0.1:18090/?tc_loop_mode=status&tc_loop_tab=score&tc_loop_task=tq-20260312-182503-f31acb&tc_loop_node=tq-20260312-182503-f31acb&tc_loop_search=tc-loop-evidence+20260312-182459
- 任务状态-演进图(真实数据或空态): C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260312-182459/screenshots/02_status_graph.png
  url: http://127.0.0.1:18090/?tc_loop_mode=status&tc_loop_tab=score&tc_loop_task=tq-20260312-182503-f31acb&tc_loop_node=tq-20260312-182503-f31acb&tc_loop_search=tc-loop-evidence+20260312-182459
- 任务状态-右侧当前节点详情: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260312-182459/screenshots/03_status_right_pane.png
  url: http://127.0.0.1:18090/?tc_loop_mode=status&tc_loop_tab=score&tc_loop_task=tq-20260312-182503-f31acb&tc_loop_node=tq-20260312-182503-f31acb&tc_loop_search=tc-loop-evidence+20260312-182459
- 创建任务-顶部五阶段流: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260312-182459/screenshots/04_create_steps.png
  url: http://127.0.0.1:18090/?tc_loop_mode=create
- 创建任务-训练路径预览(劣化回退/提升不足进下一轮): C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260312-182459/screenshots/05_create_path_preview.png
  url: http://127.0.0.1:18090/?tc_loop_mode=create
- 区内滚动条与底边平齐: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260312-182459/screenshots/06_scrollbars_bottom_alignment.png
  url: http://127.0.0.1:18090/?tc_loop_mode=create
- 进入下一轮后-演进图与队列变化: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260312-182459/screenshots/07_after_enter_next_round.png
  url: http://127.0.0.1:18090/?tc_loop_mode=status&tc_loop_tab=score&tc_loop_task=tq-20260312-182555-b10e07&tc_loop_node=tq-20260312-182555-b10e07&tc_loop_search=tc-loop-evidence+20260312-182459
- 回退本轮新增后-演进图与右侧面板: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260312-182459/screenshots/08_after_rollback_round_increment.png
  url: http://127.0.0.1:18090/?tc_loop_mode=status&tc_loop_tab=decision&tc_loop_task=tq-20260312-182555-b10e07&tc_loop_node=rb-tq-20260312-182555-b10e07&tc_loop_search=tc-loop-evidence+20260312-182459
