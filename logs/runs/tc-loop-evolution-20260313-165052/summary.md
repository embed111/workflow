# Training Loop Real Backend Evidence (20260313-165052)

- base_url: http://127.0.0.1:18090
- loop_id: plan-20260313-165055-ab2ffd
- queue_round1: tq-20260313-165055-454d93
- queue_round2: tq-20260313-165141-16e627
- db_path: C:/work/J-Agents/workflow/.runtime/state/workflow.db
- server_stdout: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/server_stdout.log
- server_stderr: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/server_stderr.log

## API
- concurrent_training_agents.json: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/api/concurrent_training_agents.json
- create_plan.json: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/api/create_plan.json
- enter_next_round.json: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/api/enter_next_round.json
- execute_round1.json: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/api/execute_round1.json
- execute_round2.json: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/api/execute_round2.json
- loop_after_rollback.json: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/api/loop_after_rollback.json
- loop_round1.json: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/api/loop_round1.json
- loop_round2_before_rollback.json: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/api/loop_round2_before_rollback.json
- loop_round2_queued.json: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/api/loop_round2_queued.json
- rollback_round_increment.json: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/api/rollback_round_increment.json
- status_detail_after_rollback.json: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/api/status_detail_after_rollback.json
- status_detail_round1.json: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/api/status_detail_round1.json
- status_detail_round2_before_rollback.json: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/api/status_detail_round2_before_rollback.json
- status_detail_round2_queued.json: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/api/status_detail_round2_queued.json

## DB
- training_audit_log.json: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/db/training_audit_log.json
- training_eval_run.json: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/db/training_eval_run.json
- training_loop_state.json: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/db/training_loop_state.json
- training_run.json: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/db/training_run.json

## Screenshots
- 状态页-当前概览: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/screenshots/01_status_overview_round1.png
  url: http://127.0.0.1:18090/?tc_loop_mode=status&tc_loop_tab=overview&tc_loop_task=tq-20260313-165055-454d93&tc_loop_node=tq-20260313-165055-454d93&tc_loop_search=tc-loop-real-backend+20260313-165052
- 状态页-工作集变化: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/screenshots/02_status_workset_round1.png
  url: http://127.0.0.1:18090/?tc_loop_mode=status&tc_loop_tab=workset&tc_loop_task=tq-20260313-165055-454d93&tc_loop_node=tq-20260313-165055-454d93&tc_loop_search=tc-loop-real-backend+20260313-165052
- 状态页-三轮评测: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/screenshots/03_status_eval_round1.png
  url: http://127.0.0.1:18090/?tc_loop_mode=status&tc_loop_tab=eval&tc_loop_task=tq-20260313-165055-454d93&tc_loop_node=tq-20260313-165055-454d93&tc_loop_search=tc-loop-real-backend+20260313-165052
- 状态页-历史记录: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/screenshots/04_status_history_round1.png
  url: http://127.0.0.1:18090/?tc_loop_mode=status&tc_loop_tab=history&tc_loop_task=tq-20260313-165055-454d93&tc_loop_node=tq-20260313-165055-454d93&tc_loop_search=tc-loop-real-backend+20260313-165052
- 进入下一轮前: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/screenshots/05_before_enter_next_round.png
  url: http://127.0.0.1:18090/?tc_loop_mode=status&tc_loop_tab=overview&tc_loop_task=tq-20260313-165055-454d93&tc_loop_node=tq-20260313-165055-454d93&tc_loop_search=tc-loop-real-backend+20260313-165052
- 进入下一轮后: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/screenshots/06_after_enter_next_round.png
  url: http://127.0.0.1:18090/?tc_loop_mode=status&tc_loop_tab=overview&tc_loop_task=tq-20260313-165141-16e627&tc_loop_node=tq-20260313-165141-16e627&tc_loop_search=tc-loop-real-backend+20260313-165052
- 回退本轮新增前: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/screenshots/07_before_rollback_round_increment.png
  url: http://127.0.0.1:18090/?tc_loop_mode=status&tc_loop_tab=eval&tc_loop_task=tq-20260313-165141-16e627&tc_loop_node=tq-20260313-165141-16e627&tc_loop_search=tc-loop-real-backend+20260313-165052
- 回退本轮新增后: C:/work/J-Agents/workflow/logs/runs/tc-loop-evolution-20260313-165052/screenshots/08_after_rollback_round_increment.png
  url: http://127.0.0.1:18090/?tc_loop_mode=status&tc_loop_tab=history&tc_loop_task=tq-20260313-165141-16e627&tc_loop_node=rb-tq-20260313-165141-16e627&tc_loop_search=tc-loop-real-backend+20260313-165052
