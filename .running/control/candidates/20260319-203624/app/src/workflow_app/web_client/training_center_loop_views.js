  // Training center loop views and stage rendering.

  function renderTrainingLoopProcessCard(mode, queueRow, loopData) {
    const box = $('tcLoopProcessCard');
    if (!box) return;
    const view = normalizeTrainingLoopMode(mode);
    const snapshot = trainingLoopPlanSnapshot();
    const loopCtx = trainingLoopSelectedNodeContext(loopData);
    const stageIndex = trainingLoopStageIndex(view, queueRow);
    const agentName =
      safe(queueRow && (queueRow.agent_name || queueRow.target_agent_id)).trim() ||
      snapshot.targetName ||
      '-';
    const goal = safe(queueRow && queueRow.capability_goal).trim() || snapshot.capabilityGoal || '-';
    const stageTitle = safe(TC_LOOP_STAGES[stageIndex - 1] && TC_LOOP_STAGES[stageIndex - 1].title).trim();
    const currentRoundIndex = Number(loopCtx.selectedNode && loopCtx.selectedNode.round_index ? loopCtx.selectedNode.round_index : 0);

    const taskTitle = view === 'create' ? '创建训练任务' : goal || agentName || '训练任务';
    const subLine =
      view === 'create'
        ? '当前正在准备首轮训练目标、工作集与启动条件。'
        : (goal ? '目标能力：' + goal + ' · ' : '') +
          (currentRoundIndex > 0 ? '当前位于第 ' + safe(currentRoundIndex) + ' 轮' : '当前位于任务状态页');
    const chipRow =
      view === 'create'
        ? "<span class='tc-loop-chip blue'>创建态</span><span class='tc-loop-chip green'>可直接启动首轮</span>"
        : "<span class='tc-loop-chip blue'>任务状态</span>" +
          (currentRoundIndex > 0
            ? "<span class='tc-loop-chip orange'>第 " + safe(currentRoundIndex) + ' 轮</span>'
            : '') +
          "<span class='tc-loop-chip orange'>阶段 " +
          safe(stageIndex) +
          '/5</span>';

    const metaCards = [
      ['目标角色', agentName || '-'],
      ['能力目标', goal || '-'],
      [
        '优先级',
        safe(queueRow && queueRow.priority).trim() ||
          safe($('tcPlanPrioritySelect') ? $('tcPlanPrioritySelect').value : '').trim() ||
          '-',
      ],
      ['下一步', view === 'create' ? '保存草稿或启动首轮' : stageIndex >= 4 ? '查看判定并决定下一步' : '继续推进当前轮'],
    ];

    const evolutionTitle = view === 'create' ? '训练路径预览' : '训练演进图';
    const evolutionDesc =
      view === 'create'
        ? '先确认训练主线、回退分支与进入下一轮的收敛路径。'
        : state.tcLoopServerLoading
          ? '正在回读训练演进图。'
          : state.tcLoopServerError
            ? '演进图加载失败，请刷新重试。'
            : loopCtx.nodes.length
              ? '演进图来自后端闭环状态；点击节点可联动右侧节点判定。'
              : '当前暂无历史节点。';
    const evolutionCaption =
      view === 'create'
        ? '首轮若能力劣化将撤销本轮新增；首轮若提升但不足阈值，将保留主线进入下一轮。'
        : loopCtx.metricsAvailable
          ? '当前节点指标已回写，可结合右侧节点判定继续推进。'
          : '当前暂无评分或阈值：' + (loopCtx.metricsReason || '后端尚未回写评分');

    box.innerHTML =
      "<div class='tc-loop-process-card'>" +
      "<div class='tc-loop-process-head'>" +
      '<div>' +
      "<div class='tc-loop-process-title'>" +
      safe(taskTitle) +
      '</div>' +
      "<div class='tc-loop-process-sub'>" +
      safe(subLine) +
      '</div>' +
      '</div>' +
      "<div class='tc-loop-chip-row'>" +
      chipRow +
      '</div>' +
      '</div>' +
      "<div class='tc-loop-stage'>" +
      '<div>' +
      "<div class='tc-loop-stage-title'>当前阶段：" +
      safe(stageTitle) +
      '</div>' +
      "<div class='tc-loop-stage-desc'>" +
      (view === 'create'
        ? '提交后会生成对应任务，并根据动作选择进入待评测或直接启动首轮。'
        : stageIndex === 2
          ? '任务已经进入待评测队列，可从右侧或列表继续执行。'
        : stageIndex === 3
            ? 'workflow 正在执行训练链路并回写最近运行状态。'
            : '当前任务已生成阶段结论，可在右侧继续进入下一轮或撤销本轮新增。') +
      '</div>' +
      '</div>' +
      "<div class='tc-loop-meta-grid'>" +
      metaCards
        .map(
          (pair) =>
            "<div class='tc-loop-meta-card'><div class='tc-loop-meta-k'>" +
            safe(pair[0]) +
            "</div><div class='tc-loop-meta-v'>" +
            safe(pair[1]) +
            '</div></div>'
        )
        .join('') +
      '</div>' +
      '</div>' +
      renderTrainingLoopSteps(stageIndex, view, queueRow) +
      "<div class='tc-loop-evolution'>" +
      "<div class='tc-loop-evolution-head'>" +
      '<div>' +
      "<div class='tc-loop-evolution-title'>" +
      safe(evolutionTitle) +
      '</div>' +
      "<div class='tc-loop-evolution-desc'>" +
      safe(evolutionDesc) +
      '</div>' +
      '</div>' +
      "<div class='tc-loop-evolution-legend'>" +
      "<span><span class='tc-loop-evolution-dot active'></span>主线</span>" +
      "<span><span class='tc-loop-evolution-dot fail'></span>已回退</span>" +
      "<span><span class='tc-loop-evolution-dot rollback'></span>回退动作</span>" +
      '</div>' +
      '</div>' +
      "<div class='tc-loop-evolution-canvas'>" +
      (view === 'create'
        ? renderTrainingLoopPreviewSvg()
        : renderTrainingLoopEvolutionSvg(loopCtx.payload, loopCtx.selectedNodeId)) +
      '</div>' +
      "<div class='tc-loop-evolution-caption'>" +
      safe(evolutionCaption) +
      '</div>' +
      '</div>' +
      '</div>';

    if (view === 'status') {
      box.onclick = (event) => {
        const target = event && event.target ? event.target : null;
        if (!(target instanceof Element)) return;
        const node = target.closest('circle[data-node-id]');
        if (!node) return;
        const nextId = safe(node.getAttribute('data-node-id')).trim();
        if (!nextId) return;
        setTrainingLoopSelectedNode(nextId);
      };
    } else {
      box.onclick = null;
    }
  }

  function renderTrainingLoopCreateBody() {
    const box = $('tcLoopDetailBody');
    if (!box) return;
    const activeTab = normalizeTrainingLoopCreateTab(state.tcLoopCreateTab);
    const snapshot = trainingLoopPlanSnapshot();
    const validationItems = trainingLoopValidationItems(snapshot);
    restoreTrainingLoopFormCache();

    if (activeTab === 'workset') {
      box.innerHTML =
        renderTrainingLoopSection(
          '首轮工作集',
          '定义首轮要补强的任务项；保存后这些条目会成为当前任务的首轮工作集。',
          "<div class='tc-form-grid'>" +
            "<div class='full'><label class='hint' for='tcPlanTasksInput'>训练任务（每行一项）</label><div id='tcLoopFieldMountTasks'></div></div>" +
            '</div>' +
            renderTrainingLoopSection(
              '工作集预览',
              '',
              "<div class='tc-loop-summary-inline'>" +
                "<div class='tc-loop-inline-stat'><span>任务数</span><strong>" +
                safe(snapshot.trainingTasks.length || 0) +
                '</strong></div>' +
                "<div class='tc-loop-inline-stat'><span>执行主体</span><strong>" +
                safe(snapshot.executionLabel) +
                '</strong></div>' +
                '</div>' +
                renderTrainingLoopBulletList(snapshot.trainingTasks.slice(0, 6)),
              'tone-soft'
            ),
          ''
        );
      mountTrainingLoopField('tcPlanTasksInput', 'tcLoopFieldMountTasks', {
        rows: 8,
        placeholder: '- 补齐评分维度说明',
      });
      return;
    }

    if (activeTab === 'launch') {
      const allReady =
        validationItems.every((item) => !!item.ok) &&
        state.agentSearchRootReady &&
        !snapshot.frozen;
      const statusLine = !state.agentSearchRootReady
        ? '当前工作区未就绪，暂不能提交训练任务。'
        : snapshot.frozen
          ? '当前角色已禁训，请切回可训练版本后再提交。'
          : allReady
            ? '已满足提交条件，可保存草稿或直接启动首轮。'
            : '仍有必填项未补齐，请先返回基础信息或首轮工作集。';
      box.innerHTML =
        renderTrainingLoopSection(
          '启动确认',
          '保存草稿会将任务写入待评测队列；保存并启动首轮会在保存后立即触发 workflow 内部训练链路。',
          renderTrainingLoopSummaryRows([
            ['目标角色', snapshot.targetName || '-'],
            ['能力目标', snapshot.capabilityGoal || '-'],
            ['首轮工作集', (snapshot.trainingTasks.length ? snapshot.trainingTasks.length : 0) + ' 项'],
            ['验收标准', snapshot.acceptanceCriteria || '-'],
            ['优先级', snapshot.priority || '-'],
            ['执行主体', snapshot.executionLabel || '-'],
          ]) +
            "<div class='tc-loop-check-grid'>" +
            validationItems
              .map(
                (item) =>
                  "<div class='tc-loop-check-item" +
                  (item.ok ? ' ok' : '') +
                  "'><div class='tc-loop-check-k'>" +
                  safe(item.label) +
                  "</div><div class='tc-loop-check-v'>" +
                  safe(item.value) +
                  '</div></div>'
              )
              .join('') +
            '</div>' +
            "<div class='tc-loop-launch-hint'>" +
            safe(statusLine) +
            '</div>' +
            "<div class='tc-loop-action-row tc-loop-launch-actions'>" +
            "<button id='tcSaveAndStartBtn' type='button' " +
            (allReady ? '' : 'disabled') +
            '>保存并启动首轮</button>' +
            "<button id='tcSaveDraftBtn' class='alt' type='button' " +
            (allReady ? '' : 'disabled') +
            '>保存草稿</button>' +
            '</div>' +
            "<div class='hint'>提交成功后将自动切换到对应任务状态页。</div>",
          ''
        );
      const startBtn = $('tcSaveAndStartBtn');
      if (startBtn) {
        startBtn.onclick = async () => {
          try {
            await withButtonLock('tcSaveAndStartBtn', async () => {
              await submitTrainingCenterPlanFromLoop('start');
            });
          } catch (err) {
            setTrainingCenterError(err.message || String(err));
          }
        };
      }
      const draftBtn = $('tcSaveDraftBtn');
      if (draftBtn) {
        draftBtn.onclick = async () => {
          try {
            await withButtonLock('tcSaveDraftBtn', async () => {
              await submitTrainingCenterPlanFromLoop('draft');
            });
          } catch (err) {
            setTrainingCenterError(err.message || String(err));
          }
        };
      }
      updateTrainingCenterOpsGateState();
      return;
    }

    box.innerHTML =
      renderTrainingLoopSection(
        '基础信息',
        '先确认训练目标、验收口径和优先级，再切到首轮工作集与启动确认。',
        "<div class='tc-form-grid'>" +
          "<div class='full'><label class='hint' for='tcPlanTargetAgentSelect'>目标角色</label><div id='tcLoopFieldMountTarget'></div></div>" +
          "<div class='full'><label class='hint' for='tcPlanGoalInput'>能力目标</label><div id='tcLoopFieldMountGoal'></div></div>" +
          "<div class='full'><label class='hint' for='tcPlanAcceptanceInput'>验收标准</label><div id='tcLoopFieldMountAcceptance'></div></div>" +
          "<div><label class='hint' for='tcPlanPrioritySelect'>优先级（必填）</label><div id='tcLoopFieldMountPriority'></div></div>" +
          "<div><label class='hint'>执行主体</label><div class='tc-loop-static-field'>" + safe(snapshot.executionLabel) + '</div></div>' +
          '</div>' +
          renderTrainingLoopSection(
            '当前填写摘要',
            '',
            renderTrainingLoopSummaryRows([
              ['目标角色', snapshot.targetName || '-'],
              ['能力目标', snapshot.capabilityGoal || '-'],
              ['优先级', snapshot.priority || '-'],
              ['首轮工作集', snapshot.trainingTasks.length ? snapshot.trainingTasks.length + ' 项' : '待填写'],
            ]),
            'tone-soft'
          ),
        ''
      );
    mountTrainingLoopField('tcPlanTargetAgentSelect', 'tcLoopFieldMountTarget');
    mountTrainingLoopField('tcPlanGoalInput', 'tcLoopFieldMountGoal', {
      placeholder: '例如：提升角色策略评分解释性',
    });
    mountTrainingLoopField('tcPlanAcceptanceInput', 'tcLoopFieldMountAcceptance', {
      rows: 5,
      placeholder: '例如：评分卡输出含维度分/扣分证据/修复建议',
    });
    mountTrainingLoopField('tcPlanPrioritySelect', 'tcLoopFieldMountPriority');
  }

  function renderTrainingLoopStatusBody(queueRow, loopData, statusDetail) {
    const box = $('tcLoopDetailBody');
    if (!box) return;
    restoreTrainingLoopFormCache();
    const tab = normalizeTrainingLoopStatusTab(state.tcLoopStatusTab);
    if (!queueRow) {
      box.innerHTML = renderTrainingLoopSection(
        '任务状态',
        '请先从左侧任务列表中选择一个已有任务。',
        "<div class='tc-loop-empty'>当前没有可展示的任务状态。</div>",
        ''
      );
      return;
    }

    const loopCtx = trainingLoopSelectedNodeContext(loopData);
    const detailCtx = trainingLoopStatusDetailContext(statusDetail);
    const overview = detailCtx.overview || {};
    const workset = detailCtx.workset || {};
    const evaluations = detailCtx.evaluations || [];
    const historyRecords = detailCtx.historyRecords || [];
    const agentName =
      safe(overview.agent_name || queueRow.agent_name || queueRow.target_agent_id).trim() || '-';
    const goal = safe(overview.capability_goal || queueRow.capability_goal).trim() || '-';
    const latestRunId = safe(overview.latest_run_id || queueRow.latest_run_id).trim();
    const latestRunStatus = safe(overview.latest_run_status || queueRow.latest_run_status).trim();
    const latestRunAt = safe(overview.updated_at || queueRow.latest_run_updated_at).trim();
    const latestRunRef = safe(overview.latest_run_ref || queueRow.latest_run_ref).trim();
    const latestResultSummary = safe(overview.latest_result_summary || queueRow.latest_result_summary).trim();
    const selectedNode = loopCtx.selectedNode || null;
    const avgText = trainingLoopScoreText(overview.avg_score, '待三轮评测完成');
    const thresholdText = trainingLoopScoreText(overview.threshold, '-');
    const previousAvgText = trainingLoopScoreText(overview.previous_avg_score, '无上一轮');
    const metricsText =
      overview && overview.metrics_available
        ? 'Avg=' +
          safe(avgText) +
          '\nThreshold=' +
          safe(thresholdText) +
          '\nPrevious Avg=' +
          safe(previousAvgText) +
          '\nDecision=' +
          safe(overview.decision || '-') +
          '\nNext Action=' +
          safe(overview.next_action || '-')
        : '暂无最终评分指标' +
          (safe(overview.metrics_unavailable_reason).trim()
            ? '（' + safe(overview.metrics_unavailable_reason) + '）'
            : '');

    if (tab === 'workset') {
      box.innerHTML =
        renderTrainingLoopSection(
          '工作集变化',
          '本页展示后端回写的当前轮工作集摘要、结构化变化和回退状态。',
          renderTrainingLoopSummaryRows([
            ['当前任务', goal],
            ['目标角色', agentName],
            ['验收标准', safe(overview.acceptance_criteria || queueRow.acceptance_criteria).trim() || '-'],
            ['变化摘要', safe(workset.delta_summary).trim() || '当前没有结构化变化摘要'],
            ['回退状态', workset && workset.rollback_applied ? '已回退本轮新增' : '主线保留'],
          ]) +
            renderTrainingLoopSection(
              '结构化工作集',
              '',
              renderTrainingLoopWorksetItems(workset),
              'tone-soft'
            ),
          ''
        );
      return;
    }

    if (tab === 'eval') {
      box.innerHTML =
        renderTrainingLoopSection(
          '三轮评测',
          '每一轮评测均由后端真实落库的 Run1 / Run2 / Run3 构成，Avg 也由后端计算。',
          renderTrainingLoopSummaryRows([
            ['最近运行', latestRunId || '暂无'],
            ['运行状态', latestRunStatus ? statusText(latestRunStatus) : '暂无'],
            ['更新时间', latestRunAt || '-'],
            ['执行主体', trainingExecutionEngineLabel(overview.execution_engine || queueRow.execution_engine) || 'workflow 内建训练能力'],
          ]) +
            renderTrainingLoopSection(
              '最近回执',
              '',
              latestRunId
                ? "<pre class='pre tc-loop-inline-pre'>run_id=" +
                  safe(latestRunId) +
                  '\nstatus=' +
                  safe(latestRunStatus || '-') +
                  '\nupdated_at=' +
                  safe(latestRunAt || '-') +
                  (latestRunRef ? '\nrun_ref=' + safe(latestRunRef) : '') +
                  (latestResultSummary ? '\nsummary=' + safe(latestResultSummary) : '') +
                  '</pre>'
                : "<div class='tc-loop-empty'>当前还没有训练运行回执。</div>",
              'tone-soft'
            ) +
            renderTrainingLoopSection(
              '三轮明细',
              '',
              renderTrainingLoopEvaluationCards(evaluations, queueRow.queue_task_id),
              'tone-soft'
            ),
          ''
        );
      return;
    }

    if (tab === 'history') {
      box.innerHTML =
        renderTrainingLoopSection(
          '历史记录',
          '这里回看每一轮后端回写的真实摘要、分数与审计引用。',
          renderTrainingLoopSummaryRows([
            ['loop_id', loopCtx.loopId],
            ['当前节点', safe(selectedNode && selectedNode.title).trim() || safe(loopCtx.currentNodeId).trim() || '-'],
            ['轮次数量', safe(historyRecords.length || 0)],
            ['测试数据', loopCtx.isTestData ? '是' : '否'],
          ]) + renderTrainingLoopBackendHistoryList(historyRecords),
          ''
        );
      return;
    }

    box.innerHTML =
      renderTrainingLoopSection(
        '当前概览',
        '先看当前任务摘要、最近运行状态和当前节点结论。',
        renderTrainingLoopSummaryRows([
          ['任务状态', statusText(overview.queue_status || queueRow.status || '-') + ' / ' + safe(overview.priority || queueRow.priority || '-')],
          ['目标角色', agentName],
          ['能力目标', goal],
          ['当前轮次', safe(overview.round_index || (selectedNode && selectedNode.round_index) || '-')],
          ['节点判定', safe(overview.decision || (selectedNode && selectedNode.decision)).trim() || '暂无判定'],
          ['下一步动作', safe(overview.next_action || (selectedNode && selectedNode.next_action)).trim() || '暂无下一步动作'],
        ]) +
          renderTrainingLoopSection(
            '评分与运行摘要',
            '',
            "<pre class='pre tc-loop-inline-pre'>" +
            safe(metricsText) +
            '</pre>' +
            "<div class='tc-loop-inline-meta'>最近运行：" +
            safe(latestRunId || '暂无') +
            (latestRunStatus ? ' · ' + safe(statusText(latestRunStatus)) : '') +
            (latestRunAt ? ' · ' + safe(latestRunAt) : '') +
            '</div>',
            'tone-soft'
          ),
        ''
      );
  }

  function renderTrainingLoopDetailFrame(mode, queueRow, loopData, statusDetail) {
    const head = $('tcLoopDetailHead');
    const body = $('tcLoopDetailBody');
    if (!head || !body) return;
    const view = normalizeTrainingLoopMode(mode);
    const isCreate = view === 'create';
    const tabs = isCreate ? TC_LOOP_CREATE_TABS : TC_LOOP_STATUS_TABS;
    const activeTab = isCreate
      ? normalizeTrainingLoopCreateTab(state.tcLoopCreateTab)
      : normalizeTrainingLoopStatusTab(state.tcLoopStatusTab);
    head.innerHTML =
      "<div class='tc-loop-detail-head'>" +
      '<div>' +
      "<div class='tc-loop-detail-title'>" +
      (isCreate ? '创建任务' : '任务状态详情') +
      '</div>' +
      "<div class='tc-loop-detail-desc'>" +
      (isCreate
        ? '按基础信息、首轮工作集、启动确认三步补齐创建内容。'
        : '按当前概览、工作集变化、三轮评测、历史记录切换查看当前任务。') +
      '</div>' +
      '</div>' +
      '</div>' +
      "<div class='tc-loop-detail-tabs' role='tablist' aria-label='" +
      (isCreate ? '创建任务页签' : '任务状态页签') +
      "'>" +
      tabs
        .map((tabItem) => {
          const active = tabItem.key === activeTab;
          return (
            "<button class='tc-loop-tab" +
            (active ? ' active' : '') +
            "' type='button' role='tab' aria-selected='" +
            (active ? 'true' : 'false') +
            "' data-" +
            (isCreate ? 'create' : 'status') +
            "-tab='" +
            safe(tabItem.key) +
            "'>" +
            safe(tabItem.label) +
            '</button>'
          );
        })
        .join('') +
      '</div>';
    head.onclick = (event) => {
      const target = event && event.target ? event.target : null;
      if (!(target instanceof Element)) return;
      const btn = target.closest('button[data-create-tab],button[data-status-tab]');
      if (!btn) return;
      const createTab = safe(btn.getAttribute('data-create-tab')).trim();
      const statusTab = safe(btn.getAttribute('data-status-tab')).trim();
      if (createTab) {
        setTrainingLoopCreateTab(createTab);
      } else if (statusTab) {
        setTrainingLoopStatusTab(statusTab);
      }
    };
    if (isCreate) {
      renderTrainingLoopCreateBody();
    } else {
      renderTrainingLoopStatusBody(queueRow, loopData, statusDetail);
    }
  }

  function renderTrainingLoopRightPane(mode, queueRow, loopData, statusDetail) {
    const box = $('tcLoopRightPane');
    if (!box) return;
    const view = normalizeTrainingLoopMode(mode);
    if (view === 'create') {
      box.innerHTML = '';
      box.onclick = null;
      return;
    }

    const loopCtx = trainingLoopSelectedNodeContext(loopData);
    const detailCtx = trainingLoopStatusDetailContext(statusDetail);
    const node = loopCtx.selectedNode || null;
    const isCurrent = !!(loopCtx.selectedNodeId && loopCtx.currentNodeId && loopCtx.selectedNodeId === loopCtx.currentNodeId);

    if (state.tcLoopServerLoading) {
      box.innerHTML =
        "<div class='tc-loop-right-title'>当前选中节点</div>" +
        "<div class='tc-loop-right-big'>加载中...</div>" +
        "<div class='tc-loop-right-sub'>正在获取演进图数据</div>";
      return;
    }
    if (state.tcLoopServerError) {
      box.innerHTML =
        "<div class='tc-loop-right-title'>当前选中节点</div>" +
        "<div class='tc-loop-right-big'>加载失败</div>" +
        "<div class='tc-loop-right-sub'>" +
        safe(state.tcLoopServerError) +
        '</div>';
      return;
    }
    if (!queueRow) {
      box.innerHTML =
        "<div class='tc-loop-right-title'>当前选中节点</div>" +
        "<div class='tc-loop-right-big'>未选择任务</div>" +
        "<div class='tc-loop-right-sub'>请先从左侧列表选择一个任务。</div>";
      return;
    }
    if (!loopCtx.nodes.length || !node) {
      box.innerHTML =
        "<div class='tc-loop-right-title'>当前选中节点</div>" +
        "<div class='tc-loop-right-big'>暂无历史</div>" +
        "<div class='tc-loop-right-sub'>当前闭环还没有可联动的节点详情。</div>";
      return;
    }

    const nodeTitle = safe(node && node.title).trim() || safe(loopCtx.selectedNodeId).trim() || '-';
    const roundText =
      node && Object.prototype.hasOwnProperty.call(node, 'round_index')
        ? '第 ' + safe(node.round_index) + ' 轮'
        : '-';
    const decisionText = safe(node && node.decision).trim() || '暂无判定';
    const nextActionText = safe(node && node.next_action).trim() || '暂无下一步动作';
    const impactText = safe(node && node.impact).trim() || '暂无本轮处理说明';
    const metrics = node && node.metrics && typeof node.metrics === 'object' ? node.metrics : {};
    const metricsText =
      node && node.metrics_available
        ? 'Avg=' +
          safe(trainingLoopScoreText(metrics.avg_score, '-')) +
          ' / Threshold=' +
          safe(trainingLoopScoreText(metrics.threshold, '-')) +
          ' / Previous=' +
          safe(trainingLoopScoreText(metrics.previous_avg_score, '无'))
        : '暂无评分或阈值' +
          (safe(node && node.metrics_unavailable_reason).trim()
            ? '（' + safe(node.metrics_unavailable_reason) + '）'
            : loopCtx.metricsReason
              ? '（' + safe(loopCtx.metricsReason) + '）'
              : '');
    const actionQueueTaskId =
      safe(node && node.queue_task_id).trim() || safe(queueRow && queueRow.queue_task_id).trim();
    const availableActions = Array.isArray(node && node.available_actions)
      ? node.available_actions.map((item) => safe(item).trim())
      : [];
    const canEnterNextRound = !!(isCurrent && actionQueueTaskId && availableActions.includes('enter-next-round'));
    const canRollbackRound = !!(isCurrent && actionQueueTaskId && availableActions.includes('rollback-round-increment'));
    const actionEnabled = canEnterNextRound || canRollbackRound;

    const execLabel = trainingExecutionEngineLabel(
      (detailCtx.overview && detailCtx.overview.execution_engine) || (queueRow && queueRow.execution_engine)
    );
    const nodeTypeKey = safe(node && node.node_type).toLowerCase();
    const nodeStatusKey = safe(node && node.status).toLowerCase();
    const kindText =
      nodeTypeKey === 'rollback' ? '回退动作' : nodeStatusKey === 'rolled_back' ? '回退分支' : '主线节点';
    let deltaText = '保留主线继续';
    if (nodeTypeKey === 'rollback') deltaText = '本轮新增已撤销';
    else if (nodeStatusKey === 'rolled_back') deltaText = '当前轮已回退';
    else if (!isCurrent) deltaText = '历史节点';

    const stageIndex = trainingLoopStageIndex('status', queueRow);
    const stageTitle = safe(TC_LOOP_STAGES[stageIndex - 1] && TC_LOOP_STAGES[stageIndex - 1].title).trim();
    const noteText =
      kindText +
      ' · ' +
      roundText +
      (stageTitle ? ' · ' + stageTitle : '') +
      (isCurrent ? ' · 当前活动' : '') +
      (loopCtx.isTestData ? ' · 测试数据' : '');
    const decisionLabel = statusText(decisionText);
    const actionMeaning =
      nodeTypeKey === 'rollback' || nodeStatusKey === 'rolled_back'
        ? '该动作会在演进图追加一个回退节点，并把当前轮标记为已回退；不会删除已有主线历史。'
        : '当前轮仍保留在主线中，可继续进入下一轮补强工作集。';
    const actionHelp = actionEnabled
      ? '动作开关由后端判定结果控制；当前只允许执行后端返回的可用动作。'
      : '仅当前活动节点可执行动作。';

    box.innerHTML =
      "<div class='tc-loop-decision-card'>" +
      "<div class='tc-loop-right-title'>当前选中节点</div>" +
      "<div class='tc-loop-right-big'>" +
      safe(nodeTitle) +
      '</div>' +
      "<div class='tc-loop-right-sub'>" +
      safe(noteText) +
      '</div>' +
      "<div class='tc-loop-decision-delta'>" +
      safe(deltaText) +
      '</div>' +
      "<div class='tc-loop-summary-list' style='margin-top:10px'>" +
      [
        ['节点得分', metricsText],
        ['节点结论', decisionLabel],
        ['关联影响', impactText],
        ['执行主体', execLabel || 'workflow 内建训练能力'],
      ]
        .map(
          (pair) =>
            "<div class='tc-loop-summary-item'><div class='tc-loop-summary-k'>" +
            safe(pair[0]) +
            "</div><div class='tc-loop-summary-v'>" +
            safe(pair[1]) +
            '</div></div>'
        )
        .join('') +
      '</div>' +
      '</div>' +
      "<div class='tc-loop-next-card'>" +
      "<div class='tc-loop-next-title'>节点判定与下一步</div>" +
      renderTrainingLoopSummaryRows([
        ['下一步动作', nextActionText],
        ['本轮处理说明', impactText],
        ['动作含义', actionMeaning],
        ['loop_id', loopCtx.loopId],
      ]) +
      "<div class='tc-loop-action-row'>" +
      "<button id='tcLoopEnterNextRoundBtn' class='alt' type='button' " +
      (canEnterNextRound ? '' : 'disabled') +
      '>进入下一轮</button>' +
      "<button id='tcLoopRollbackRoundBtn' class='alt' type='button' " +
      (canRollbackRound ? '' : 'disabled') +
      '>撤销本轮新增</button>' +
      '</div>' +
      "<div class='tc-loop-action-help'>" +
      safe(actionHelp) +
      '</div>' +
      '</div>';

    const enterBtn = $('tcLoopEnterNextRoundBtn');
    if (enterBtn) {
      enterBtn.onclick = () => {
        if (enterBtn.disabled) return;
        enterBtn.disabled = true;
        postJSON('/api/training/queue/' + encodeURIComponent(actionQueueTaskId) + '/loop/enter-next-round', {
          operator: 'web-user',
          reason: '',
        })
          .then(async (data) => {
            setTrainingCenterRunResult(data);
            const nextQueueTaskId = safe(data.created_queue_task_id || data.current_node_id).trim();
            const nextNodeId = safe(data.current_node_id).trim();
            if (nextQueueTaskId) {
              state.tcLoopSelectedQueueTaskId = nextQueueTaskId;
              state.tcLoopSelectedNodeId = nextNodeId || nextQueueTaskId;
              state.tcLoopMode = 'status';
              state.tcLoopStatusTab = 'overview';
              await refreshTrainingCenterQueue(true);
              await refreshTrainingLoopServerData(nextQueueTaskId, { force: true });
            } else {
              await refreshTrainingLoopServerData(actionQueueTaskId, { force: true });
            }
          })
          .catch((err) => {
            setTrainingCenterRunResult(err && err.data ? err.data : { ok: false, error: safe(err && err.message ? err.message : err) });
          })
          .finally(() => {
            renderTrainingLoop();
          });
      };
    }

    const rollbackBtn = $('tcLoopRollbackRoundBtn');
    if (rollbackBtn) {
      rollbackBtn.onclick = () => {
        if (rollbackBtn.disabled) return;
        rollbackBtn.disabled = true;
        postJSON('/api/training/queue/' + encodeURIComponent(actionQueueTaskId) + '/loop/rollback-round-increment', {
          operator: 'web-user',
          reason: '',
        })
          .then(async (data) => {
            setTrainingCenterRunResult(data);
            const nextNodeId = safe(data.current_node_id || data.rollback_node_id).trim();
            if (nextNodeId) state.tcLoopSelectedNodeId = nextNodeId;
            await refreshTrainingLoopServerData(actionQueueTaskId, { force: true });
          })
          .catch((err) => {
            setTrainingCenterRunResult(err && err.data ? err.data : { ok: false, error: safe(err && err.message ? err.message : err) });
          })
          .finally(() => {
            renderTrainingLoop();
          });
      };
    }
  }

  function renderTrainingLoopModeFrames(mode) {
    const view = normalizeTrainingLoopMode(mode);
    const moduleOps = $('tcModuleOps');
    if (moduleOps) moduleOps.setAttribute('data-loop-mode', view);
    const rightColumn = $('tcLoopRightColumn');
    if (rightColumn) {
      rightColumn.classList.toggle('active', view === 'status');
      rightColumn.setAttribute('aria-hidden', view === 'status' ? 'false' : 'true');
    }
    ensureTrainingLoopRightWheelBinding();
  }

  function applyTrainingLoopQueryScrollPosition() {
    const target = safe(queryParam('tc_loop_scroll')).trim().toLowerCase();
    if (!target) return;
    const node = $('tcLoopCenterPane');
    if (!node) return;
    window.requestAnimationFrame(() => {
      if (target === 'bottom') {
        node.scrollTop = node.scrollHeight;
      } else {
        node.scrollTop = 0;
      }
    });
  }

  function ensureTrainingLoopRightWheelBinding() {
    const column = $('tcLoopRightColumn');
    if (!column || column.dataset.wheelBound === '1') return;
    column.dataset.wheelBound = '1';
    column.addEventListener(
      'wheel',
      (event) => {
        if (event.ctrlKey || !(event.target instanceof Element)) return;
        const deltaY = Number(event.deltaY || 0);
        if (!Number.isFinite(deltaY) || deltaY === 0) return;
        const hoverTarget = event.target.closest('#tcRunResult, #tcLoopRightPane');
        const candidates = [];
        if (hoverTarget) {
          candidates.push(hoverTarget);
        } else {
          const rightPane = $('tcLoopRightPane');
          const runResult = $('tcRunResult');
          if (rightPane) candidates.push(rightPane);
          if (runResult) candidates.push(runResult);
        }
        const scrollTarget = candidates.find((node) => node && node.scrollHeight > node.clientHeight + 1);
        if (!scrollTarget) return;
        const maxTop = Math.max(0, scrollTarget.scrollHeight - scrollTarget.clientHeight);
        const before = scrollTarget.scrollTop;
        const next = Math.max(0, Math.min(maxTop, before + deltaY));
        if (next === before) return;
        scrollTarget.scrollTop = next;
        event.preventDefault();
      },
      { passive: false }
    );
  }

  function renderTrainingLoop() {
    if (!state.tcLoopQueryApplied) {
      const forcedMode = safe(queryParam('tc_loop_mode')).toLowerCase();
      if (forcedMode === 'create' || forcedMode === 'status') {
        state.tcLoopMode = forcedMode;
      }
      const forcedSearch = safe(queryParam('tc_loop_search')).trim();
      if (forcedSearch && $('tcLoopTaskSearchInput')) {
        $('tcLoopTaskSearchInput').value = forcedSearch;
      }
      const forcedNode = safe(queryParam('tc_loop_node')).trim();
      if (forcedNode) {
        state.tcLoopSelectedNodeId = forcedNode;
      }
      const forcedTask = safe(queryParam('tc_loop_task')).trim();
      if (forcedTask) {
        state.tcLoopSelectedQueueTaskId = forcedTask;
        if (forcedMode !== 'create') {
          state.tcLoopMode = 'status';
        }
      }
      const forcedTab = safe(queryParam('tc_loop_tab')).toLowerCase();
      if (normalizeTrainingLoopMode(state.tcLoopMode) === 'create') {
        state.tcLoopCreateTab = normalizeTrainingLoopCreateTab(forcedTab);
      } else {
        state.tcLoopStatusTab = normalizeTrainingLoopStatusTab(forcedTab);
      }
      state.tcLoopQueryApplied = true;
    }

    const mode = normalizeTrainingLoopMode(state.tcLoopMode);
    ensureTrainingLoopSelection(mode);
    renderTrainingLoopModeFrames(mode);
    const row = mode === 'status' ? selectedTrainingLoopQueueRow() : null;
    let loopPayload = null;
    let statusDetailPayload = null;
    if (mode === 'status') {
      const qid = safe(row && row.queue_task_id).trim() || safe(state.tcLoopSelectedQueueTaskId).trim();
      if (qid) {
        const same = safe(state.tcLoopServerQueueTaskId).trim() === qid;
        if (
          !same ||
          ((!state.tcLoopServerData || !state.tcLoopStatusDetailData) &&
            !state.tcLoopServerLoading &&
            !state.tcLoopServerError)
        ) {
          refreshTrainingLoopServerData(qid).catch((err) => {
            state.tcLoopServerLoading = false;
            state.tcLoopServerError = safe(err && err.message ? err.message : err);
            renderTrainingLoop();
          });
        }
        loopPayload = same ? state.tcLoopServerData : null;
        statusDetailPayload = same ? state.tcLoopStatusDetailData : null;
      }
    }
    renderTrainingLoopProcessCard(mode, row, loopPayload);
    renderTrainingLoopDetailFrame(mode, row, loopPayload, statusDetailPayload);
    renderTrainingLoopRightPane(mode, row, loopPayload, statusDetailPayload);
    updateTrainingCenterOpsGateState();
    applyTrainingLoopQueryScrollPosition();
  }
