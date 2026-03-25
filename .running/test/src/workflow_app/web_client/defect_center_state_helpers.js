  function defectStatusText(value) {
    const key = safe(value).trim().toLowerCase();
    if (key === 'unresolved') return '未解决';
    if (key === 'resolved') return '已解决';
    if (key === 'closed') return '已关闭';
    if (key === 'dispute') return '有分歧';
    return '当前不构成缺陷';
  }

  function defectStatusTone(value) {
    const key = safe(value).trim().toLowerCase();
    if (key === 'resolved' || key === 'closed') return 'ok';
    if (key === 'dispute') return 'dispute';
    if (key === 'not_formal') return 'returned';
    if (key === 'unresolved') return 'active';
    return 'muted';
  }

  function defectCurrentDetail() {
    return state.defectDetail && typeof state.defectDetail === 'object'
      ? state.defectDetail
      : {};
  }

  function defectCurrentReport() {
    const detail = defectCurrentDetail();
    return detail.report && typeof detail.report === 'object' ? detail.report : {};
  }

  function defectSelectedReportId() {
    return safe(state.defectSelectedReportId).trim();
  }

  function normalizeDefectListItem(item) {
    const row = item && typeof item === 'object' ? item : {};
    return {
      report_id: safe(row.report_id).trim(),
      dts_id: safe(row.dts_id).trim(),
      display_id: safe(row.display_id || row.dts_id || row.report_id).trim(),
      defect_summary: safe(row.defect_summary),
      status: safe(row.status).trim().toLowerCase() || 'not_formal',
      status_text: safe(row.status_text) || defectStatusText(row.status),
      discovered_iteration: safe(row.discovered_iteration),
      resolved_version: safe(row.resolved_version),
      decision_title: safe(row.decision_title),
      decision_summary: safe(row.decision_summary),
      decision_source: safe(row.decision_source),
      created_at: safe(row.created_at),
      updated_at: safe(row.updated_at),
      is_formal: !!row.is_formal,
      is_test_data: !!row.is_test_data,
    };
  }

  function setDefectError(text) {
    state.defectError = safe(text);
    const node = $('defectError');
    if (node) node.textContent = state.defectError;
  }

  function setDefectSubmitError(text) {
    state.defectSubmitError = safe(text);
    const node = $('defectSubmitError');
    if (node) node.textContent = state.defectSubmitError;
  }

  function setRequirementBugModule(moduleName, options) {
    const next = normalizeRequirementBugModule(moduleName);
    const opts = options && typeof options === 'object' ? options : {};
    state.requirementBugModule = next;
    const requirementBtn = $('rbTabRequirementBtn');
    const defectBtn = $('rbTabDefectBtn');
    const requirementPane = $('rbModuleRequirement');
    const defectPane = $('rbModuleDefect');
    if (requirementBtn) requirementBtn.classList.toggle('active', next === 'requirement');
    if (defectBtn) defectBtn.classList.toggle('active', next === 'defect');
    if (requirementPane) requirementPane.classList.toggle('active', next === 'requirement');
    if (defectPane) defectPane.classList.toggle('active', next === 'defect');
    if (opts.persist !== false) {
      writeSavedRequirementBugModule(next);
    }
  }

  function defectApiUrl(path, params) {
    const text = safe(path).trim() || '/api/defects';
    const items = params && typeof params === 'object' ? params : {};
    const pairs = [];
    Object.keys(items).forEach((key) => {
      const value = items[key];
      if (value === undefined || value === null || safe(value).trim() === '') return;
      pairs.push(encodeURIComponent(key) + '=' + encodeURIComponent(String(value)));
    });
    const full = pairs.length ? text + (text.includes('?') ? '&' : '?') + pairs.join('&') : text;
    return withTestDataQuery(full);
  }

  function defectImageThumbHtml(image, removeAction, buttonLabel) {
    const item = image && typeof image === 'object' ? image : {};
    const removeFn = safe(removeAction).trim();
    const actionLabel = safe(buttonLabel).trim() || '移除';
    return (
      "<div class='defect-image-chip'>" +
        "<img class='defect-image-chip-thumb' src='" + escapeHtml(safe(item.url)) + "' alt='证据图片' />" +
        "<div class='defect-image-chip-meta'>" +
          "<div class='defect-image-chip-name'>" + escapeHtml(safe(item.name) || '图片证据') + '</div>' +
          (removeFn
            ? "<button class='alt defect-image-chip-remove' type='button' data-remove-action='" + escapeHtml(removeFn) + "' data-image-id='" + escapeHtml(safe(item.image_id)) + "'>" + escapeHtml(actionLabel) + '</button>'
            : '') +
        '</div>' +
      '</div>'
    );
  }

  function renderDefectDraftImages(containerId, items, removeAction) {
    const node = $(containerId);
    if (!node) return;
    const rows = Array.isArray(items) ? items : [];
    if (!rows.length) {
      node.innerHTML = "<div class='hint'>暂未添加图片证据，可在说明框中直接粘贴截图</div>";
      return;
    }
    node.innerHTML = rows.map((item) => defectImageThumbHtml(item, removeAction, '移除')).join('');
  }

  function defectTaskRefOpenButton(ref) {
    const row = ref && typeof ref === 'object' ? ref : {};
    const ticketId = safe(row.ticket_id).trim();
    if (!ticketId) return '';
    return (
      "<button class='alt defect-open-task-btn' type='button' data-ticket-id='" + escapeHtml(ticketId) +
      "' data-node-id='" + escapeHtml(safe(row.focus_node_id).trim()) + "'>打开任务中心</button>"
    );
  }

  function defectOpenTaskCenter(ticketId, nodeId) {
    const ticket = safe(ticketId).trim();
    const focusNodeId = safe(nodeId).trim();
    if (!ticket) return;
    state.assignmentSelectedTicketId = ticket;
    state.assignmentSelectedNodeId = focusNodeId;
    switchTab('task-center');
    refreshAssignmentGraphData({ ticketId: ticket })
      .then(() => {
        if (focusNodeId) {
          return refreshAssignmentDetail(focusNodeId);
        }
        return null;
      })
      .catch((err) => {
        setAssignmentError(err.message || String(err));
      });
  }

  function defectReadFileAsDataUrl(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(safe(reader.result));
      reader.onerror = () => reject(new Error('图片读取失败'));
      reader.readAsDataURL(file);
    });
  }

  function defectRequirementEmptyHtml() {
    return (
      "<div class='defect-empty-card'>" +
        "<div class='defect-empty-title'>需求视图暂未开放</div>" +
        "<div class='hint'>当前轮只正式承接缺陷闭环，需求入口先保留为空态占位。</div>" +
      '</div>'
    );
  }
