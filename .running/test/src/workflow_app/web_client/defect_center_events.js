  let defectKeywordTimer = 0;

  function removeDefectDraftImage(imageId) {
    const targetId = safe(imageId).trim();
    state.defectDraftImages = (Array.isArray(state.defectDraftImages) ? state.defectDraftImages : [])
      .filter((item) => safe(item && item.image_id).trim() !== targetId);
    renderDefectDraftImages('defectDraftImageList', state.defectDraftImages, 'removeDefectDraftImage');
  }

  function removeDefectSupplementDraftImage(imageId) {
    const targetId = safe(imageId).trim();
    state.defectSupplementDraftImages = (Array.isArray(state.defectSupplementDraftImages) ? state.defectSupplementDraftImages : [])
      .filter((item) => safe(item && item.image_id).trim() !== targetId);
    renderDefectDraftImages('defectSharedImageList', state.defectSupplementDraftImages, 'removeDefectSupplementDraftImage');
  }

  async function appendDefectImagesFromFiles(files, targetKey) {
    const list = Array.isArray(files) ? files : Array.from(files || []);
    const nextRows = [];
    for (const file of list) {
      if (!file) continue;
      const dataUrl = await defectReadFileAsDataUrl(file);
      nextRows.push({
        image_id: 'img-' + String(Date.now()) + '-' + String(Math.floor(Math.random() * 100000)),
        name: safe(file.name),
        url: dataUrl,
      });
    }
    if (targetKey === 'supplement') {
      state.defectSupplementDraftImages = (Array.isArray(state.defectSupplementDraftImages) ? state.defectSupplementDraftImages : []).concat(nextRows);
      renderDefectDraftImages('defectSharedImageList', state.defectSupplementDraftImages, 'removeDefectSupplementDraftImage');
      return;
    }
    state.defectDraftImages = (Array.isArray(state.defectDraftImages) ? state.defectDraftImages : []).concat(nextRows);
    renderDefectDraftImages('defectDraftImageList', state.defectDraftImages, 'removeDefectDraftImage');
  }

  function ensureDefectProbeOutputNode() {
    let node = $('defectCenterProbeOutput');
    if (node) return node;
    node = document.createElement('pre');
    node.id = 'defectCenterProbeOutput';
    node.style.display = 'none';
    document.body.appendChild(node);
    return node;
  }

  function collectDefectProbe() {
    const detail = defectCurrentDetail();
    const report = defectCurrentReport();
    const detailScroll = $('defectDetailScroll');
    const reviewBtn = $('defectSubmitReviewBtn');
    return {
      ts: new Date().toISOString(),
      case: defectProbeCase(),
      pass: false,
      active_tab: readSavedAppTab(),
      active_module: safe(state.requirementBugModule).trim(),
      list_total: Array.isArray(state.defectList) ? state.defectList.length : 0,
      selected_report_id: safe(report.report_id).trim(),
      selected_display_id: safe(report.display_id || report.dts_id || report.report_id).trim(),
      selected_status: safe(report.status).trim(),
      selected_status_text: safe(report.status_text).trim(),
      task_ref_total: Number(detail.task_ref_total || 0),
      history_total: Number(detail.history_total || 0),
      filter_value: safe(state.defectStatusFilter).trim(),
      keyword_value: safe(state.defectKeyword).trim(),
      process_btn_visible: !!$('defectCreateProcessTaskBtn'),
      review_btn_visible: !!reviewBtn,
      review_btn_text: safe(reviewBtn ? reviewBtn.textContent : '').trim(),
      detail_scrollable: !!(detailScroll && (detailScroll.scrollHeight > detailScroll.clientHeight || getComputedStyle(detailScroll).overflowY !== 'visible')),
      requirement_empty_visible: safe(state.requirementBugModule).trim() === 'requirement' && /暂未开放/.test(safe($('rbModuleRequirement') ? $('rbModuleRequirement').textContent : '')),
      list_item_count: document.querySelectorAll('#defectList .defect-list-item').length,
    };
  }

  async function runDefectCenterProbe() {
    const output = ensureDefectProbeOutputNode();
    const probeCase = defectProbeCase();
    const reportId = safe(queryParam('defect_probe_report')).trim();
    const statusValue = safe(queryParam('defect_probe_status')).trim() || state.defectStatusFilter || 'all';
    const keywordValue = safe(queryParam('defect_probe_keyword')).trim();
    try {
      switchTab('requirement-bug');
      state.defectStatusFilter = statusValue || 'all';
      state.defectKeyword = keywordValue;
      await refreshDefectList({ preferredReportId: reportId || defectSelectedReportId() });
      if (probeCase === 'requirement_empty') {
        setRequirementBugModule('requirement');
      } else {
        setRequirementBugModule('defect');
      }
      if ((probeCase === 'dispute_supplement' || probeCase === 'review_input') && $('defectSharedTextInput')) {
        $('defectSharedTextInput').value = probeCase === 'review_input'
          ? '补充复评说明：当前版本仍有残留问题。'
          : '补充争议说明：当前判定与实际现象不一致。';
      }
      if (probeCase === 'dispute_supplement' || probeCase === 'review_input') {
        state.defectSupplementDraftImages = [{
          image_id: 'probe-image',
          name: 'probe.png',
          url: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+cC8QAAAAASUVORK5CYII=',
        }];
        renderDefectDraftImages('defectSharedImageList', state.defectSupplementDraftImages, 'removeDefectSupplementDraftImage');
      }
      const result = collectDefectProbe();
      if (probeCase === 'requirement_empty') {
        result.pass = !!result.requirement_empty_visible;
      } else if (probeCase === 'filter_search') {
        result.pass = result.list_total >= 0 && result.list_item_count >= 0;
      } else {
        result.pass = !!result.selected_report_id && result.detail_scrollable;
      }
      output.textContent = JSON.stringify(result);
      output.setAttribute('data-pass', result.pass ? '1' : '0');
    } catch (err) {
      const result = collectDefectProbe();
      result.error = safe(err && err.message ? err.message : err);
      output.textContent = JSON.stringify(result);
      output.setAttribute('data-pass', '0');
    }
  }

  function bindDefectCenterEvents() {
    const requirementBtn = $('rbTabRequirementBtn');
    const defectBtn = $('rbTabDefectBtn');
    if (requirementBtn) {
      requirementBtn.onclick = () => {
        setRequirementBugModule('requirement');
      };
    }
    if (defectBtn) {
      defectBtn.onclick = () => {
        setRequirementBugModule('defect');
        refreshDefectList({ preserveSelection: true }).catch((err) => {
          setDefectError(err.message || String(err));
        });
      };
    }
    if ($('defectRefreshBtn')) {
      $('defectRefreshBtn').onclick = async () => {
        try {
          await withButtonLock('defectRefreshBtn', async () => {
            await refreshDefectList({ preserveSelection: true });
          });
        } catch (err) {
          setDefectError(err.message || String(err));
        }
      };
    }
    if ($('defectSubmitBtn')) {
      $('defectSubmitBtn').onclick = async () => {
        try {
          await withButtonLock('defectSubmitBtn', async () => {
            await submitDefectReport();
          });
        } catch (err) {
          setDefectSubmitError(err.message || String(err));
        }
      };
    }
    if ($('defectStatusFilterSelect')) {
      $('defectStatusFilterSelect').addEventListener('change', () => {
        state.defectStatusFilter = safe($('defectStatusFilterSelect').value).trim() || 'all';
        refreshDefectList({ preserveSelection: false }).catch((err) => {
          setDefectError(err.message || String(err));
        });
      });
    }
    if ($('defectKeywordInput')) {
      $('defectKeywordInput').addEventListener('input', () => {
        state.defectKeyword = safe($('defectKeywordInput').value);
        window.clearTimeout(defectKeywordTimer);
        defectKeywordTimer = window.setTimeout(() => {
          refreshDefectList({ preserveSelection: false }).catch((err) => {
            setDefectError(err.message || String(err));
          });
        }, 220);
      });
    }
    if ($('defectReportImageInput')) {
      $('defectReportImageInput').addEventListener('change', async (event) => {
        try {
          const target = event.target;
          await appendDefectImagesFromFiles(target && target.files ? target.files : [], 'draft');
        } catch (err) {
          setDefectSubmitError(err.message || String(err));
        }
      });
    }
    if ($('defectList')) {
      $('defectList').addEventListener('click', (event) => {
        const target = event.target;
        if (!(target instanceof Element)) return;
        const item = target.closest('.defect-list-item');
        if (!item) return;
        const reportId = safe(item.getAttribute('data-report-id')).trim();
        if (!reportId) return;
        refreshDefectDetail(reportId).catch((err) => {
          setDefectError(err.message || String(err));
        });
      });
    }
    if ($('defectDraftImageList')) {
      $('defectDraftImageList').addEventListener('click', (event) => {
        const target = event.target;
        if (!(target instanceof Element)) return;
        const btn = target.closest('button[data-remove-action]');
        if (!btn) return;
        removeDefectDraftImage(btn.getAttribute('data-image-id'));
      });
    }
    if ($('defectDetailBody')) {
      $('defectDetailBody').addEventListener('click', async (event) => {
        const target = event.target;
        if (!(target instanceof Element)) return;
        const removeBtn = target.closest('button[data-remove-action]');
        if (removeBtn) {
          removeDefectSupplementDraftImage(removeBtn.getAttribute('data-image-id'));
          return;
        }
        const openTaskBtn = target.closest('.defect-open-task-btn');
        if (openTaskBtn) {
          defectOpenTaskCenter(openTaskBtn.getAttribute('data-ticket-id'), openTaskBtn.getAttribute('data-node-id'));
          return;
        }
        try {
          if (target.closest('#defectCreateProcessTaskBtn')) {
            await createDefectProcessTaskAction();
            return;
          }
          if (target.closest('#defectResolvedVersionBtn')) {
            await writeDefectResolvedVersionAction();
            return;
          }
          if (target.closest('#defectCloseBtn')) {
            await closeDefectAction();
            return;
          }
          if (target.closest('#defectReopenBtn')) {
            await reopenDefectAction();
            return;
          }
          if (target.closest('#defectSubmitReviewBtn')) {
            await submitDefectReviewFlow();
          }
        } catch (err) {
          setDefectError(err.message || String(err));
        }
      });
      $('defectDetailBody').addEventListener('change', async (event) => {
        const target = event.target;
        if (!(target instanceof Element)) return;
        if (target.id === 'defectSharedImageInput') {
          try {
            await appendDefectImagesFromFiles(target.files ? target.files : [], 'supplement');
          } catch (err) {
            setDefectError(err.message || String(err));
          }
        }
      });
    }
  }
