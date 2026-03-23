  function scheduleStatusChipHtml(status, text, extraClass) {
    const tone = extraClass || scheduleResultTone(status);
    return "<span class='schedule-status-chip " + escapeHtml(tone) + "'>" + escapeHtml(text || '-') + '</span>';
  }

  function schedulePlanCardHtml(item, isActive) {
    const labels = Array.isArray(item && item.rule_labels) ? item.rule_labels : [];
    const tone = !!(item && item.enabled) ? safe(item && item.last_result_status).trim().toLowerCase() || 'pending' : 'disabled';
    const text = !!(item && item.enabled)
      ? (safe(item && item.last_result_status_text).trim() || '待触发')
      : '已停用';
    return (
      "<button class='schedule-plan-item" + (isActive ? " active" : '') + "' type='button' data-schedule-select='" + escapeHtml(safe(item && item.schedule_id).trim()) + "'>" +
        "<div class='schedule-plan-title'>" + escapeHtml(safe(item && item.schedule_name).trim() || '-') + '</div>' +
        "<div class='schedule-plan-desc'>" + escapeHtml(safe(item && item.launch_summary).trim() || '-') + '</div>' +
        "<div class='schedule-plan-rules'>" +
          labels.map((label) => "<span class='schedule-rule-chip'>" + escapeHtml(label) + "</span>").join('') +
        '</div>' +
        "<div class='schedule-plan-meta'>" +
          "<div><div class='schedule-plan-sub'>下一次触发</div><div class='schedule-plan-sub'>" + escapeHtml(safe(item && item.next_trigger_text).trim() || '-') + '</div></div>' +
          "<div><div class='schedule-plan-sub'>最近结果</div><div>" + scheduleStatusChipHtml(tone, text, tone) + '</div></div>' +
        '</div>' +
      '</button>'
    );
  }

  function scheduleStatHtml(label, value) {
    return (
      "<div class='schedule-stat'>" +
        "<div class='schedule-stat-k'>" + escapeHtml(label) + '</div>' +
        "<div class='schedule-stat-v'>" + escapeHtml(safe(value).trim() || '-') + '</div>' +
      '</div>'
    );
  }

  function scheduleHistoryItemHtml(item) {
    const openBtn = safe(item && item.assignment_ticket_id).trim() && safe(item && item.assignment_node_id).trim()
      ? "<button class='alt schedule-jump-btn' type='button' data-open-task-center='1' data-ticket-id='" + escapeHtml(safe(item.assignment_ticket_id).trim()) + "' data-node-id='" + escapeHtml(safe(item.assignment_node_id).trim()) + "'>去任务中心查看</button>"
      : '';
    return (
      "<div class='schedule-list-item'>" +
        "<div class='schedule-list-item-head'>" +
          "<div>" +
            "<div class='schedule-plan-title'>" + escapeHtml(scheduleFormatBeijingTime(item && item.planned_trigger_at)) + '</div>' +
            "<div class='schedule-plan-sub'>" + escapeHtml(safe(item && item.trigger_rule_summary).trim() || '-') + '</div>' +
          '</div>' +
          scheduleStatusChipHtml(safe(item && item.result_status).trim(), safe(item && item.result_status_text).trim() || '-', '') +
        '</div>' +
        "<div class='schedule-plan-sub'>" + escapeHtml(safe(item && item.trigger_message).trim() || safe(item && item.assignment_status_text).trim() || '-') + '</div>' +
        (openBtn ? "<div class='schedule-actions'>" + openBtn + '</div>' : '') +
      '</div>'
    );
  }

  function renderScheduleDetailBody() {
    const body = $('scheduleDetailBody');
    const meta = $('scheduleDetailMeta');
    if (!body) return;
    const detail = state.scheduleDetail && typeof state.scheduleDetail === 'object' ? state.scheduleDetail : {};
    const schedule = detail.schedule && typeof detail.schedule === 'object' ? detail.schedule : selectedSchedulePlan();
    if (!schedule || !safe(schedule.schedule_id).trim()) {
      if (meta) meta.textContent = '请选择定时计划';
      body.innerHTML = "<div class='schedule-empty'><div class='schedule-plan-title'>暂无计划详情</div><div class='schedule-plan-sub'>从左侧选择计划后，在这里查看规则、未来触发、最近结果和关联任务中心实例。</div></div>";
      return;
    }
    if (meta) meta.textContent = 'source_schedule_id: ' + safe(schedule.schedule_id).trim();
    const future = Array.isArray(detail.future_triggers) ? detail.future_triggers : [];
    const recent = Array.isArray(detail.recent_triggers) ? detail.recent_triggers : [];
    const related = Array.isArray(detail.related_task_refs) ? detail.related_task_refs : [];
    const enabled = !!schedule.enabled;
    body.innerHTML =
      "<section class='schedule-hero'>" +
        "<div class='schedule-hero-head'>" +
          "<div>" +
            "<div class='schedule-plan-title'>" + escapeHtml(safe(schedule.schedule_name).trim()) + '</div>' +
            "<div class='schedule-plan-sub'>" + escapeHtml(safe(schedule.launch_summary).trim() || '-') + '</div>' +
          '</div>' +
          scheduleStatusChipHtml(enabled ? safe(schedule.last_result_status).trim() : 'disabled', enabled ? (safe(schedule.last_result_status_text).trim() || '待触发') : '已停用', enabled ? '' : 'disabled') +
        '</div>' +
        "<div class='schedule-actions'>" +
          "<button class='alt' type='button' data-schedule-action='edit' data-schedule-id='" + escapeHtml(safe(schedule.schedule_id).trim()) + "'>编辑计划</button>" +
          "<button class='alt' type='button' data-schedule-action='" + (enabled ? 'disable' : 'enable') + "' data-schedule-id='" + escapeHtml(safe(schedule.schedule_id).trim()) + "'>" + (enabled ? '停用计划' : '启用计划') + "</button>" +
          "<button class='bad' type='button' data-schedule-action='delete' data-schedule-id='" + escapeHtml(safe(schedule.schedule_id).trim()) + "'>删除计划</button>" +
        '</div>' +
        "<div class='schedule-hero-grid'>" +
          scheduleStatHtml('执行 Agent', safe(schedule.assigned_agent_name).trim() || safe(schedule.assigned_agent_id).trim()) +
          scheduleStatHtml('优先级', safe(schedule.priority).trim()) +
          scheduleStatHtml('下一次触发', safe(schedule.next_trigger_text).trim()) +
          scheduleStatHtml('最近一次触发', safe(schedule.last_trigger_at).trim() ? scheduleFormatBeijingTime(schedule.last_trigger_at) : '-') +
        '</div>' +
      '</section>' +
      "<section class='schedule-section'>" +
        "<div class='schedule-section-head'><div class='card-title'>发起任务内容预览</div></div>" +
        "<div class='schedule-section-grid'>" +
          scheduleStatHtml('本次目标', safe(schedule.launch_summary).trim()) +
          scheduleStatHtml('预期产物', safe(schedule.expected_artifact).trim() || '-') +
          scheduleStatHtml('执行清单', safe(schedule.execution_checklist).trim()) +
          scheduleStatHtml('完成标准', safe(schedule.done_definition).trim()) +
        '</div>' +
      '</section>' +
      "<section class='schedule-section'><div class='card-title'>触发规则</div><div class='schedule-plan-rules'>" +
        (Array.isArray(schedule.rule_labels) && schedule.rule_labels.length
          ? schedule.rule_labels.map((label) => "<span class='schedule-rule-chip'>" + escapeHtml(label) + "</span>").join('')
          : "<span class='schedule-plan-sub'>暂无规则</span>") +
      '</div></section>' +
      "<section class='schedule-section'><div class='card-title'>未来触发</div><div class='schedule-list'>" +
        (future.length
          ? future.map((item) => "<div class='schedule-list-item'><div class='schedule-plan-title'>" + escapeHtml(scheduleFormatBeijingTime(item.planned_trigger_at)) + "</div><div class='schedule-plan-sub'>" + escapeHtml(safe(item.trigger_rule_summary).trim() || '-') + "</div></div>").join('')
          : "<div class='schedule-empty'><div class='schedule-plan-sub'>暂无未来触发</div></div>") +
      '</div></section>' +
      "<section class='schedule-section'><div class='card-title'>最近执行结果</div><div class='schedule-list'>" +
        (recent.length ? recent.map(scheduleHistoryItemHtml).join('') : "<div class='schedule-empty'><div class='schedule-plan-sub'>暂无执行记录</div></div>") +
      '</div></section>' +
      "<section class='schedule-section'><div class='card-title'>关联任务中心实例</div><div class='schedule-list'>" +
        (related.length
          ? related.map((item) => "<div class='schedule-list-item'><div class='schedule-list-item-head'><div><div class='schedule-plan-title'>" + escapeHtml(safe(item.assignment_node_name).trim() || safe(item.assignment_node_id).trim()) + "</div><div class='schedule-plan-sub'>" + escapeHtml(scheduleFormatBeijingTime(item.planned_trigger_at)) + "</div></div>" + scheduleStatusChipHtml(safe(item.result_status).trim(), safe(item.result_status_text).trim() || '-', '') + "</div><div class='schedule-actions'><button class='alt schedule-jump-btn' type='button' data-open-task-center='1' data-ticket-id='" + escapeHtml(safe(item.assignment_ticket_id).trim()) + "' data-node-id='" + escapeHtml(safe(item.assignment_node_id).trim()) + "'>去任务中心查看</button></div></div>").join('')
          : "<div class='schedule-empty'><div class='schedule-plan-sub'>暂无关联实例</div></div>") +
      '</div></section>';
  }

  function renderScheduleCalendarGrid() {
    const grid = $('scheduleCalendarGrid');
    const label = $('scheduleCalendarMonthLabel');
    if (!grid) return;
    const calendarData = state.scheduleCalendar && typeof state.scheduleCalendar === 'object' ? state.scheduleCalendar : {};
    if (label) label.textContent = safe(calendarData.month_title).trim() || '-';
    const days = Array.isArray(calendarData.days) ? calendarData.days : [];
    grid.innerHTML = [
      "<div class='schedule-weekday'>周一</div>",
      "<div class='schedule-weekday'>周二</div>",
      "<div class='schedule-weekday'>周三</div>",
      "<div class='schedule-weekday'>周四</div>",
      "<div class='schedule-weekday'>周五</div>",
      "<div class='schedule-weekday'>周六</div>",
      "<div class='schedule-weekday'>周日</div>",
      days.map((day) => {
        const classes = ['schedule-day'];
        if (!day.is_current_month) classes.push('is-muted');
        if (day.is_today) classes.push('is-today');
        if (safe(day.date).trim() === safe(state.scheduleCalendarSelectedDate).trim()) classes.push('is-selected');
        const planEvents = (Array.isArray(day.plans) ? day.plans : []).slice(0, 2).map((item) => "<div class='schedule-day-event plan'>" + escapeHtml(safe(item.planned_trigger_at).trim().slice(11, 16) + ' ' + safe(item.schedule_name).trim()) + '</div>').join('');
        const resultEvents = (Array.isArray(day.results) ? day.results : []).slice(0, 2).map((item) => "<div class='schedule-day-event " + escapeHtml(scheduleResultTone(item.result_status)) + "'>" + escapeHtml(safe(item.planned_trigger_at).trim().slice(11, 16) + ' ' + safe(item.schedule_name_snapshot || item.assignment_node_name || item.schedule_id).trim()) + '</div>').join('');
        return "<button class='" + classes.join(' ') + "' type='button' data-schedule-day='" + escapeHtml(safe(day.date).trim()) + "'><div class='schedule-day-num'>" + escapeHtml(String(day.day || '')) + "</div><div class='schedule-day-events'>" + planEvents + resultEvents + "</div></button>";
      }).join('')
    ].join('');
  }

  function renderScheduleCalendarDetail() {
    const body = $('scheduleCalendarDetailBody');
    const meta = $('scheduleCalendarDetailMeta');
    if (!body) return;
    const day = scheduleSelectedCalendarDay();
    if (!day) {
      if (meta) meta.textContent = '请选择日期';
      body.innerHTML = "<div class='schedule-empty'><div class='schedule-plan-sub'>暂无日历数据</div></div>";
      return;
    }
    if (meta) meta.textContent = safe(day.date).trim();
    const plans = Array.isArray(day.plans) ? day.plans : [];
    const results = Array.isArray(day.results) ? day.results : [];
    body.innerHTML =
      "<section class='schedule-section'>" +
        "<div class='schedule-calendar-day-head'><div><div class='schedule-plan-title'>" + escapeHtml(safe(day.date).trim()) + "</div><div class='schedule-plan-sub'>选中日可直接查看将要发起的任务摘要和已触发实例结果。</div></div></div>" +
      '</section>' +
      "<section class='schedule-section'><div class='card-title'>当日计划</div><div class='schedule-list'>" +
        (plans.length
          ? plans.map((item) => "<div class='schedule-list-item'><div class='schedule-list-item-head'><div><div class='schedule-plan-title'>" + escapeHtml(safe(item.schedule_name).trim()) + "</div><div class='schedule-plan-sub'>" + escapeHtml(scheduleFormatBeijingTime(item.planned_trigger_at)) + "</div></div><button class='alt schedule-jump-btn' type='button' data-schedule-action='edit' data-schedule-id='" + escapeHtml(safe(item.schedule_id).trim()) + "'>编辑计划</button></div><div class='schedule-plan-sub'>" + escapeHtml(safe(item.trigger_rule_summary).trim()) + "</div></div>").join('')
          : "<div class='schedule-empty'><div class='schedule-plan-sub'>当日暂无未来计划</div></div>") +
      '</div></section>' +
      "<section class='schedule-section'><div class='card-title'>实际结果</div><div class='schedule-list'>" +
        (results.length
          ? results.map((item) => "<div class='schedule-list-item'><div class='schedule-list-item-head'><div><div class='schedule-plan-title'>" + escapeHtml(safe(item.schedule_name_snapshot).trim() || safe(item.assignment_node_name).trim()) + "</div><div class='schedule-plan-sub'>" + escapeHtml(scheduleFormatBeijingTime(item.planned_trigger_at)) + "</div></div>" + scheduleStatusChipHtml(safe(item.result_status).trim(), safe(item.result_status_text).trim() || '-', '') + "</div><div class='schedule-plan-sub'>" + escapeHtml(safe(item.launch_summary_snapshot).trim() || safe(item.trigger_message).trim() || '-') + "</div><div class='schedule-actions'>" + (safe(item.assignment_ticket_id).trim() && safe(item.assignment_node_id).trim() ? "<button class='alt schedule-jump-btn' type='button' data-open-task-center='1' data-ticket-id='" + escapeHtml(safe(item.assignment_ticket_id).trim()) + "' data-node-id='" + escapeHtml(safe(item.assignment_node_id).trim()) + "'>去任务中心查看</button>" : '') + (safe(item.schedule_id).trim() ? "<button class='alt schedule-jump-btn' type='button' data-schedule-action='edit' data-schedule-id='" + escapeHtml(safe(item.schedule_id).trim()) + "'>编辑计划</button>" : '') + "</div></div>").join('')
          : "<div class='schedule-empty'><div class='schedule-plan-sub'>当日暂无执行结果</div></div>") +
      '</div></section>';
  }

  function populateScheduleEditor() {
    const schedule = state.scheduleEditorMode === 'edit' ? selectedScheduleDetail() : {};
    const inputs = schedule.editor_rule_inputs || { monthly: {}, weekly: {}, daily: {}, once: {} };
    $('scheduleEditorTitle').textContent = state.scheduleEditorMode === 'edit' ? '编辑定时任务' : '新建定时任务';
    $('scheduleEditorNameInput').value = safe(schedule.schedule_name).trim();
    $('scheduleEditorPrioritySelect').value = safe(schedule.priority).trim() || 'P1';
    $('scheduleEditorLaunchSummaryInput').value = safe(schedule.launch_summary).trim();
    $('scheduleEditorChecklistInput').value = safe(schedule.execution_checklist).trim();
    $('scheduleEditorDoneDefinitionInput').value = safe(schedule.done_definition).trim();
    $('scheduleEditorArtifactInput').value = safe(schedule.expected_artifact).trim();
    $('scheduleEditorDeliveryModeSelect').value = safe(schedule.delivery_mode).trim() || 'none';
    $('scheduleEditorEnabledCheck').checked = state.scheduleEditorMode === 'edit' ? !!schedule.enabled : true;
    $('scheduleRuleMonthlyEnabled').checked = !!inputs.monthly.enabled;
    $('scheduleRuleMonthlyDays').value = safe(inputs.monthly.days_text).trim();
    $('scheduleRuleMonthlyTimes').value = safe(inputs.monthly.times_text).trim();
    $('scheduleRuleWeeklyEnabled').checked = !!inputs.weekly.enabled;
    $('scheduleRuleWeeklyTimes').value = safe(inputs.weekly.times_text).trim();
    document.querySelectorAll('[data-schedule-weekday]').forEach((node) => {
      node.checked = Array.isArray(inputs.weekly.weekdays) && inputs.weekly.weekdays.includes(Number(node.getAttribute('data-schedule-weekday')));
    });
    $('scheduleRuleDailyEnabled').checked = !!inputs.daily.enabled;
    $('scheduleRuleDailyTimes').value = safe(inputs.daily.times_text).trim();
    $('scheduleRuleOnceEnabled').checked = !!inputs.once.enabled;
    $('scheduleRuleOnceDates').value = safe(inputs.once.date_times_text).trim();
    const agentSelect = $('scheduleEditorAgentSelect');
    const deliverySelect = $('scheduleEditorDeliveryReceiverSelect');
    const options = Array.isArray(state.agents) ? state.agents : [];
    const currentAgent = safe(schedule.assigned_agent_id).trim() || safe(schedule.assigned_agent_name).trim();
    const currentReceiver = safe(schedule.delivery_receiver_agent_id).trim() || safe(schedule.delivery_receiver_agent_name).trim();
    const rendered = ["<option value=''>请选择执行 agent</option>"].concat(options.map((item) => "<option value='" + escapeHtml(safe(item && item.agent_id).trim() || safe(item && item.agent_name).trim()) + "'>" + escapeHtml(safe(item && item.agent_name).trim() || safe(item && item.agent_id).trim()) + "</option>"));
    if (agentSelect) {
      agentSelect.innerHTML = rendered.join('');
      agentSelect.value = currentAgent;
    }
    if (deliverySelect) {
      deliverySelect.innerHTML = ["<option value=''>默认交付给当前 agent</option>"].concat(rendered.slice(1)).join('');
      deliverySelect.value = currentReceiver;
    }
    if (typeof scheduleApplyEditorDeliveryModeState === 'function') {
      scheduleApplyEditorDeliveryModeState();
    }
    setScheduleEditorError(state.scheduleEditorError);
  }

  function renderScheduleCenter() {
    const errorNode = $('scheduleError');
    if (errorNode) errorNode.textContent = state.scheduleError || '';
    const listBtn = $('scheduleViewListBtn');
    const calendarBtn = $('scheduleViewCalendarBtn');
    const listView = $('scheduleListView');
    const calendarView = $('scheduleCalendarView');
    if (listBtn) listBtn.classList.toggle('active', state.scheduleView !== 'calendar');
    if (calendarBtn) calendarBtn.classList.toggle('active', state.scheduleView === 'calendar');
    if (listView) listView.classList.toggle('active', state.scheduleView !== 'calendar');
    if (calendarView) calendarView.classList.toggle('active', state.scheduleView === 'calendar');
    const meta = $('scheduleMeta');
    if (meta) {
      if (!state.agentSearchRootReady) {
        meta.textContent = 'agent路径未设置或无效，定时任务模块已锁定。';
      } else if (state.scheduleLoading) {
        meta.textContent = '计划加载中...';
      } else {
        meta.textContent = '共 ' + String(Array.isArray(state.schedulePlans) ? state.schedulePlans.length : 0) + ' 条计划';
      }
    }
    const list = $('schedulePlanList');
    const count = $('schedulePlanCountChip');
    if (count) count.textContent = String(Array.isArray(state.schedulePlans) ? state.schedulePlans.length : 0) + ' 条计划';
    if (list) {
      if (!state.agentSearchRootReady) {
        list.innerHTML = "<div class='schedule-empty'><div class='schedule-plan-title'>功能已锁定</div><div class='schedule-plan-sub'>请先在设置页配置有效的 agent 路径。</div></div>";
      } else if (!Array.isArray(state.schedulePlans) || !state.schedulePlans.length) {
        list.innerHTML = "<div class='schedule-empty'><div class='schedule-plan-title'>暂无定时计划</div><div class='schedule-plan-sub'>从右上角 + 开始新建，保存后可真实命中并向任务中心建单。</div></div>";
      } else {
        list.innerHTML = state.schedulePlans.map((item) => schedulePlanCardHtml(item, safe(item && item.schedule_id).trim() === safe(state.scheduleSelectedId).trim())).join('');
      }
    }
    renderScheduleDetailBody();
    renderScheduleCalendarGrid();
    renderScheduleCalendarDetail();
    const mask = $('scheduleEditorMask');
    if (mask) {
      mask.classList.toggle('hidden', !state.scheduleEditorOpen);
    }
    if (state.scheduleEditorOpen) {
      populateScheduleEditor();
    }
  }
