  const ASSIGNMENT_HISTORY_BATCH = 12;
  const ASSIGNMENT_PRIORITY_LEVELS = ['P0', 'P1', 'P2', 'P3'];
  const ASSIGNMENT_BEIJING_TIMEZONE = 'Asia/Shanghai';
  const ASSIGNMENT_BEIJING_FORMATTER = typeof Intl !== 'undefined' && Intl.DateTimeFormat
    ? new Intl.DateTimeFormat('zh-CN', {
      timeZone: ASSIGNMENT_BEIJING_TIMEZONE,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    })
    : null;

  function escapeHtml(value) {
    return safe(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function defaultAssignmentCreateForm() {
    return {
      node_name: '',
      assigned_agent_id: '',
      priority: 'P1',
      node_goal: '',
      expected_artifact: '',
      delivery_mode: 'none',
      delivery_receiver_agent_id: '',
    };
  }

  function resetAssignmentCreateForm() {
    state.assignmentCreateForm = defaultAssignmentCreateForm();
    state.assignmentCreateSelectedUpstreamIds = [];
    state.assignmentCreateUpstreamSearch = '';
    state.assignmentDrawerError = '';
  }

  function selectedAssignmentTicketId() {
    return safe(state.assignmentSelectedTicketId).trim();
  }

  function selectedAssignmentGraphOverview() {
    const data = state.assignmentGraphData && typeof state.assignmentGraphData === 'object'
      ? state.assignmentGraphData
      : {};
    return data.graph && typeof data.graph === 'object' ? data.graph : null;
  }

  function assignmentNodeCatalog() {
    const data = state.assignmentGraphData && typeof state.assignmentGraphData === 'object'
      ? state.assignmentGraphData
      : {};
    return Array.isArray(data.node_catalog) ? data.node_catalog : [];
  }

  function assignmentDetailPayload() {
    return state.assignmentDetail && typeof state.assignmentDetail === 'object'
      ? state.assignmentDetail
      : {};
  }

  function assignmentMetricsSummary() {
    const overview = selectedAssignmentGraphOverview();
    if (overview && overview.metrics_summary && typeof overview.metrics_summary === 'object') {
      return overview.metrics_summary;
    }
    const data = state.assignmentGraphData && typeof state.assignmentGraphData === 'object'
      ? state.assignmentGraphData
      : {};
    return data.metrics_summary && typeof data.metrics_summary === 'object'
      ? data.metrics_summary
      : {};
  }

  function assignmentHasNodes() {
    return Number(assignmentMetricsSummary().total_nodes || 0) > 0;
  }

  function selectedAssignmentNode() {
    const detail = assignmentDetailPayload();
    return detail.selected_node && typeof detail.selected_node === 'object'
      ? detail.selected_node
      : {};
  }

  function setAssignmentError(text) {
    state.assignmentError = safe(text);
    const node = $('assignmentGraphError');
    if (node) node.textContent = state.assignmentError;
  }

  function setAssignmentDetailError(text) {
    state.assignmentDetailError = safe(text);
    const node = $('assignmentDetailError');
    if (node) node.textContent = state.assignmentDetailError;
  }

  function setAssignmentDrawerError(text) {
    state.assignmentDrawerError = safe(text);
    const node = $('assignmentDrawerError');
    if (node) node.textContent = state.assignmentDrawerError;
  }

  function assignmentStatusTone(value) {
    const key = safe(value).trim().toLowerCase();
    if (key === 'running') return 'running';
    if (key === 'failed') return 'fail';
    if (key === 'blocked') return 'blocked';
    if (key === 'succeeded') return 'done';
    return 'future';
  }

  function assignmentSchedulerTone(value) {
    const key = safe(value).trim().toLowerCase();
    if (key === 'running') return 'running';
    if (key === 'pause_pending') return 'pause_pending';
    if (key === 'paused') return 'paused';
    return 'idle';
  }

  function assignmentSchedulerDisplayState(schedulerState, runningNodeCount) {
    const key = safe(schedulerState).trim().toLowerCase();
    const runningCount = Math.max(0, Number(runningNodeCount || 0));
    if (key === 'pause_pending') {
      return {
        tone: runningCount > 0 ? 'pause_pending' : 'paused',
        text: runningCount > 0 ? '暂停中' : '已暂停',
        title: runningCount > 0 ? '当前仍有任务收尾，结束后会自动暂停。' : '调度器已暂停。',
      };
    }
    if (key === 'paused') {
      return { tone: 'paused', text: '已暂停', title: '调度器已暂停。' };
    }
    if (key === 'running') {
      return runningCount > 0
        ? { tone: 'running', text: '运行中', title: '当前有任务正在执行。' }
        : { tone: 'idle', text: '空闲', title: '调度器已开启，当前无运行中任务。' };
    }
    return { tone: 'idle', text: '未启动', title: '调度器未启动。' };
  }

  function assignmentPriorityLabel(value) {
    const text = safe(value).trim().toUpperCase();
    if (ASSIGNMENT_PRIORITY_LEVELS.includes(text)) return text;
    const num = Number.parseInt(text, 10);
    if (Number.isFinite(num) && num >= 0 && num <= 3) return 'P' + String(num);
    return 'P1';
  }

  function assignmentNodeSort(a, b, orderIndex) {
    const statusA = safe(a && a.status).trim().toLowerCase();
    const statusB = safe(b && b.status).trim().toLowerCase();
    const executedA = ['running', 'succeeded', 'failed'].includes(statusA) ? 0 : 1;
    const executedB = ['running', 'succeeded', 'failed'].includes(statusB) ? 0 : 1;
    if (executedA !== executedB) return executedA - executedB;
    const priorityDiff = Number(a && a.priority) - Number(b && b.priority);
    if (priorityDiff !== 0) return priorityDiff;
    const timeA = safe((a && a.completed_at) || (a && a.created_at));
    const timeB = safe((b && b.completed_at) || (b && b.created_at));
    if (timeA !== timeB) {
      return timeA < timeB ? -1 : 1;
    }
    if (orderIndex) {
      const indexA = Number(orderIndex[safe(a && a.node_id).trim()]);
      const indexB = Number(orderIndex[safe(b && b.node_id).trim()]);
      if (Number.isFinite(indexA) && Number.isFinite(indexB) && indexA !== indexB) {
        return indexA - indexB;
      }
    }
    return safe(a && a.node_id).localeCompare(safe(b && b.node_id));
  }

  function assignmentFormatBeijingTimeParts(value) {
    const raw = safe(value).trim();
    if (!raw) {
      return {
        dateText: '',
        timeText: '',
        fullText: '-',
      };
    }
    const dt = new Date(raw);
    if (Number.isNaN(dt.getTime()) || !ASSIGNMENT_BEIJING_FORMATTER || typeof ASSIGNMENT_BEIJING_FORMATTER.formatToParts !== 'function') {
      return {
        dateText: raw,
        timeText: '',
        fullText: raw,
      };
    }
    const partMap = {};
    ASSIGNMENT_BEIJING_FORMATTER.formatToParts(dt).forEach((part) => {
      if (part && part.type && part.type !== 'literal') {
        partMap[part.type] = safe(part.value);
      }
    });
    const dateText = [
      safe(partMap.year),
      safe(partMap.month),
      safe(partMap.day),
    ].filter(Boolean).join('-');
    const timeText = [
      safe(partMap.hour),
      safe(partMap.minute),
      safe(partMap.second),
    ].filter(Boolean).join(':');
    const fullText = [dateText, timeText].filter(Boolean).join(' ') + ' 北京时间';
    return {
      dateText: dateText || raw,
      timeText: timeText || '',
      fullText: fullText.trim() || raw,
    };
  }

  function assignmentFormatBeijingTime(value) {
    return assignmentFormatBeijingTimeParts(value).fullText;
  }

  function assignmentDeliveryModeText(value) {
    return safe(value).trim().toLowerCase() === 'specified' ? '指定交付人' : '无交付人';
  }

  function assignmentArtifactDeliveryStatusText(value) {
    return safe(value).trim().toLowerCase() === 'delivered' ? '已交付' : '待交付';
  }

  function assignmentSafePathSegment(value, fallback) {
    let text = safe(value).trim();
    if (!text) text = safe(fallback).trim() || 'item';
    text = text.replace(/[<>:"/\\|?*\x00-\x1f]+/g, '_').replace(/\s+/g, ' ').trim().replace(/[. ]+$/g, '');
    return text || 'item';
  }

  function assignmentAgentLabelById(agentId) {
    const target = safe(agentId).trim();
    const rows = Array.isArray(state.tcAgents) ? state.tcAgents : [];
    const matched = rows.find((item) => safe(item && item.agent_id).trim() === target);
    return safe((matched && (matched.agent_name || matched.agent_id)) || target).trim();
  }

  function assignmentCreatePreviewPaths() {
    const form = state.assignmentCreateForm || defaultAssignmentCreateForm();
    const artifactRoot = safe(state.artifactRootPath).trim();
    if (!artifactRoot) return ['-'];
    const ticketId = selectedAssignmentTicketId() || '<ticket_id>';
    const nodeId = '<node_id>';
    const paths = [artifactRoot + '/tasks/' + ticketId + '/artifacts/' + nodeId + '/output/...'];
    if (safe(form.delivery_mode).trim().toLowerCase() === 'specified') {
      const receiver = assignmentSafePathSegment(
        assignmentAgentLabelById(form.delivery_receiver_agent_id) || form.delivery_receiver_agent_id || 'receiver',
        'receiver',
      );
      paths.push(
        artifactRoot + '/tasks/' + ticketId + '/artifacts/' + nodeId + '/delivery/' + receiver + '/...',
      );
    }
    return paths;
  }

  function assignmentCompareNodeLabel(a, b, nodeMeta, orderIndex) {
    const metaA = nodeMeta[a] || {};
    const metaB = nodeMeta[b] || {};
    const nameA = safe(metaA.node_name).trim();
    const nameB = safe(metaB.node_name).trim();
    if (nameA && nameB && nameA !== nameB) {
      return nameA.localeCompare(nameB, 'zh-CN', { numeric: true, sensitivity: 'base' });
    }
    return assignmentCompareNodeOrder(a, b, orderIndex);
  }

  function assignmentCompareNodeOrder(a, b, orderIndex) {
    const indexA = Number(orderIndex[a]);
    const indexB = Number(orderIndex[b]);
    if (indexA !== indexB) {
      return indexA - indexB;
    }
    return safe(a).localeCompare(safe(b));
  }

  function assignmentBuildNodeOrderIndex(nodes, nodeCatalog) {
    const orderIndex = {};
    const orderedRows = Array.isArray(nodeCatalog) && nodeCatalog.length ? nodeCatalog : nodes;
    orderedRows.forEach((node, index) => {
      const nodeId = safe(node && node.node_id).trim();
      if (nodeId && !Object.prototype.hasOwnProperty.call(orderIndex, nodeId)) {
        orderIndex[nodeId] = index;
      }
    });
    nodes.forEach((node, index) => {
      const nodeId = safe(node && node.node_id).trim();
      if (nodeId && !Object.prototype.hasOwnProperty.call(orderIndex, nodeId)) {
        orderIndex[nodeId] = orderedRows.length + index;
      }
    });
    return orderIndex;
  }

  function assignmentClampLane(value) {
    const lane = Number(value);
    if (!Number.isFinite(lane)) return 0.44;
    return Math.max(0.04, Math.min(0.94, lane));
  }

  function assignmentRootLaneAnchor(index) {
    const preferred = [0.44, 0.82, 0.78, 0.12, 0.86, 0.12, 0.88, 0.1, 0.22, 0.94, 0.04, 0.66, 0.32];
    if (index < preferred.length) {
      return preferred[index];
    }
    const overflow = index - preferred.length;
    const band = 0.38 + Math.floor(overflow / 2) * 0.08;
    const direction = overflow % 2 === 0 ? 1 : -1;
    return assignmentClampLane(0.44 + direction * band);
  }

  function assignmentSiblingLaneOffset(count, index) {
    if (count <= 1) return 0;
    if (count === 2) {
      return index === 0 ? -0.18 : 0.22;
    }
    const totalSpan = Math.min(0.56, 0.2 * (count - 1));
    const step = totalSpan / Math.max(1, count - 1);
    return -totalSpan / 2 + step * index;
  }

  function assignmentComputeLanes(nodes, edges, orderIndexOverride) {
    const nodeIds = nodes.map((node) => safe(node && node.node_id).trim()).filter(Boolean);
    const orderIndex = orderIndexOverride && typeof orderIndexOverride === 'object'
      ? orderIndexOverride
      : {};
    const nodeMeta = {};
    nodes.forEach((node, index) => {
      const nodeId = safe(node && node.node_id).trim();
      if (!Object.prototype.hasOwnProperty.call(orderIndex, nodeId)) {
        orderIndex[nodeId] = index;
      }
      nodeMeta[nodeId] = node || {};
    });
    const parentMap = {};
    const childMap = {};
    const indegree = {};
    nodeIds.forEach((id) => {
      parentMap[id] = [];
      childMap[id] = [];
      indegree[id] = 0;
    });
    (edges || []).forEach((edge) => {
      const fromId = safe(edge && edge.from_node_id).trim();
      const toId = safe(edge && edge.to_node_id).trim();
      if (!fromId || !toId || !Object.prototype.hasOwnProperty.call(indegree, fromId) || !Object.prototype.hasOwnProperty.call(indegree, toId)) {
        return;
      }
      if (!childMap[fromId].includes(toId)) {
        childMap[fromId].push(toId);
      }
      if (!parentMap[toId].includes(fromId)) {
        parentMap[toId].push(fromId);
        indegree[toId] += 1;
      }
    });
    nodeIds.forEach((id) => {
      parentMap[id].sort((a, b) => assignmentCompareNodeLabel(a, b, nodeMeta, orderIndex));
      childMap[id].sort((a, b) => assignmentCompareNodeLabel(a, b, nodeMeta, orderIndex));
    });
    const topo = [];
    const queue = nodeIds
      .filter((id) => indegree[id] === 0)
      .sort((a, b) => assignmentCompareNodeOrder(a, b, orderIndex));
    while (queue.length) {
      const current = queue.shift();
      topo.push(current);
      childMap[current].forEach((nextId) => {
        indegree[nextId] -= 1;
        if (indegree[nextId] === 0) {
          queue.push(nextId);
          queue.sort((a, b) => assignmentCompareNodeOrder(a, b, orderIndex));
        }
      });
    }
    nodeIds.forEach((id) => {
      if (!topo.includes(id)) {
        topo.push(id);
      }
    });
    const roots = topo
      .filter((id) => parentMap[id].length === 0)
      .sort((a, b) => assignmentCompareNodeOrder(a, b, orderIndex));
    const laneMap = {};
    roots.forEach((id, index) => {
      laneMap[id] = assignmentRootLaneAnchor(index);
    });
    topo.forEach((id) => {
      if (Object.prototype.hasOwnProperty.call(laneMap, id)) {
        return;
      }
      const parentIds = parentMap[id];
      if (!parentIds.length) {
        laneMap[id] = 0.44;
        return;
      }
      if (parentIds.length > 1) {
        const total = parentIds.reduce((sum, parentId) => sum + assignmentClampLane(laneMap[parentId]), 0);
        laneMap[id] = assignmentClampLane(total / parentIds.length);
        return;
      }
      const parentId = parentIds[0];
      const siblingIds = childMap[parentId];
      const siblingIndex = siblingIds.indexOf(id);
      laneMap[id] = assignmentClampLane(
        assignmentClampLane(laneMap[parentId]) + assignmentSiblingLaneOffset(siblingIds.length, siblingIndex),
      );
    });
    const reverseTopo = [...topo].reverse();
    for (let pass = 0; pass < 2; pass += 1) {
      reverseTopo.forEach((id) => {
        if (roots.includes(id)) {
          return;
        }
        const parentIds = parentMap[id];
        const childIds = childMap[id];
        if (
          parentIds.length === 1 &&
          childIds.length === 1 &&
          childMap[parentIds[0]].length === 1 &&
          parentMap[childIds[0]].length === 1
        ) {
          const parentLane = assignmentClampLane(laneMap[parentIds[0]]);
          const childLane = assignmentClampLane(laneMap[childIds[0]]);
          laneMap[id] = assignmentClampLane((laneMap[id] + ((parentLane + childLane) / 2)) / 2);
        } else if (parentIds.length > 1) {
          const total = parentIds.reduce((sum, parentId) => sum + assignmentClampLane(laneMap[parentId]), 0);
          laneMap[id] = assignmentClampLane((laneMap[id] + (total / parentIds.length)) / 2);
        }
      });
    }
    nodeIds.forEach((id) => {
      laneMap[id] = assignmentClampLane(laneMap[id]);
    });
    return laneMap;
  }

  function assignmentComputeVerticalNodes(nodes, edges, orderIndexOverride) {
    const nodeIds = nodes.map((node) => safe(node && node.node_id).trim()).filter(Boolean);
    const nodeMap = {};
    const orderIndex = orderIndexOverride && typeof orderIndexOverride === 'object'
      ? orderIndexOverride
      : {};
    const indegree = {};
    const childMap = {};
    nodes.forEach((node, index) => {
      const nodeId = safe(node && node.node_id).trim();
      nodeMap[nodeId] = node;
      if (!Object.prototype.hasOwnProperty.call(orderIndex, nodeId)) {
        orderIndex[nodeId] = index;
      }
      indegree[nodeId] = 0;
      childMap[nodeId] = [];
    });
    (edges || []).forEach((edge) => {
      const fromId = safe(edge && edge.from_node_id).trim();
      const toId = safe(edge && edge.to_node_id).trim();
      if (!fromId || !toId || !Object.prototype.hasOwnProperty.call(indegree, fromId) || !Object.prototype.hasOwnProperty.call(indegree, toId)) {
        return;
      }
      childMap[fromId].push(toId);
      indegree[toId] += 1;
    });
    Object.keys(childMap).forEach((id) => {
      childMap[id].sort((a, b) => assignmentCompareNodeOrder(a, b, orderIndex));
    });
    const queue = nodeIds
      .filter((id) => indegree[id] === 0)
      .sort((a, b) => assignmentCompareNodeOrder(a, b, orderIndex));
    const orderedIds = [];
    while (queue.length) {
      const currentId = queue.shift();
      orderedIds.push(currentId);
      childMap[currentId].forEach((nextId) => {
        indegree[nextId] -= 1;
        if (indegree[nextId] === 0) {
          queue.push(nextId);
          queue.sort((a, b) => assignmentCompareNodeOrder(a, b, orderIndex));
        }
      });
    }
    nodeIds.forEach((id) => {
      if (!orderedIds.includes(id)) {
        orderedIds.push(id);
      }
    });
    return orderedIds.map((id) => nodeMap[id]).filter(Boolean);
  }

  function assignmentBuildPath(from, to) {
    const startY = from.y + 18;
    const endY = to.y - 18;
    const deltaY = Math.max(70, Math.abs(endY - startY));
    const deltaX = to.x - from.x;
    const direction = deltaX < 0 ? -1 : 1;
    const lateral = Math.max(28, Math.min(84, Math.round(Math.max(Math.abs(deltaX), 52) * 0.34)));
    const curve = Math.max(48, Math.round(deltaY * 0.38));
    const startControlX = from.x + (deltaX === 0 ? direction * Math.round(lateral * 0.55) : Math.round(deltaX * 0.18));
    const endControlX = to.x - direction * lateral;
    return [
      'M', from.x, startY,
      'C', startControlX, startY + curve,
      endControlX, endY - curve,
      to.x, endY,
    ].join(' ');
  }

  function assignmentGraphMarkerId(tone) {
    return 'assignment-graph-arrow-' + safe(tone).trim().toLowerCase();
  }

  function assignmentGraphStroke(tone) {
    return '#c6ccd6';
  }

  function assignmentNodeStatusMeta(node) {
    const status = safe(node && node.status).trim().toLowerCase();
    const tone = assignmentStatusTone(status);
    const text = safe(node && node.status_text).trim() || (tone === 'done' ? '已完成' : tone === 'running' ? '进行中' : tone === 'blocked' ? '阻塞' : tone === 'fail' ? '失败' : '待开始');
    return { tone: tone, text: text };
  }

  function renderAssignmentScheduler() {
    const overview = selectedAssignmentGraphOverview();
    const scheduler = overview && overview.scheduler && typeof overview.scheduler === 'object'
      ? overview.scheduler
      : {};
    const schedulerState = safe((overview && overview.scheduler_state) || scheduler.state || 'idle').trim().toLowerCase();
    const rootReady = !!state.agentSearchRootReady;
    const hasNodes = assignmentHasNodes();
    const stateChip = $('assignmentSchedulerStateChip');
    const parallelChip = $('assignmentParallelCountChip');
    const note = $('assignmentHeaderNote');
    const pauseBtn = $('assignmentPauseBtn');
    const resumeBtn = $('assignmentResumeBtn');
    const clearBtn = $('assignmentClearBtn');
    const runningNodeCount = Math.max(
      0,
      Number(scheduler.graph_running_node_count || (assignmentMetricsSummary().status_counts || {}).running || 0),
    );
    const displayState = assignmentSchedulerDisplayState(schedulerState || 'idle', runningNodeCount);
    const isEffectivelyRunning = displayState.tone === 'running' || displayState.tone === 'pause_pending';
    const canResumeFromIdle = ['idle', 'paused'].includes(schedulerState) || (schedulerState === 'running' && runningNodeCount <= 0);
    if (stateChip) {
      stateChip.className = 'assignment-chip ' + assignmentSchedulerTone(displayState.tone);
      stateChip.textContent = displayState.text;
      stateChip.title = displayState.title;
    }
    if (parallelChip) {
      parallelChip.className = 'assignment-chip muted';
      parallelChip.textContent = '并行agent数 ' + String(Number(scheduler.running_agent_count || 0));
    }
    if (note) {
      if (!overview) {
        note.textContent = state.agentSearchRootReady
          ? '按依赖关系与优先级展示当前任务图。'
          : 'agent路径未设置或无效，任务中心功能已锁定。';
      } else {
        const summary = safe(overview.summary).trim();
        const graphName = safe(overview.graph_name).trim();
        const testSuffix = overview.is_test_data ? ' · 测试数据' : '';
        note.textContent = (graphName ? graphName + testSuffix + ' · ' : '') + (summary || '按依赖关系与优先级展示当前任务图。');
      }
    }
    if (pauseBtn) {
      const disabled = !rootReady || !hasNodes || !!state.assignmentLoading || !isEffectivelyRunning;
      pauseBtn.disabled = disabled;
      pauseBtn.title = !hasNodes
        ? '暂无任务可调度'
        : (!isEffectivelyRunning ? '当前没有运行中的任务' : '');
    }
    if (resumeBtn) {
      const disabled =
        !rootReady ||
        !hasNodes ||
        !!state.assignmentLoading ||
        !canResumeFromIdle;
      resumeBtn.disabled = disabled;
      resumeBtn.title = !hasNodes
        ? '暂无任务可调度'
        : (!canResumeFromIdle ? '当前已有任务在运行' : '');
    }
    if (clearBtn) {
      const disabled = !rootReady || !hasNodes || !!state.assignmentLoading || runningNodeCount > 0;
      clearBtn.disabled = disabled;
      clearBtn.title = runningNodeCount > 0
        ? '存在运行中任务，不可清空'
        : (!hasNodes ? '暂无任务可清空' : '');
    }
  }

  function renderAssignmentGraphMeta() {
    const metaNode = $('assignmentGraphMeta');
    const historyChip = $('assignmentHistoryChip');
    const loadBtn = $('assignmentLoadHistoryBtn');
    const data = state.assignmentGraphData && typeof state.assignmentGraphData === 'object'
      ? state.assignmentGraphData
      : {};
    const metrics = data.metrics_summary && typeof data.metrics_summary === 'object'
      ? data.metrics_summary
      : {};
    const history = data.history && typeof data.history === 'object'
      ? data.history
      : {};
    if (metaNode) {
      if (!selectedAssignmentGraphOverview()) {
        metaNode.textContent = '暂无任务图';
      } else {
        metaNode.textContent =
          '总任务 ' + String(Number(metrics.total_nodes || 0)) +
          ' · 已执行 ' + String(Number(metrics.executed_count || 0)) +
          ' · 待开始 ' + String(Number(metrics.unexecuted_count || 0));
      }
    }
    if (historyChip) {
      const remaining = Number(history.remaining_completed_count || 0);
      const loaded = Number(history.loaded_extra_count || 0);
      historyChip.className = 'assignment-history-chip' +
        (state.assignmentLoading ? ' loading' : remaining <= 0 && loaded > 0 ? ' loaded' : '');
      if (!selectedAssignmentGraphOverview()) {
        historyChip.textContent = '历史未加载';
      } else if (state.assignmentLoading) {
        historyChip.textContent = '正在刷新任务图';
      } else if (remaining > 0) {
        historyChip.textContent = '可继续加载历史 ' + String(remaining);
      } else if (loaded > 0) {
        historyChip.textContent = '历史已全部加载';
      } else {
        historyChip.textContent = '当前无需加载历史';
      }
    }
    if (loadBtn) {
      loadBtn.disabled = !state.agentSearchRootReady || !selectedAssignmentTicketId() || !history.has_more;
      loadBtn.textContent = history.has_more
        ? '加载历史'
        : '历史已加载';
    }
  }

  function renderAssignmentGraph() {
    const graphData = state.assignmentGraphData && typeof state.assignmentGraphData === 'object'
      ? state.assignmentGraphData
      : {};
    const layoutNodes = Array.isArray(graphData.nodes) ? [...graphData.nodes] : [];
    const edges = Array.isArray(graphData.edges) ? [...graphData.edges] : [];
    const emptyState = $('assignmentEmptyState');
    const stage = $('assignmentGraphStage');
    const timeColumn = $('assignmentTimeColumn');
    const svg = $('assignmentGraphSvg');
    if (!timeColumn || !svg || !stage) return;
    renderAssignmentGraphMeta();
    const orderIndex = assignmentBuildNodeOrderIndex(layoutNodes, graphData.node_catalog);
    const nodes = assignmentComputeVerticalNodes(layoutNodes, edges, orderIndex);
    if (!nodes.length) {
      if (emptyState) emptyState.classList.remove('hidden');
      stage.style.height = '280px';
      timeColumn.innerHTML = '';
      svg.innerHTML = '';
      return;
    }
    if (emptyState) emptyState.classList.add('hidden');
    const lanes = assignmentComputeLanes(layoutNodes, edges, orderIndex);
    const firstRowY = 110;
    const rowGap = 110;
    const stageHeight = Math.max(320, firstRowY + Math.max(0, nodes.length - 1) * rowGap + 120);
    const canvasWidth = Math.max(760, (svg.parentElement ? svg.parentElement.clientWidth : 0) - 12);
    const leftPad = 46;
    const rightPad = 180;
    const laneSpan = Math.max(1, canvasWidth - leftPad - (2 * leftPad));
    stage.style.height = String(stageHeight) + 'px';
    svg.setAttribute('width', String(canvasWidth));
    svg.setAttribute('height', String(stageHeight));
    svg.setAttribute('viewBox', '0 0 ' + String(canvasWidth) + ' ' + String(stageHeight));
    svg.style.width = String(canvasWidth) + 'px';
    svg.style.height = String(stageHeight) + 'px';
    timeColumn.innerHTML = '';
    svg.innerHTML = '';
    const defs = createSvgElement('defs', {});
    ['done', 'running', 'blocked', 'fail', 'future'].forEach((tone) => {
      const marker = createSvgElement('marker', {
        id: assignmentGraphMarkerId(tone),
        markerWidth: '8',
        markerHeight: '7',
        refX: '7',
        refY: '3.5',
        orient: 'auto',
        markerUnits: 'strokeWidth',
      });
      const arrow = createSvgElement('path', {
        d: 'M1,1 L7,3.5 L1,6 C2.1,4.7 2.1,2.3 1,1 z',
        fill: assignmentGraphStroke(tone),
      });
      marker.appendChild(arrow);
      defs.appendChild(marker);
    });
    svg.appendChild(defs);
    const positions = {};
    const entryNodes = {};
    const circleNodes = {};
    nodes.forEach((node, index) => {
      const nodeId = safe(node && node.node_id).trim();
      const lane = assignmentClampLane(lanes[nodeId]);
      let x = leftPad + lane * laneSpan;
      x = Math.max(72, Math.min(canvasWidth - rightPad, x));
      const y = firstRowY + index * rowGap;
      positions[nodeId] = { x: x, y: y };
      const entry = document.createElement('div');
      entry.className = 'assignment-time-entry' + (safe(node.completed_at).trim() ? '' : ' pending');
      entry.style.top = String(y - 18) + 'px';
      const ts = safe(node.completed_at).trim();
      const completedAt = assignmentFormatBeijingTimeParts(ts);
      const dateText = ts ? completedAt.dateText : '待完成';
      const clockText = ts ? (completedAt.timeText || '--:--:--') : '--:--:--';
      entry.innerHTML =
        "<span class='assignment-time-date'>" + escapeHtml(dateText) + "</span>" +
        "<span class='assignment-time-clock'>" + escapeHtml(clockText) + '</span>';
      entry.title = ts ? completedAt.fullText : '待完成';
      timeColumn.appendChild(entry);
      entryNodes[nodeId] = entry;
    });
    edges.forEach((edge) => {
      const fromId = safe(edge && edge.from_node_id).trim();
      const toId = safe(edge && edge.to_node_id).trim();
      if (!positions[fromId] || !positions[toId]) return;
      const target = nodes.find((item) => safe(item && item.node_id).trim() === toId) || {};
      const lineTone = assignmentStatusTone(target.status);
      const line = createSvgElement('path', {
        class: 'assignment-graph-line ' + lineTone,
        d: assignmentBuildPath(positions[fromId], positions[toId]),
        'marker-end': 'url(#' + assignmentGraphMarkerId(lineTone) + ')',
      });
      svg.appendChild(line);
    });
    nodes.forEach((node) => {
      const nodeId = safe(node && node.node_id).trim();
      const pos = positions[nodeId];
      if (!pos) return;
      const group = createSvgElement('g', {
        class: 'assignment-node-group' + (nodeId === safe(state.assignmentSelectedNodeId).trim() ? ' selected' : ''),
        'data-node-id': nodeId,
      });
      const tone = assignmentStatusTone(node.status);
      const circle = createSvgElement('circle', {
        class: 'assignment-node-circle ' + tone,
        cx: String(pos.x),
        cy: String(pos.y),
        r: '18',
      });
      const label = createSvgElement('text', {
        class: 'assignment-node-label',
        x: String(pos.x + 34),
        y: String(pos.y - 3),
      });
      label.textContent = safe(node.node_name || node.node_id);
      const sub = createSvgElement('text', {
        class: 'assignment-node-sub',
        x: String(pos.x + 34),
        y: String(pos.y + 15),
      });
      sub.textContent = assignmentPriorityLabel(node.priority) + ' · ' + safe(node.assigned_agent_name || node.assigned_agent_id);
      group.appendChild(circle);
      group.appendChild(label);
      group.appendChild(sub);
      svg.appendChild(group);
      circleNodes[nodeId] = circle;
    });
    const stageRect = stage.getBoundingClientRect();
    nodes.forEach((node) => {
      const nodeId = safe(node && node.node_id).trim();
      const entry = entryNodes[nodeId];
      const circle = circleNodes[nodeId];
      if (!entry || !circle) return;
      const circleRect = circle.getBoundingClientRect();
      if (!circleRect || !Number.isFinite(circleRect.top) || !Number.isFinite(circleRect.bottom)) return;
      const centerY = (circleRect.top + circleRect.bottom) / 2;
      entry.style.top = String(centerY - stageRect.top - 18) + 'px';
    });
  }

  function assignmentExecutionChainPayload() {
    const detail = assignmentDetailPayload();
    return detail.execution_chain && typeof detail.execution_chain === 'object'
      ? detail.execution_chain
      : {};
  }

  function assignmentExecutionLatestRun(chain) {
    const payload = chain && typeof chain === 'object' ? chain : assignmentExecutionChainPayload();
    return payload.latest_run && typeof payload.latest_run === 'object'
      ? payload.latest_run
      : {};
  }
