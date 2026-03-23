  function defectFormatMetaLine(label, value) {
    return (
      "<div class='defect-meta-item'>" +
        "<div class='defect-meta-key'>" + escapeHtml(label) + '</div>' +
        "<div class='defect-meta-value'>" + escapeHtml(safe(value).trim() || '-') + '</div>' +
      '</div>'
    );
  }

  function defectHistoryHtml(items) {
    const rows = Array.isArray(items) ? items : [];
    if (!rows.length) {
      return "<div class='hint'>暂无状态与补充历史</div>";
    }
    return rows.map((item) => {
      const detail = item && item.detail && typeof item.detail === 'object' ? item.detail : {};
      let body = '';
      if (safe(detail.text).trim()) {
        body += "<div class='defect-history-text'>" + escapeHtml(safe(detail.text)) + '</div>';
      }
      if (Array.isArray(detail.images) && detail.images.length) {
        body += "<div class='defect-history-images'>" +
          detail.images.map((image) => "<img class='defect-history-thumb' src='" + escapeHtml(safe(image && image.url)) + "' alt='补充图片' />").join('') +
          '</div>';
      }
      if (!body && Object.keys(detail).length) {
        body = "<pre class='pre defect-history-pre'>" + escapeHtml(JSON.stringify(detail, null, 2)) + '</pre>';
      }
      return (
        "<div class='defect-history-item'>" +
          "<div class='defect-history-head'>" +
            "<div class='defect-history-title'>" + escapeHtml(safe(item.title) || safe(item.entry_type) || '历史记录') + '</div>' +
            "<div class='defect-history-time'>" + escapeHtml(safe(item.created_at)) + '</div>' +
          '</div>' +
          "<div class='defect-history-sub'>" + escapeHtml(safe(item.actor) || '-') + '</div>' +
          body +
        '</div>'
      );
    }).join('');
  }

  function defectTaskRefsHtml(taskRefs) {
    const rows = Array.isArray(taskRefs) ? taskRefs : [];
    if (!rows.length) {
      return "<div class='hint'>尚未创建任务中心任务引用</div>";
    }
    return rows.map((item) => {
      const ticketMeta = safe(item.graph_name).trim() || safe(item.ticket_id).trim() || '-';
      const nodeMeta = safe(item.node_name).trim() || safe(item.title).trim() || safe(item.focus_node_id).trim() || '-';
      return (
        "<div class='defect-task-card'>" +
          "<div class='defect-task-card-head'>" +
            "<div class='defect-task-card-title'>" + escapeHtml(safe(item.title) || nodeMeta) + '</div>' +
            "<span class='defect-status-chip " + escapeHtml(defectStatusTone(item.node_status || item.scheduler_state)) + "'>" +
              escapeHtml(safe(item.node_status_text) || safe(item.scheduler_state_text) || '待查看') +
            '</span>' +
          '</div>' +
          "<div class='defect-task-card-sub'>" + escapeHtml(ticketMeta) + '</div>' +
          "<div class='defect-task-card-sub'>" + escapeHtml(nodeMeta) + '</div>' +
          "<div class='defect-task-card-actions'>" + defectTaskRefOpenButton(item) + '</div>' +
        '</div>'
      );
    }).join('');
  }

  function renderDefectList() {
    const node = $('defectList');
    if (!node) return;
    const rows = Array.isArray(state.defectList) ? state.defectList : [];
    if (state.defectLoading && !rows.length) {
      node.innerHTML = "<div class='defect-empty-card'><div class='hint'>缺陷列表加载中...</div></div>";
      return;
    }
    if (!rows.length) {
      node.innerHTML = "<div class='defect-empty-card'><div class='defect-empty-title'>暂无缺陷记录</div><div class='hint'>提交一条描述和图片证据后，会在这里形成闭环记录。</div></div>";
      return;
    }
    const currentId = defectSelectedReportId();
    node.innerHTML = rows.map((raw) => {
      const item = normalizeDefectListItem(raw);
      const active = item.report_id === currentId;
      return (
        "<button class='defect-list-item" + (active ? ' active' : '') + "' type='button' data-report-id='" + escapeHtml(item.report_id) + "'>" +
          "<div class='defect-list-item-head'>" +
            "<div class='defect-list-item-title'>" + escapeHtml(item.defect_summary || item.display_id) + '</div>' +
            "<span class='defect-status-chip " + escapeHtml(defectStatusTone(item.status)) + "'>" + escapeHtml(item.status_text) + '</span>' +
          '</div>' +
          "<div class='defect-list-item-sub'>" + escapeHtml(item.display_id || '-') + '</div>' +
          "<div class='defect-list-item-meta'>" + escapeHtml(item.decision_title || item.decision_summary || '等待判定') + '</div>' +
        '</button>'
      );
    }).join('');
  }

  function renderDefectDetail() {
    const body = $('defectDetailBody');
    const meta = $('defectDetailMeta');
    if (!body) return;
    const detail = defectCurrentDetail();
    const report = defectCurrentReport();
    if (!safe(report.report_id).trim()) {
      if (meta) meta.textContent = '请选择左侧缺陷记录';
      body.innerHTML = "<div class='defect-empty-card'><div class='defect-empty-title'>暂无记录详情</div><div class='hint'>筛选或选择左侧记录后，可在这里查看 DTS、结论、任务引用和状态历史。</div></div>";
      return;
    }
    if (meta) meta.textContent = safe(report.display_id || report.dts_id || report.report_id);
    const images = Array.isArray(report.evidence_images) ? report.evidence_images : [];
    const history = Array.isArray(detail.history) ? detail.history : [];
    const taskRefs = Array.isArray(detail.task_refs) ? detail.task_refs : [];
    const decision = report.current_decision && typeof report.current_decision === 'object' ? report.current_decision : {};
    const reviewButtonText = report.status === 'resolved'
      ? '提交复评'
      : (report.status === 'dispute' ? '继续补充并提交复核' : '标记有分歧并提交复核');
    body.innerHTML =
      "<div class='defect-detail-card'>" +
        "<div class='defect-detail-head'>" +
          "<div>" +
            "<div class='defect-detail-title'>" + escapeHtml(report.defect_summary || report.display_id) + '</div>' +
            "<div class='defect-detail-sub'>" + escapeHtml(report.display_id || report.report_id) + '</div>' +
          '</div>' +
          "<span class='defect-status-chip " + escapeHtml(defectStatusTone(report.status)) + "'>" + escapeHtml(report.status_text || defectStatusText(report.status)) + '</span>' +
        '</div>' +
        "<div class='defect-meta-grid'>" +
          defectFormatMetaLine('发现迭代', report.discovered_iteration) +
          defectFormatMetaLine('解决版本', report.resolved_version) +
          defectFormatMetaLine('上报来源', report.report_source) +
          defectFormatMetaLine('结论来源', report.decision_source || safe(decision.decision_source)) +
        '</div>' +
      '</div>' +
      "<div class='defect-detail-card'>" +
        "<div class='card-title'>原始上报</div>" +
        "<div class='defect-report-text'>" + escapeHtml(report.report_text || '-') + '</div>' +
        "<div class='defect-image-list'>" +
          (images.length ? images.map((item) => defectImageThumbHtml(item, '', '')).join('') : "<div class='hint'>未附带图片证据</div>") +
        '</div>' +
      '</div>' +
      "<div class='defect-detail-card'>" +
        "<div class='card-title'>当前判定 / 复评结论</div>" +
        "<div class='defect-decision-title'>" + escapeHtml(safe(decision.title) || report.decision_title || '等待结论') + '</div>' +
        "<div class='defect-report-text'>" + escapeHtml(safe(decision.summary) || report.decision_summary || '-') + '</div>' +
      '</div>' +
      "<div class='defect-detail-card'>" +
        "<div class='row between'>" +
          "<div class='card-title'>任务引用</div>" +
          (detail.can_process
            ? "<button id='defectCreateProcessTaskBtn' type='button'>处理缺陷</button>"
            : '') +
        '</div>' +
        "<div class='defect-task-list'>" + defectTaskRefsHtml(taskRefs) + '</div>' +
      '</div>' +
      ((report.is_formal || report.status === 'resolved')
        ? "<div class='defect-detail-card'>" +
            "<div class='card-title'>解决版本与确认</div>" +
            "<div class='defect-action-grid'>" +
              "<label class='defect-field defect-span-2'>" +
                "<span class='hint'>解决版本</span>" +
                "<input id='defectResolvedVersionInput' type='text' value='" + escapeHtml(report.resolved_version) + "' placeholder='留空则使用当前 workflow 版本' />" +
              '</label>' +
            '</div>' +
            "<div class='defect-detail-actions'>" +
              ((report.status === 'unresolved' || report.status === 'dispute')
                ? "<button id='defectResolvedVersionBtn' class='alt' type='button'>写回解决版本</button>"
                : '') +
              (detail.can_close ? "<button id='defectCloseBtn' type='button'>确认关闭</button>" : '') +
              (report.status === 'closed' ? "<button id='defectReopenBtn' class='alt' type='button'>重新打开</button>" : '') +
            '</div>' +
          '</div>'
        : '') +
      (detail.show_re_review_input
        ? "<div class='defect-detail-card'>" +
            "<div class='card-title'>补充说明 / 复评输入</div>" +
            "<div class='hint'>首轮不成立后的补充与已解决后的复评共用同一输入区。</div>" +
            "<div class='defect-action-grid'>" +
              "<label class='defect-field defect-span-2'>" +
                "<span class='hint'>补充说明</span>" +
                "<textarea id='defectSharedTextInput' rows='5' placeholder='补充说明当前证据、复现结果或分歧点'></textarea>" +
              '</label>' +
              "<label class='defect-field defect-span-2'>" +
                "<span class='hint'>补充图片证据</span>" +
                "<input id='defectSharedImageInput' type='file' multiple accept='.png,.jpg,.jpeg,.webp,image/png,image/jpeg,image/webp' />" +
              '</label>' +
            '</div>' +
            "<div id='defectSharedImageList' class='defect-image-list'></div>" +
            "<div class='defect-detail-actions'>" +
              "<button id='defectSubmitReviewBtn' type='button'>" + escapeHtml(reviewButtonText) + '</button>' +
            '</div>' +
          '</div>'
        : '') +
      "<div class='defect-detail-card'>" +
        "<div class='card-title'>状态变更历史</div>" +
        "<div class='defect-history-list'>" + defectHistoryHtml(history) + '</div>' +
      '</div>';
    renderDefectDraftImages('defectSharedImageList', state.defectSupplementDraftImages, 'removeDefectSupplementDraftImage');
  }

  function renderDefectCenter() {
    setRequirementBugModule(state.requirementBugModule, { persist: false });
    const keywordInput = $('defectKeywordInput');
    const statusSelect = $('defectStatusFilterSelect');
    if (keywordInput && document.activeElement !== keywordInput) {
      keywordInput.value = safe(state.defectKeyword);
    }
    if (statusSelect && document.activeElement !== statusSelect) {
      statusSelect.value = safe(state.defectStatusFilter).trim() || 'all';
    }
    renderDefectDraftImages('defectDraftImageList', state.defectDraftImages, 'removeDefectDraftImage');
    renderDefectList();
    renderDefectDetail();
    setDefectError(state.defectError);
    setDefectSubmitError(state.defectSubmitError);
    const totalNode = $('defectListMeta');
    if (totalNode) {
      totalNode.textContent = '共 ' + String((state.defectList || []).length) + ' 条记录';
    }
  }

  async function refreshDefectDetail(reportId, options) {
    const key = safe(reportId).trim();
    const opts = options && typeof options === 'object' ? options : {};
    if (!key) {
      state.defectSelectedReportId = '';
      state.defectDetail = null;
      renderDefectCenter();
      return null;
    }
    state.defectDetailLoading = true;
    try {
      const data = await getJSON(defectApiUrl('/api/defects/' + encodeURIComponent(key)));
      state.defectSelectedReportId = key;
      state.defectDetail = data;
      setDefectError('');
      if (!opts.skipRender) {
        renderDefectCenter();
      }
      return data;
    } finally {
      state.defectDetailLoading = false;
    }
  }

  async function refreshDefectList(options) {
    const opts = options && typeof options === 'object' ? options : {};
    state.defectLoading = true;
    try {
      const data = await getJSON(defectApiUrl('/api/defects', {
        status: safe(state.defectStatusFilter).trim() || 'all',
        keyword: safe(state.defectKeyword).trim(),
        limit: 200,
      }));
      state.defectList = Array.isArray(data.items) ? data.items.map(normalizeDefectListItem) : [];
      const preferred = safe(opts.preferredReportId).trim();
      const available = new Set(state.defectList.map((item) => safe(item.report_id).trim()).filter((item) => !!item));
      let nextReportId = preferred || defectSelectedReportId();
      if (!available.has(nextReportId)) {
        nextReportId = state.defectList.length ? safe(state.defectList[0].report_id).trim() : '';
      }
      state.defectSelectedReportId = nextReportId;
      if (!opts.skipRender) {
        renderDefectCenter();
      }
      if (!opts.skipDetail && nextReportId) {
        return await refreshDefectDetail(nextReportId, { skipRender: true });
      }
      if (!nextReportId) {
        state.defectDetail = null;
      }
      renderDefectCenter();
      return data;
    } finally {
      state.defectLoading = false;
      renderDefectCenter();
    }
  }

  function clearDefectDraftForm() {
    state.defectDraftImages = [];
    if ($('defectSummaryInput')) $('defectSummaryInput').value = '';
    if ($('defectReportTextInput')) $('defectReportTextInput').value = '';
    if ($('defectReportImageInput')) $('defectReportImageInput').value = '';
    renderDefectDraftImages('defectDraftImageList', state.defectDraftImages, 'removeDefectDraftImage');
  }

  function clearDefectSharedDraft() {
    state.defectSupplementDraftImages = [];
    if ($('defectSharedTextInput')) $('defectSharedTextInput').value = '';
    if ($('defectSharedImageInput')) $('defectSharedImageInput').value = '';
    renderDefectDraftImages('defectSharedImageList', state.defectSupplementDraftImages, 'removeDefectSupplementDraftImage');
  }

  async function submitDefectReport() {
    const payload = await postJSON('/api/defects', {
      defect_summary: safe($('defectSummaryInput') ? $('defectSummaryInput').value : '').trim(),
      report_text: safe($('defectReportTextInput') ? $('defectReportTextInput').value : '').trim(),
      evidence_images: state.defectDraftImages,
      operator: 'web-user',
    });
    clearDefectDraftForm();
    setDefectSubmitError('');
    setRequirementBugModule('defect');
    await refreshDefectList({ preferredReportId: safe(payload && payload.report && payload.report.report_id).trim() });
    setStatus('缺陷记录已提交');
    return payload;
  }

  async function submitDefectReviewFlow() {
    const report = defectCurrentReport();
    const reportId = safe(report.report_id).trim();
    if (!reportId) return null;
    const text = safe($('defectSharedTextInput') ? $('defectSharedTextInput').value : '').trim();
    const images = Array.isArray(state.defectSupplementDraftImages) ? state.defectSupplementDraftImages : [];
    if (!text && !images.length) {
      throw new Error('请先补充说明或图片证据');
    }
    if (text) {
      await postJSON('/api/defects/' + encodeURIComponent(reportId) + '/supplements/text', {
        text: text,
        operator: 'web-user',
      });
    }
    if (images.length) {
      await postJSON('/api/defects/' + encodeURIComponent(reportId) + '/supplements/images', {
        evidence_images: images,
        operator: 'web-user',
      });
    }
    if (report.status === 'not_formal' || report.status === 'resolved') {
      await postJSON('/api/defects/' + encodeURIComponent(reportId) + '/dispute', {
        reason: text,
        operator: 'web-user',
      });
    }
    const result = await postJSON('/api/defects/' + encodeURIComponent(reportId) + '/review-task', {
      operator: 'web-user',
    });
    clearDefectSharedDraft();
    await refreshDefectList({ preferredReportId: reportId });
    setStatus('复核任务已创建');
    return result;
  }

  async function createDefectProcessTaskAction() {
    const report = defectCurrentReport();
    const reportId = safe(report.report_id).trim();
    if (!reportId) return null;
    const result = await postJSON('/api/defects/' + encodeURIComponent(reportId) + '/process-task', {
      operator: 'web-user',
    });
    await refreshDefectList({ preferredReportId: reportId });
    setStatus('处理任务已创建');
    return result;
  }

  async function writeDefectResolvedVersionAction() {
    const report = defectCurrentReport();
    const reportId = safe(report.report_id).trim();
    if (!reportId) return null;
    const result = await postJSON('/api/defects/' + encodeURIComponent(reportId) + '/resolved-version', {
      resolved_version: safe($('defectResolvedVersionInput') ? $('defectResolvedVersionInput').value : '').trim(),
      operator: 'web-user',
    });
    await refreshDefectList({ preferredReportId: reportId });
    setStatus('解决版本已写回');
    return result;
  }

  async function closeDefectAction() {
    const report = defectCurrentReport();
    const reportId = safe(report.report_id).trim();
    if (!reportId) return null;
    const result = await postJSON('/api/defects/' + encodeURIComponent(reportId) + '/status', {
      status: 'closed',
      operator: 'web-user',
    });
    await refreshDefectList({ preferredReportId: reportId });
    setStatus('缺陷已关闭');
    return result;
  }

  async function reopenDefectAction() {
    const report = defectCurrentReport();
    const reportId = safe(report.report_id).trim();
    if (!reportId) return null;
    const result = await postJSON('/api/defects/' + encodeURIComponent(reportId) + '/status', {
      status: 'unresolved',
      operator: 'web-user',
    });
    await refreshDefectList({ preferredReportId: reportId });
    setStatus('缺陷已重新打开');
    return result;
  }
