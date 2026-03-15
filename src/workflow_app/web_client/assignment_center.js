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
    const taskName = assignmentSafePathSegment(form.node_name || '任务', '任务');
    const worker = assignmentSafePathSegment(
      assignmentAgentLabelById(form.assigned_agent_id) || form.assigned_agent_id || 'agent',
      'agent',
    );
    const paths = [artifactRoot + '/' + worker + '/product/' + taskName + '/...'];
    if (safe(form.delivery_mode).trim().toLowerCase() === 'specified') {
      const receiver = assignmentSafePathSegment(
        assignmentAgentLabelById(form.delivery_receiver_agent_id) || form.delivery_receiver_agent_id || 'receiver',
        'receiver',
      );
      paths.push(artifactRoot + '/' + receiver + '/receive/' + taskName + '/...');
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
    const stateText = safe((overview && overview.scheduler_state_text) || scheduler.state_text || '未启动');
    const stateKey = assignmentSchedulerTone(schedulerState || 'idle');
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
    if (stateChip) {
      stateChip.className = 'assignment-chip ' + stateKey;
      stateChip.textContent = stateText;
    }
    if (parallelChip) {
      parallelChip.className = 'assignment-chip muted';
      parallelChip.textContent = '并行agent数 ' + String(Number(scheduler.running_agent_count || 0));
    }
    if (note) {
      if (!overview) {
        note.textContent = state.agentSearchRootReady
          ? '按依赖关系与优先级展示当前任务图。'
          : 'agent_search_root 未设置或无效，任务中心功能已锁定。';
      } else {
        const summary = safe(overview.summary).trim();
        const graphName = safe(overview.graph_name).trim();
        const testSuffix = overview.is_test_data ? ' · 测试数据' : '';
        note.textContent = (graphName ? graphName + testSuffix + ' · ' : '') + (summary || '按依赖关系与优先级展示当前任务图。');
      }
    }
    if (pauseBtn) {
      const disabled = !rootReady || !hasNodes || !!state.assignmentLoading || schedulerState !== 'running';
      pauseBtn.disabled = disabled;
      pauseBtn.title = !hasNodes ? '暂无任务可调度' : '';
    }
    if (resumeBtn) {
      const disabled =
        !rootReady ||
        !hasNodes ||
        !!state.assignmentLoading ||
        !['idle', 'paused'].includes(schedulerState);
      resumeBtn.disabled = disabled;
      resumeBtn.title = !hasNodes ? '暂无任务可调度' : '';
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

  function renderAssignmentDetail() {
    const body = $('assignmentDetailBody');
    if (!body) return;
    const detail = assignmentDetailPayload();
    const selected = selectedAssignmentNode();
    const metaNode = $('assignmentDetailMeta');
    if (!safe(selected.node_id).trim()) {
      if (metaNode) metaNode.textContent = '请选择任务节点';
      body.innerHTML =
        "<div class='assignment-detail-card'>" +
        "<div class='assignment-empty-title'>暂无任务详情</div>" +
        "<div class='hint'>点击任务图中的节点后，在这里查看执行主体、上下游、回执、产物与任务管理动作。</div>" +
        '</div>';
      return;
    }
    if (metaNode) metaNode.textContent = '当前选中 ' + safe(selected.node_name || selected.node_id);
    const statusMeta = assignmentNodeStatusMeta(selected);
    const upstream = Array.isArray(selected.upstream_nodes) ? selected.upstream_nodes : [];
    const downstream = Array.isArray(selected.downstream_nodes) ? selected.downstream_nodes : [];
    const availableActions = Array.isArray(detail.available_actions)
      ? detail.available_actions.map((item) => safe(item).trim().toLowerCase())
      : [];
    const audits = Array.isArray(detail.audit_refs)
      ? detail.audit_refs.filter((item) => {
        const action = safe(item && item.action).trim().toLowerCase();
        return action === 'rerun' || action === 'override_status' || action === 'deliver_artifact';
      })
      : [];
    const blockings = Array.isArray(detail.blocking_reasons) ? detail.blocking_reasons : [];
    const artifactPaths = Array.isArray(selected.artifact_paths) ? selected.artifact_paths : [];
    const chips = (rows) => rows.length
      ? rows.map((item) => "<span class='assignment-token'>" + escapeHtml(safe(item.node_name || item.node_id)) + '</span>').join('')
      : "<span class='hint'>-</span>";
    const rawStatus = safe(selected.status).trim().toLowerCase();
    let receiptActionHtml = '';
    let managementHtml = '';
    if (statusMeta.tone === 'running') {
      receiptActionHtml =
        "<div class='assignment-detail-card'>" +
        "<div class='card-title'>回执</div>" +
        "<div class='assignment-action-form'>" +
        "<textarea id='assignmentReceiptReason' rows='4' placeholder='请填写成功/失败理由（必填）'></textarea>" +
        "<input id='assignmentReceiptRef' type='text' placeholder='结果引用（选填，仅成功时使用）' />" +
        "<div class='assignment-action-row'>" +
        "<button id='assignmentMarkSuccessBtn' type='button'>标记成功</button>" +
        "<button id='assignmentMarkFailedBtn' class='bad' type='button'>标记失败</button>" +
        '</div></div></div>';
    }
    if (availableActions.includes('override-status')) {
      managementHtml =
        "<div class='assignment-detail-card'>" +
        "<div class='card-title'>任务管理</div>" +
        "<div class='assignment-action-form'>" +
        "<input id='assignmentOverrideReason' type='text' placeholder='人工修改执行状态时必须填写理由' />" +
        "<select id='assignmentOverrideStatus'>" +
        "<option value='ready'>改为待开始</option>" +
        "<option value='pending'>改为 pending</option>" +
        "<option value='blocked'>改为阻塞</option>" +
        "<option value='succeeded'>改为已完成</option>" +
        "<option value='failed'>保持失败</option>" +
        "</select>" +
        "<div class='assignment-action-row'>" +
        (availableActions.includes('rerun') ? "<button id='assignmentRerunBtn' class='alt' type='button'>重跑任务</button>" : '') +
        "<button id='assignmentOverrideBtn' type='button'>人工修改执行状态</button>" +
        (availableActions.includes('delete') ? "<button id='assignmentDeleteBtn' class='bad' type='button'>删除任务</button>" : '') +
        '</div></div></div>';
    } else if (rawStatus === 'running') {
      managementHtml =
        "<div class='assignment-detail-card'>" +
        "<div class='card-title'>任务管理</div>" +
        "<div class='assignment-action-form'>" +
        "<div class='hint'>运行中的任务不可删除，请先完成状态回写。</div>" +
        "<div class='assignment-action-row'>" +
        "<button id='assignmentDeleteBtn' class='bad' type='button' disabled>删除任务</button>" +
        '</div></div></div>';
    } else {
      managementHtml =
        "<div class='assignment-detail-card'>" +
        "<div class='card-title'>任务管理</div>" +
        "<div class='assignment-action-form'>" +
        "<div class='hint'>当前任务支持删除；若位于依赖链中间，系统会自动桥接其上下游。</div>" +
        "<div class='assignment-action-row'>" +
        (availableActions.includes('delete') ? "<button id='assignmentDeleteBtn' class='bad' type='button'>删除任务</button>" : '') +
        '</div></div></div>';
    }
    const artifactActionHtml =
      "<div class='assignment-action-form'>" +
      "<input id='assignmentArtifactLabelInput' type='text' placeholder='产物名称（选填，默认使用预期产物或任务名称）' />" +
      "<textarea id='assignmentArtifactNoteInput' rows='4' placeholder='交付说明（选填）'></textarea>" +
      "<div class='assignment-action-row'>" +
      "<button id='assignmentDeliverBtn' class='alt' type='button'>" +
      (safe(selected.artifact_delivery_status).trim().toLowerCase() === 'delivered' ? '重新交付产物' : '提交产物') +
      "</button>" +
      "<button id='assignmentViewArtifactBtn' type='button'" + (artifactPaths.length ? '>' : ' disabled>') + '查看产物</button>' +
      '</div></div>';
    body.innerHTML =
      "<div class='assignment-detail-card'>" +
      "<div class='assignment-detail-top'>" +
      "<div><div class='hint'>选中任务</div><div class='assignment-detail-name'>" + escapeHtml(safe(selected.node_name)) + '</div></div>' +
      "<span class='assignment-chip " + statusMeta.tone + "'>" + escapeHtml(statusMeta.text) + '</span>' +
      '</div>' +
      "<div class='assignment-detail-grid'>" +
      "<div class='assignment-stat'><div class='assignment-stat-k'>执行 agent</div><div class='assignment-stat-v'>" + escapeHtml(safe(selected.assigned_agent_name || selected.assigned_agent_id)) + '</div></div>' +
      "<div class='assignment-stat'><div class='assignment-stat-k'>优先级</div><div class='assignment-stat-v'>" + escapeHtml(assignmentPriorityLabel(selected.priority)) + '</div></div>' +
      "<div class='assignment-stat'><div class='assignment-stat-k'>上游任务</div><div class='assignment-stat-v'>" + chips(upstream) + '</div></div>' +
      "<div class='assignment-stat'><div class='assignment-stat-k'>下游任务</div><div class='assignment-stat-v'>" + chips(downstream) + '</div></div>' +
      "<div class='assignment-stat'><div class='assignment-stat-k'>确认任务目标</div><div class='assignment-stat-v'>" + escapeHtml(safe(selected.node_goal)) + '</div></div>' +
      "<div class='assignment-stat'><div class='assignment-stat-k'>完成时间</div><div class='assignment-stat-v'>" + escapeHtml(safe(selected.completed_at) ? assignmentFormatBeijingTime(selected.completed_at) : '-') + '</div></div>' +
      '</div></div>' +
      "<div class='assignment-detail-card'>" +
      "<div class='card-title'>回执</div>" +
      "<div class='assignment-detail-grid'>" +
      "<div class='assignment-stat'><div class='assignment-stat-k'>预期产物</div><div class='assignment-stat-v'>" + escapeHtml(safe(selected.expected_artifact) || '-') + '</div></div>' +
      "<div class='assignment-stat'><div class='assignment-stat-k'>结果引用</div><div class='assignment-stat-v'>" + escapeHtml(safe(selected.result_ref) || '-') + '</div></div>' +
      "<div class='assignment-stat'><div class='assignment-stat-k'>成功理由</div><div class='assignment-stat-v'>" + escapeHtml(safe(selected.success_reason) || '-') + '</div></div>' +
      "<div class='assignment-stat'><div class='assignment-stat-k'>失败原因</div><div class='assignment-stat-v'>" + escapeHtml(safe(selected.failure_reason) || '-') + '</div></div>' +
      '</div></div>' +
      "<div class='assignment-detail-card'>" +
      "<div class='card-title'>产物</div>" +
      "<div class='assignment-detail-grid'>" +
      "<div class='assignment-stat'><div class='assignment-stat-k'>产物状态</div><div class='assignment-stat-v'>" + escapeHtml(safe(selected.artifact_delivery_status_text) || assignmentArtifactDeliveryStatusText(selected.artifact_delivery_status)) + '</div></div>' +
      "<div class='assignment-stat'><div class='assignment-stat-k'>交付类型</div><div class='assignment-stat-v'>" + escapeHtml(safe(selected.delivery_mode_text) || assignmentDeliveryModeText(selected.delivery_mode)) + '</div></div>' +
      "<div class='assignment-stat'><div class='assignment-stat-k'>交付对象</div><div class='assignment-stat-v'>" + escapeHtml(safe(selected.delivery_receiver_agent_name || selected.delivery_receiver_agent_id) || '-') + '</div></div>' +
      "<div class='assignment-stat'><div class='assignment-stat-k'>最近交付时间</div><div class='assignment-stat-v'>" + escapeHtml(safe(selected.artifact_delivered_at) ? assignmentFormatBeijingTime(selected.artifact_delivered_at) : '-') + '</div></div>' +
      '</div>' +
      "<div class='assignment-path-list'>" +
      (artifactPaths.length
        ? artifactPaths.map((item) => "<div class='assignment-path-item'>" + escapeHtml(safe(item)) + '</div>').join('')
        : "<div class='assignment-path-item'>尚未交付，路径将在提交产物后生成。</div>") +
      '</div>' +
      artifactActionHtml +
      '</div>' +
      (blockings.length
        ? "<div class='assignment-detail-card'><div class='card-title'>阻塞来源</div><div class='assignment-audit-list'>" +
          blockings.map((item) => "<div class='assignment-audit-item'>" + escapeHtml(safe(item.node_name)) + ' · ' + escapeHtml(safe(item.status_text)) + '</div>').join('') +
          '</div></div>'
        : '') +
      receiptActionHtml +
      managementHtml +
      (audits.length
        ? "<div class='assignment-detail-card'>" +
          "<div class='card-title'>人工处置留痕</div>" +
          "<div class='assignment-audit-list'>" +
          audits.map((item) => "<div class='assignment-audit-item'>" +
            escapeHtml(assignmentFormatBeijingTime(item.created_at)) + '\n' +
            escapeHtml(safe(item.action)) + ' · ' + escapeHtml(safe(item.reason || '-')) + '\n' +
            escapeHtml(safe(item.ref || '-')) +
            '</div>').join('') +
          '</div></div>'
        : '');
  }

  function renderAssignmentAgentOptions() {
    const select = $('assignmentAgentSelect');
    const receiverSelect = $('assignmentDeliveryReceiverSelect');
    if (!select) return;
    const items = Array.isArray(state.tcAgents) ? state.tcAgents : [];
    const current = safe(state.assignmentCreateForm.assigned_agent_id).trim();
    const currentReceiver = safe(state.assignmentCreateForm.delivery_receiver_agent_id).trim();
    let html = '';
    if (!items.length) {
      html = "<option value=''>暂无可用角色</option>";
    } else {
      html = items
        .map((item) => {
          const agentId = safe(item && item.agent_id).trim();
          const agentName = safe(item && item.agent_name).trim();
          return "<option value='" + escapeHtml(agentId) + "'" +
            (agentId === current ? ' selected' : '') +
            '>' + escapeHtml(agentName || agentId) + '</option>';
        })
        .join('');
    }
    select.innerHTML = html;
    if (!current && items.length) {
      state.assignmentCreateForm.assigned_agent_id = safe(items[0].agent_id).trim();
      select.value = state.assignmentCreateForm.assigned_agent_id;
    }
    if (receiverSelect) {
      receiverSelect.innerHTML = items.length
        ? ("<option value=''>请选择交付对象</option>" + items.map((item) => {
          const agentId = safe(item && item.agent_id).trim();
          const agentName = safe(item && item.agent_name).trim();
          return "<option value='" + escapeHtml(agentId) + "'" +
            (agentId === currentReceiver ? ' selected' : '') +
            '>' + escapeHtml(agentName || agentId) + '</option>';
        }).join(''))
        : "<option value=''>暂无可用角色</option>";
      receiverSelect.value = currentReceiver;
    }
  }

  function renderAssignmentUpstreamResults() {
    const resultNode = $('assignmentUpstreamResults');
    if (!resultNode) return;
    const catalog = assignmentNodeCatalog();
    const query = safe(state.assignmentCreateUpstreamSearch).trim().toLowerCase();
    const selectedIds = new Set(state.assignmentCreateSelectedUpstreamIds || []);
    const rows = catalog
      .filter((item) => !selectedIds.has(safe(item && item.node_id).trim()))
      .filter((item) => {
        if (!query) return true;
        const hay = (
          safe(item && item.node_name) + ' ' +
          safe(item && item.node_id)
        ).toLowerCase();
        return hay.includes(query);
      })
      .slice(0, 8);
    if (!rows.length) {
      resultNode.innerHTML = "<div class='hint'>暂无可添加的上游任务</div>";
      return;
    }
    resultNode.innerHTML = rows.map((item) => {
      const nodeId = safe(item && item.node_id).trim();
      const status = safe(item && item.status_text ? item.status_text : statusText(item && item.status)).trim() || '-';
      return (
        "<div class='assignment-search-item'>" +
        "<div>" +
        "<div class='assignment-search-item-title'>" + escapeHtml(safe(item && item.node_name)) + "</div>" +
        "<div class='assignment-search-item-meta'>" + escapeHtml(nodeId + ' · ' + status) + '</div>' +
        "</div>" +
        "<button class='alt' type='button' data-assignment-upstream-add='" + escapeHtml(nodeId) + "'>添加</button>" +
        '</div>'
      );
    }).join('');
  }

  function renderAssignmentSelectedUpstreams() {
    const node = $('assignmentSelectedUpstreams');
    if (!node) return;
    const catalog = assignmentNodeCatalog();
    const selectedIds = Array.isArray(state.assignmentCreateSelectedUpstreamIds)
      ? state.assignmentCreateSelectedUpstreamIds
      : [];
    if (!selectedIds.length) {
      node.innerHTML = "<div class='hint'>未选择上游任务</div>";
      return;
    }
    node.innerHTML = selectedIds.map((nodeId) => {
      const matched = catalog.find((item) => safe(item && item.node_id).trim() === safe(nodeId).trim()) || {};
      const label = safe(matched.node_name || nodeId).trim();
      return (
        "<span class='assignment-token'>" +
        "<span>" + escapeHtml(label) + '</span>' +
        "<button type='button' data-assignment-upstream-remove='" + escapeHtml(nodeId) + "'>×</button>" +
        '</span>'
      );
    }).join('');
  }

  function renderAssignmentPathPreview() {
    const pathPreview = $('assignmentPathPreview');
    const receiverField = $('assignmentDeliveryReceiverField');
    if (receiverField) {
      receiverField.style.display = safe(state.assignmentCreateForm.delivery_mode).trim().toLowerCase() === 'specified' ? 'flex' : 'none';
    }
    if (pathPreview) {
      pathPreview.innerHTML = assignmentCreatePreviewPaths().map((item) => escapeHtml(item)).join('<br/>');
    }
  }

  function renderAssignmentDrawer() {
    const mask = $('assignmentDrawerMask');
    if (mask) {
      mask.classList.toggle('hidden', !state.assignmentCreateOpen);
    }
    renderAssignmentAgentOptions();
    const nameInput = $('assignmentTaskNameInput');
    const goalInput = $('assignmentGoalInput');
    const artifactInput = $('assignmentArtifactInput');
    const agentSelect = $('assignmentAgentSelect');
    const prioritySelect = $('assignmentPrioritySelect');
    const deliveryModeSelect = $('assignmentDeliveryModeSelect');
    const receiverField = $('assignmentDeliveryReceiverField');
    const receiverSelect = $('assignmentDeliveryReceiverSelect');
    const searchInput = $('assignmentUpstreamSearch');
    if (nameInput) nameInput.value = safe(state.assignmentCreateForm.node_name);
    if (goalInput) goalInput.value = safe(state.assignmentCreateForm.node_goal);
    if (artifactInput) artifactInput.value = safe(state.assignmentCreateForm.expected_artifact);
    if (agentSelect) agentSelect.value = safe(state.assignmentCreateForm.assigned_agent_id);
    if (prioritySelect) prioritySelect.value = assignmentPriorityLabel(state.assignmentCreateForm.priority);
    if (deliveryModeSelect) deliveryModeSelect.value = safe(state.assignmentCreateForm.delivery_mode || 'none').trim() || 'none';
    if (receiverSelect) receiverSelect.value = safe(state.assignmentCreateForm.delivery_receiver_agent_id).trim();
    if (receiverField) {
      receiverField.style.display = safe(state.assignmentCreateForm.delivery_mode).trim().toLowerCase() === 'specified' ? 'flex' : 'none';
    }
    renderAssignmentPathPreview();
    if (searchInput) searchInput.value = safe(state.assignmentCreateUpstreamSearch);
    renderAssignmentUpstreamResults();
    renderAssignmentSelectedUpstreams();
    setAssignmentDrawerError(state.assignmentDrawerError || '');
  }

  function renderAssignmentCenter() {
    renderAssignmentScheduler();
    renderAssignmentGraph();
    renderAssignmentDetail();
    renderAssignmentDrawer();
    setAssignmentError(state.assignmentError || '');
    setAssignmentDetailError(state.assignmentDetailError || '');
  }

  async function ensureAssignmentAgentPool(forceRefresh) {
    const force = !!forceRefresh;
    if (!force && Array.isArray(state.tcAgents) && state.tcAgents.length) {
      renderAssignmentAgentOptions();
      return state.tcAgents;
    }
    const data = await getJSON(withTestDataQuery('/api/training/agents'));
    state.tcAgents = Array.isArray(data.items) ? data.items : [];
    state.tcStats = data.stats && typeof data.stats === 'object' ? data.stats : state.tcStats;
    if (typeof syncTrainingCenterPlanAgentOptions === 'function') {
      syncTrainingCenterPlanAgentOptions();
    }
    renderAssignmentAgentOptions();
    return state.tcAgents;
  }

  function assignmentDefaultCreatePayload() {
    return {
      graph_name: '任务中心主图',
      source_workflow: 'workflow-ui',
      summary: '任务中心手动创建',
      review_mode: 'none',
    };
  }

  async function ensureAssignmentGraphExists() {
    const existing = selectedAssignmentTicketId();
    if (existing) return existing;
    const created = await postJSON('/api/assignments', assignmentDefaultCreatePayload());
    state.assignmentSelectedTicketId = safe(created.ticket_id).trim();
    state.assignmentHistoryLoaded = 0;
    await refreshAssignmentGraphs({ preserveSelection: true });
    return selectedAssignmentTicketId();
  }

  async function ensureAssignmentPrototypeTestData() {
    return postJSON('/api/assignments/test-data/bootstrap', {
      operator: 'web-user',
    });
  }

  function assignmentGraphUrl(ticketId) {
    return withTestDataQuery('/api/assignments/' + encodeURIComponent(ticketId) +
      '/graph?history_loaded=' + encodeURIComponent(String(Number(state.assignmentHistoryLoaded || 0))) +
      '&history_batch_size=' + encodeURIComponent(String(ASSIGNMENT_HISTORY_BATCH)));
  }

  function pickAssignmentDefaultNode(graphData) {
    const rows = Array.isArray(graphData && graphData.nodes) ? graphData.nodes : [];
    const preferred = rows.find((item) => safe(item && item.status).trim().toLowerCase() === 'running') ||
      rows.find((item) => safe(item && item.status).trim().toLowerCase() === 'failed') ||
      rows[0];
    return safe(preferred && preferred.node_id).trim();
  }

  async function refreshAssignmentDetail(nodeId) {
    const ticketId = selectedAssignmentTicketId();
    if (!ticketId) {
      state.assignmentDetail = null;
      state.assignmentSelectedNodeId = '';
      renderAssignmentDetail();
      return null;
    }
    const targetNodeId = safe(nodeId || state.assignmentSelectedNodeId).trim();
    const seq = Number(state.assignmentDetailRequestSeq || 0) + 1;
    state.assignmentDetailRequestSeq = seq;
    const url = withTestDataQuery('/api/assignments/' + encodeURIComponent(ticketId) +
      '/status-detail?node_id=' + encodeURIComponent(targetNodeId));
    const data = await getJSON(url);
    if (seq !== state.assignmentDetailRequestSeq) return null;
    state.assignmentDetail = data;
    state.assignmentSelectedNodeId = safe(data && data.selected_node && data.selected_node.node_id).trim();
    setAssignmentDetailError('');
    renderAssignmentDetail();
    renderAssignmentGraph();
    return data;
  }

  async function refreshAssignmentGraphData(options) {
    const opts = options || {};
    const ticketId = safe(opts.ticketId || state.assignmentSelectedTicketId).trim();
    if (!ticketId) {
      state.assignmentGraphData = null;
      state.assignmentScheduler = null;
      renderAssignmentCenter();
      return null;
    }
    const seq = Number(state.assignmentGraphRequestSeq || 0) + 1;
    state.assignmentGraphRequestSeq = seq;
    state.assignmentLoading = true;
    renderAssignmentCenter();
    try {
      const data = await getJSON(assignmentGraphUrl(ticketId));
      if (seq !== state.assignmentGraphRequestSeq) return null;
      state.assignmentGraphData = data;
      state.assignmentScheduler = data.graph && data.graph.scheduler ? data.graph.scheduler : null;
      state.assignmentSelectedTicketId = ticketId;
      if (!safe(state.assignmentSelectedNodeId).trim()) {
        state.assignmentSelectedNodeId = pickAssignmentDefaultNode(data);
      } else {
        const exists = Array.isArray(data.nodes)
          ? data.nodes.some((item) => safe(item && item.node_id).trim() === safe(state.assignmentSelectedNodeId).trim())
          : false;
        if (!exists) {
          state.assignmentSelectedNodeId = pickAssignmentDefaultNode(data);
        }
      }
      setAssignmentError('');
      renderAssignmentCenter();
      await refreshAssignmentDetail(state.assignmentSelectedNodeId);
      return data;
    } finally {
      state.assignmentLoading = false;
      renderAssignmentCenter();
    }
  }

  async function refreshAssignmentGraphs(options) {
    if (!state.agentSearchRootReady) {
      state.assignmentGraphs = [];
      state.assignmentGraphData = null;
      state.assignmentDetail = null;
      state.assignmentSelectedTicketId = '';
      state.assignmentSelectedNodeId = '';
      state.assignmentScheduler = null;
      state.assignmentHistoryLoaded = 0;
      renderAssignmentCenter();
      return { items: [] };
    }
    const opts = options || {};
    const previous = safe(state.assignmentSelectedTicketId).trim();
    const data = await getJSON(withTestDataQuery('/api/assignments'));
    state.assignmentGraphs = Array.isArray(data.items) ? data.items : [];
    const emptyPrototypeGraph = state.assignmentGraphs.find((item) => {
      const metrics = item && item.metrics_summary && typeof item.metrics_summary === 'object'
        ? item.metrics_summary
        : {};
      return !!(item && item.is_test_data) &&
        safe(item && item.external_request_id).trim() === 'task-center-prototype-v1' &&
        Number(metrics.total_nodes || 0) <= 0;
    });
    if (
      !!state.showTestData &&
      !opts.testBootstrapAttempted &&
      (!state.assignmentGraphs.length || (!!emptyPrototypeGraph && state.assignmentGraphs.length === 1))
    ) {
      await ensureAssignmentPrototypeTestData();
      return refreshAssignmentGraphs({
        preserveSelection: !!opts.preserveSelection,
        testBootstrapAttempted: true,
      });
    }
    const selectedExists = state.assignmentGraphs.some((item) => safe(item && item.ticket_id).trim() === previous);
    if (opts.preserveSelection && previous && selectedExists) {
      state.assignmentSelectedTicketId = previous;
    } else if (!selectedExists) {
      state.assignmentSelectedTicketId = state.assignmentGraphs.length
        ? safe(state.assignmentGraphs[0].ticket_id).trim()
        : '';
      state.assignmentHistoryLoaded = 0;
    }
    if (selectedAssignmentTicketId()) {
      return refreshAssignmentGraphData({ ticketId: selectedAssignmentTicketId() });
    }
    state.assignmentGraphData = null;
    state.assignmentDetail = null;
    state.assignmentSelectedNodeId = '';
    renderAssignmentCenter();
    return data;
  }

  async function maybeDispatchAssignmentTicket(ticketId) {
    const tid = safe(ticketId || selectedAssignmentTicketId()).trim();
    if (!tid || !state.agentSearchRootReady) return null;
    await postJSON('/api/assignments/' + encodeURIComponent(tid) + '/dispatch-next', {
      operator: 'web-user',
    });
    return refreshAssignmentGraphData({ ticketId: tid });
  }

  function setAssignmentCreateOpen(nextOpen) {
    state.assignmentCreateOpen = !!nextOpen;
    if (!state.assignmentCreateOpen) {
      resetAssignmentCreateForm();
    }
    if (state.assignmentCreateOpen) {
      ensureAssignmentAgentPool(false).catch((err) => {
        setAssignmentDrawerError(err.message || String(err));
      });
    }
    renderAssignmentDrawer();
  }

  function syncAssignmentCreateFormFromInputs() {
    state.assignmentCreateForm = {
      node_name: safe($('assignmentTaskNameInput') ? $('assignmentTaskNameInput').value : '').trim(),
      assigned_agent_id: safe($('assignmentAgentSelect') ? $('assignmentAgentSelect').value : '').trim(),
      priority: assignmentPriorityLabel($('assignmentPrioritySelect') ? $('assignmentPrioritySelect').value : 'P1'),
      node_goal: safe($('assignmentGoalInput') ? $('assignmentGoalInput').value : '').trim(),
      expected_artifact: safe($('assignmentArtifactInput') ? $('assignmentArtifactInput').value : '').trim(),
      delivery_mode: safe($('assignmentDeliveryModeSelect') ? $('assignmentDeliveryModeSelect').value : 'none').trim() || 'none',
      delivery_receiver_agent_id: safe($('assignmentDeliveryReceiverSelect') ? $('assignmentDeliveryReceiverSelect').value : '').trim(),
    };
    state.assignmentCreateUpstreamSearch = safe($('assignmentUpstreamSearch') ? $('assignmentUpstreamSearch').value : '').trim();
  }

  async function submitAssignmentCreate() {
    syncAssignmentCreateFormFromInputs();
    const form = state.assignmentCreateForm || defaultAssignmentCreateForm();
    if (!safe(form.node_name).trim()) throw new Error('任务名称必填');
    if (!safe(form.assigned_agent_id).trim()) throw new Error('执行 agent 必填');
    if (!safe(form.node_goal).trim()) throw new Error('确认任务目标必填');
    if (safe(form.delivery_mode).trim().toLowerCase() === 'specified' && !safe(form.delivery_receiver_agent_id).trim()) {
      throw new Error('指定交付人时必须选择交付给 agent');
    }
    const ticketId = await ensureAssignmentGraphExists();
    const payload = {
      node_name: form.node_name,
      assigned_agent_id: form.assigned_agent_id,
      priority: assignmentPriorityLabel(form.priority),
      node_goal: form.node_goal,
      expected_artifact: form.expected_artifact,
      delivery_mode: form.delivery_mode,
      delivery_receiver_agent_id: form.delivery_receiver_agent_id,
      upstream_node_ids: Array.isArray(state.assignmentCreateSelectedUpstreamIds)
        ? state.assignmentCreateSelectedUpstreamIds
        : [],
      operator: 'web-user',
    };
    await postJSON('/api/assignments/' + encodeURIComponent(ticketId) + '/nodes', payload);
    setAssignmentCreateOpen(false);
    await refreshAssignmentGraphs({ preserveSelection: true });
    await maybeDispatchAssignmentTicket(ticketId);
    setStatus('任务已创建');
  }

  async function pauseAssignmentSchedulerAction() {
    const ticketId = selectedAssignmentTicketId();
    if (!ticketId) return;
    await postJSON('/api/assignments/' + encodeURIComponent(ticketId) + '/pause', {
      operator: 'web-user',
    });
    await refreshAssignmentGraphData({ ticketId: ticketId });
    setStatus('任务调度已暂停');
  }

  async function resumeAssignmentSchedulerAction() {
    const ticketId = selectedAssignmentTicketId();
    if (!ticketId) return;
    await postJSON('/api/assignments/' + encodeURIComponent(ticketId) + '/resume', {
      operator: 'web-user',
    });
    const dispatchResult = await maybeDispatchAssignmentTicket(ticketId);
    if (!dispatchResult) {
      await refreshAssignmentGraphData({ ticketId: ticketId });
    }
    setStatus('任务调度已恢复');
  }

  async function clearAssignmentGraphAction() {
    const ticketId = selectedAssignmentTicketId();
    if (!ticketId) return;
    const ok = window.confirm(
      '将清空当前任务图中的全部活动任务与依赖边，并保留删除留痕。此操作不可撤销，确认继续？',
    );
    if (!ok) return;
    await postJSON('/api/assignments/' + encodeURIComponent(ticketId) + '/clear', {
      operator: 'web-user',
    });
    state.assignmentSelectedNodeId = '';
    await refreshAssignmentGraphData({ ticketId: ticketId });
    setStatus('当前任务图已清空');
  }

  async function loadMoreAssignmentHistory() {
    const graphData = state.assignmentGraphData && typeof state.assignmentGraphData === 'object'
      ? state.assignmentGraphData
      : {};
    const history = graphData.history && typeof graphData.history === 'object'
      ? graphData.history
      : {};
    if (!history.has_more) return;
    state.assignmentHistoryLoaded = Number(history.next_history_loaded || state.assignmentHistoryLoaded || 0);
    await refreshAssignmentGraphData({ ticketId: selectedAssignmentTicketId() });
  }

  async function deliverSelectedAssignmentArtifact() {
    const selected = selectedAssignmentNode();
    const ticketId = selectedAssignmentTicketId();
    const nodeId = safe(selected.node_id).trim();
    if (!ticketId || !nodeId) return;
    await postJSON(
      '/api/assignments/' + encodeURIComponent(ticketId) + '/nodes/' + encodeURIComponent(nodeId) + '/deliver-artifact',
      {
        artifact_label: safe($('assignmentArtifactLabelInput') ? $('assignmentArtifactLabelInput').value : '').trim(),
        delivery_note: safe($('assignmentArtifactNoteInput') ? $('assignmentArtifactNoteInput').value : '').trim(),
        operator: 'web-user',
      },
    );
    await refreshAssignmentGraphData({ ticketId: ticketId });
    setStatus('产物已提交');
  }

  async function viewSelectedAssignmentArtifact() {
    const selected = selectedAssignmentNode();
    const ticketId = selectedAssignmentTicketId();
    const nodeId = safe(selected.node_id).trim();
    if (!ticketId || !nodeId) return;
    window.open(
      withTestDataQuery('/api/assignments/' + encodeURIComponent(ticketId) + '/nodes/' + encodeURIComponent(nodeId) + '/artifact-preview'),
      '_blank',
      'noopener',
    );
  }

  async function markSelectedAssignmentSuccess() {
    const selected = selectedAssignmentNode();
    const ticketId = selectedAssignmentTicketId();
    const nodeId = safe(selected.node_id).trim();
    const successReason = safe($('assignmentReceiptReason') ? $('assignmentReceiptReason').value : '').trim();
    const resultRef = safe($('assignmentReceiptRef') ? $('assignmentReceiptRef').value : '').trim();
    if (!ticketId || !nodeId) return;
    await postJSON(
      '/api/assignments/' + encodeURIComponent(ticketId) + '/nodes/' + encodeURIComponent(nodeId) + '/mark-success',
      {
        success_reason: successReason,
        result_ref: resultRef,
        operator: 'web-user',
      },
    );
    await refreshAssignmentGraphData({ ticketId: ticketId });
    await maybeDispatchAssignmentTicket(ticketId);
    setStatus('任务已标记成功');
  }

  async function markSelectedAssignmentFailed() {
    const selected = selectedAssignmentNode();
    const ticketId = selectedAssignmentTicketId();
    const nodeId = safe(selected.node_id).trim();
    const failureReason = safe($('assignmentReceiptReason') ? $('assignmentReceiptReason').value : '').trim();
    if (!ticketId || !nodeId) return;
    await postJSON(
      '/api/assignments/' + encodeURIComponent(ticketId) + '/nodes/' + encodeURIComponent(nodeId) + '/mark-failed',
      {
        failure_reason: failureReason,
        operator: 'web-user',
      },
    );
    await refreshAssignmentGraphData({ ticketId: ticketId });
    setStatus('任务已标记失败');
  }

  async function rerunSelectedAssignmentNode() {
    const selected = selectedAssignmentNode();
    const ticketId = selectedAssignmentTicketId();
    const nodeId = safe(selected.node_id).trim();
    if (!ticketId || !nodeId) return;
    await postJSON(
      '/api/assignments/' + encodeURIComponent(ticketId) + '/nodes/' + encodeURIComponent(nodeId) + '/rerun',
      {
        operator: 'web-user',
      },
    );
    await refreshAssignmentGraphData({ ticketId: ticketId });
    await maybeDispatchAssignmentTicket(ticketId);
    setStatus('失败任务已重跑');
  }

  async function overrideSelectedAssignmentNode() {
    const selected = selectedAssignmentNode();
    const ticketId = selectedAssignmentTicketId();
    const nodeId = safe(selected.node_id).trim();
    const targetStatus = safe($('assignmentOverrideStatus') ? $('assignmentOverrideStatus').value : '').trim();
    const reason = safe($('assignmentOverrideReason') ? $('assignmentOverrideReason').value : '').trim();
    if (!ticketId || !nodeId) return;
    await postJSON(
      '/api/assignments/' + encodeURIComponent(ticketId) + '/nodes/' + encodeURIComponent(nodeId) + '/override-status',
      {
        target_status: targetStatus,
        reason: reason,
        operator: 'web-user',
      },
    );
    await refreshAssignmentGraphData({ ticketId: ticketId });
    await maybeDispatchAssignmentTicket(ticketId);
    setStatus('执行状态已人工修改');
  }

  async function deleteSelectedAssignmentNode() {
    const selected = selectedAssignmentNode();
    const ticketId = selectedAssignmentTicketId();
    const nodeId = safe(selected.node_id).trim();
    const nodeName = safe(selected.node_name || selected.node_id).trim();
    if (!ticketId || !nodeId) return;
    const ok = window.confirm(
      '将删除任务“' + nodeName + '”。若它位于依赖链中间，系统会自动桥接原有上下游并保留删除留痕。此操作不可撤销，确认继续？',
    );
    if (!ok) return;
    const data = await deleteJSON(
      '/api/assignments/' + encodeURIComponent(ticketId) + '/nodes/' + encodeURIComponent(nodeId),
      { operator: 'web-user' },
    );
    const schedulerState = safe(data && data.graph_overview && data.graph_overview.scheduler_state).trim().toLowerCase();
    state.assignmentSelectedNodeId = '';
    if (schedulerState === 'running') {
      const dispatchResult = await maybeDispatchAssignmentTicket(ticketId);
      if (!dispatchResult) {
        await refreshAssignmentGraphData({ ticketId: ticketId });
      }
    } else {
      await refreshAssignmentGraphData({ ticketId: ticketId });
    }
    setStatus('任务已删除');
  }

  async function runAssignmentCenterProbe() {
    const output = {
      ts: new Date().toISOString(),
      case: assignmentProbeCase(),
      pass: false,
      error: '',
      active_tab: '',
      show_test_data: !!state.showTestData,
      ticket_id: '',
      graph_name: '',
      graph_is_test_data: false,
      scheduler_state: '',
      total_nodes: 0,
      status_counts: {},
      rendered_node_count: 0,
      running_circle_count: 0,
      selected_node_id: '',
      selected_node_name: '',
      header_note: '',
      graph_meta: '',
      detail_meta: '',
      empty_visible: false,
      pause_disabled: true,
      resume_disabled: true,
      clear_disabled: true,
    };
    const waitMs = (ms) => new Promise((resolve) => window.setTimeout(resolve, ms));
    try {
      switchTab('task-center');
      await refreshAssignmentGraphs({ preserveSelection: true });
      const requestedNodeId = safe(queryParam('assignment_probe_node')).trim();
      if (requestedNodeId && selectedAssignmentTicketId()) {
        state.assignmentSelectedNodeId = requestedNodeId;
        await refreshAssignmentDetail(requestedNodeId);
      }
      const delayMs = Math.max(0, Number(queryParam('assignment_probe_delay_ms') || '720'));
      if (delayMs > 0) {
        await waitMs(delayMs);
      }
      const activeTab = document.querySelector('.tab.active');
      const overview = selectedAssignmentGraphOverview() || {};
      const metrics = assignmentMetricsSummary();
      const selected = selectedAssignmentNode();
      const emptyState = $('assignmentEmptyState');
      output.active_tab = safe(activeTab && activeTab.getAttribute('data-tab')).trim();
      output.show_test_data = !!state.showTestData;
      output.ticket_id = selectedAssignmentTicketId();
      output.graph_name = safe(overview.graph_name).trim();
      output.graph_is_test_data = !!overview.is_test_data;
      output.scheduler_state = safe(overview.scheduler_state).trim().toLowerCase();
      output.total_nodes = Number(metrics.total_nodes || 0);
      output.status_counts = metrics.status_counts && typeof metrics.status_counts === 'object'
        ? metrics.status_counts
        : {};
      output.rendered_node_count = document.querySelectorAll('#assignmentGraphSvg [data-node-id]').length;
      output.running_circle_count = document.querySelectorAll('#assignmentGraphSvg .assignment-node-circle.running').length;
      output.selected_node_id = safe(selected.node_id).trim();
      output.selected_node_name = safe(selected.node_name).trim();
      output.header_note = safe($('assignmentHeaderNote') ? $('assignmentHeaderNote').textContent : '').trim();
      output.graph_meta = safe($('assignmentGraphMeta') ? $('assignmentGraphMeta').textContent : '').trim();
      output.detail_meta = safe($('assignmentDetailMeta') ? $('assignmentDetailMeta').textContent : '').trim();
      output.empty_visible = !!(emptyState && !emptyState.classList.contains('hidden'));
      output.pause_disabled = !!($('assignmentPauseBtn') && $('assignmentPauseBtn').disabled);
      output.resume_disabled = !!($('assignmentResumeBtn') && $('assignmentResumeBtn').disabled);
      output.clear_disabled = !!($('assignmentClearBtn') && $('assignmentClearBtn').disabled);
      if (output.case === 'hidden') {
        output.pass =
          output.active_tab === 'task-center' &&
          !output.ticket_id &&
          output.empty_visible &&
          output.rendered_node_count === 0 &&
          output.pause_disabled &&
          output.resume_disabled &&
          output.clear_disabled;
      } else {
        output.pass =
          output.active_tab === 'task-center' &&
          !!output.ticket_id &&
          output.graph_is_test_data &&
          output.total_nodes >= 20 &&
          output.rendered_node_count >= 12 &&
          output.running_circle_count >= 1 &&
          !!output.selected_node_id &&
          output.header_note.includes('测试数据');
      }
    } catch (err) {
      output.error = safe(err && err.message ? err.message : err);
    }
    const node = ensureAssignmentCenterProbeOutputNode();
    node.textContent = JSON.stringify(output);
    node.setAttribute('data-pass', output.pass ? '1' : '0');
  }

  function bindAssignmentCenterEvents() {
    const graphCanvas = $('assignmentGraphCanvas');
    if (graphCanvas) {
      graphCanvas.addEventListener('click', (event) => {
        const target = event.target;
        if (!(target instanceof Element)) return;
        const group = target.closest('[data-node-id]');
        if (!group) return;
        const nodeId = safe(group.getAttribute('data-node-id')).trim();
        if (!nodeId) return;
        state.assignmentSelectedNodeId = nodeId;
        refreshAssignmentDetail(nodeId).catch((err) => {
          setAssignmentDetailError(err.message || String(err));
        });
      });
    }

    const detailBody = $('assignmentDetailBody');
    if (detailBody) {
      detailBody.addEventListener('click', (event) => {
        const target = event.target;
        if (!(target instanceof Element)) return;
        const id = safe(target.id).trim();
        const run = async (work) => {
          try {
            await work();
            setAssignmentDetailError('');
          } catch (err) {
            setAssignmentDetailError(err.message || String(err));
          }
        };
        if (id === 'assignmentMarkSuccessBtn') {
          run(() => withButtonLock('assignmentMarkSuccessBtn', markSelectedAssignmentSuccess));
        } else if (id === 'assignmentMarkFailedBtn') {
          run(() => withButtonLock('assignmentMarkFailedBtn', markSelectedAssignmentFailed));
        } else if (id === 'assignmentDeliverBtn') {
          run(() => withButtonLock('assignmentDeliverBtn', deliverSelectedAssignmentArtifact));
        } else if (id === 'assignmentViewArtifactBtn') {
          run(() => withButtonLock('assignmentViewArtifactBtn', viewSelectedAssignmentArtifact));
        } else if (id === 'assignmentRerunBtn') {
          run(() => withButtonLock('assignmentRerunBtn', rerunSelectedAssignmentNode));
        } else if (id === 'assignmentOverrideBtn') {
          run(() => withButtonLock('assignmentOverrideBtn', overrideSelectedAssignmentNode));
        } else if (id === 'assignmentDeleteBtn') {
          run(() => withButtonLock('assignmentDeleteBtn', deleteSelectedAssignmentNode));
        }
      });
    }

    const drawerMask = $('assignmentDrawerMask');
    if (drawerMask) {
      drawerMask.addEventListener('click', (event) => {
        if (event.target === drawerMask) {
          setAssignmentCreateOpen(false);
        }
      });
    }

    const resultNode = $('assignmentUpstreamResults');
    if (resultNode) {
      resultNode.addEventListener('click', (event) => {
        const target = event.target;
        if (!(target instanceof Element)) return;
        const button = target.closest('[data-assignment-upstream-add]');
        if (!button) return;
        const nodeId = safe(button.getAttribute('data-assignment-upstream-add')).trim();
        if (!nodeId) return;
        if (!Array.isArray(state.assignmentCreateSelectedUpstreamIds)) {
          state.assignmentCreateSelectedUpstreamIds = [];
        }
        if (!state.assignmentCreateSelectedUpstreamIds.includes(nodeId)) {
          state.assignmentCreateSelectedUpstreamIds.push(nodeId);
        }
        renderAssignmentDrawer();
      });
    }

    const selectedNode = $('assignmentSelectedUpstreams');
    if (selectedNode) {
      selectedNode.addEventListener('click', (event) => {
        const target = event.target;
        if (!(target instanceof Element)) return;
        const button = target.closest('[data-assignment-upstream-remove]');
        if (!button) return;
        const nodeId = safe(button.getAttribute('data-assignment-upstream-remove')).trim();
        state.assignmentCreateSelectedUpstreamIds = (state.assignmentCreateSelectedUpstreamIds || [])
          .filter((item) => safe(item).trim() !== nodeId);
        renderAssignmentDrawer();
      });
    }

    if ($('assignmentCreateBtn')) {
      $('assignmentCreateBtn').onclick = async () => {
        try {
          setAssignmentDrawerError('');
          await ensureAssignmentAgentPool(false);
          setAssignmentCreateOpen(true);
        } catch (err) {
          setAssignmentError(err.message || String(err));
        }
      };
    }
    if ($('assignmentRefreshBtn')) {
      $('assignmentRefreshBtn').onclick = async () => {
        try {
          await withButtonLock('assignmentRefreshBtn', async () => {
            await refreshAssignmentGraphs({ preserveSelection: true });
          });
        } catch (err) {
          setAssignmentError(err.message || String(err));
        }
      };
    }
    if ($('assignmentLoadHistoryBtn')) {
      $('assignmentLoadHistoryBtn').onclick = async () => {
        try {
          await withButtonLock('assignmentLoadHistoryBtn', async () => {
            await loadMoreAssignmentHistory();
          });
        } catch (err) {
          setAssignmentError(err.message || String(err));
        }
      };
    }
    if ($('assignmentPauseBtn')) {
      $('assignmentPauseBtn').onclick = async () => {
        try {
          await withButtonLock('assignmentPauseBtn', pauseAssignmentSchedulerAction);
        } catch (err) {
          setAssignmentError(err.message || String(err));
        }
      };
    }
    if ($('assignmentResumeBtn')) {
      $('assignmentResumeBtn').onclick = async () => {
        try {
          await withButtonLock('assignmentResumeBtn', resumeAssignmentSchedulerAction);
        } catch (err) {
          setAssignmentError(err.message || String(err));
        }
      };
    }
    if ($('assignmentClearBtn')) {
      $('assignmentClearBtn').onclick = async () => {
        try {
          await withButtonLock('assignmentClearBtn', clearAssignmentGraphAction);
        } catch (err) {
          setAssignmentError(err.message || String(err));
        }
      };
    }
    if ($('assignmentDrawerCloseBtn')) {
      $('assignmentDrawerCloseBtn').onclick = () => setAssignmentCreateOpen(false);
    }
    if ($('assignmentDrawerCancelBtn')) {
      $('assignmentDrawerCancelBtn').onclick = () => setAssignmentCreateOpen(false);
    }
    if ($('assignmentDrawerSubmitBtn')) {
      $('assignmentDrawerSubmitBtn').onclick = async () => {
        try {
          await withButtonLock('assignmentDrawerSubmitBtn', submitAssignmentCreate);
        } catch (err) {
          setAssignmentDrawerError(err.message || String(err));
        }
      };
    }
    if ($('assignmentClearUpstreamSearchBtn')) {
      $('assignmentClearUpstreamSearchBtn').onclick = () => {
        state.assignmentCreateUpstreamSearch = '';
        if ($('assignmentUpstreamSearch')) $('assignmentUpstreamSearch').value = '';
        renderAssignmentDrawer();
      };
    }
    if ($('assignmentUpstreamSearch')) {
      $('assignmentUpstreamSearch').addEventListener('input', () => {
        state.assignmentCreateUpstreamSearch = safe($('assignmentUpstreamSearch').value).trim();
        renderAssignmentUpstreamResults();
      });
    }
    if ($('assignmentTaskNameInput')) {
      $('assignmentTaskNameInput').addEventListener('input', () => {
        state.assignmentCreateForm.node_name = safe($('assignmentTaskNameInput').value);
        renderAssignmentPathPreview();
      });
    }
    if ($('assignmentGoalInput')) {
      $('assignmentGoalInput').addEventListener('input', () => {
        state.assignmentCreateForm.node_goal = safe($('assignmentGoalInput').value);
      });
    }
    if ($('assignmentArtifactInput')) {
      $('assignmentArtifactInput').addEventListener('input', () => {
        state.assignmentCreateForm.expected_artifact = safe($('assignmentArtifactInput').value);
        renderAssignmentPathPreview();
      });
    }
    if ($('assignmentAgentSelect')) {
      $('assignmentAgentSelect').addEventListener('change', () => {
        state.assignmentCreateForm.assigned_agent_id = safe($('assignmentAgentSelect').value).trim();
        renderAssignmentPathPreview();
      });
    }
    if ($('assignmentPrioritySelect')) {
      $('assignmentPrioritySelect').addEventListener('change', () => {
        state.assignmentCreateForm.priority = assignmentPriorityLabel($('assignmentPrioritySelect').value);
      });
    }
    if ($('assignmentDeliveryModeSelect')) {
      $('assignmentDeliveryModeSelect').addEventListener('change', () => {
        state.assignmentCreateForm.delivery_mode = safe($('assignmentDeliveryModeSelect').value).trim() || 'none';
        if (safe(state.assignmentCreateForm.delivery_mode).trim().toLowerCase() !== 'specified') {
          state.assignmentCreateForm.delivery_receiver_agent_id = '';
        }
        renderAssignmentPathPreview();
      });
    }
    if ($('assignmentDeliveryReceiverSelect')) {
      $('assignmentDeliveryReceiverSelect').addEventListener('change', () => {
        state.assignmentCreateForm.delivery_receiver_agent_id = safe($('assignmentDeliveryReceiverSelect').value).trim();
        renderAssignmentPathPreview();
      });
    }
  }
