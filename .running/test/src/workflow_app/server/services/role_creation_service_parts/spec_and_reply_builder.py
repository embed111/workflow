def _append_message(
    conn: sqlite3.Connection,
    *,
    session_id: str,
    role: str,
    content: str,
    attachments: list[dict[str, Any]] | None = None,
    message_type: str = "chat",
    meta: dict[str, Any] | None = None,
    created_at: str = "",
) -> dict[str, Any]:
    ts = created_at or _tc_now_text()
    payload = {
        "message_id": _role_creation_message_id(),
        "session_id": session_id,
        "role": str(role or "assistant").strip().lower() or "assistant",
        "content": str(content or ""),
        "attachments": list(attachments or []),
        "message_type": _normalize_message_type(message_type),
        "meta": dict(meta or {}),
        "created_at": ts,
    }
    conn.execute(
        """
        INSERT INTO role_creation_messages (
            message_id,session_id,role,content,attachments_json,message_type,meta_json,created_at
        ) VALUES (?,?,?,?,?,?,?,?)
        """,
        (
            payload["message_id"],
            session_id,
            payload["role"],
            payload["content"],
            _json_dumps(payload["attachments"]),
            payload["message_type"],
            _json_dumps(payload["meta"]),
            payload["created_at"],
        ),
    )
    preview = _message_preview(payload["content"], payload["attachments"])
    conn.execute(
        """
        UPDATE role_creation_sessions
        SET last_message_preview=?,last_message_at=?,updated_at=?
        WHERE session_id=?
        """,
        (preview, payload["created_at"], payload["created_at"], session_id),
    )
    return payload


def _session_messages_texts(messages: list[dict[str, Any]], *, role: str) -> list[str]:
    return [
        str(item.get("content") or "")
        for item in messages
        if str(item.get("role") or "").strip().lower() == role and str(item.get("content") or "").strip()
    ]


def _extract_labeled_values(text: str) -> dict[str, list[str]]:
    mapping = {
        "role_name": {"角色名", "角色名称", "名字", "name", "role_name"},
        "role_goal": {"目标", "角色目标", "职责", "role_goal"},
        "core_capabilities": {"能力", "核心能力", "擅长", "capabilities", "core_capabilities"},
        "boundaries": {"边界", "禁止", "不要做", "boundaries"},
        "applicable_scenarios": {"场景", "适用场景", "适用", "scenarios", "applicable_scenarios"},
        "collaboration_style": {"协作方式", "输出风格", "风格", "协作", "collaboration_style"},
    }
    normalized_labels = {key: {label.lower() for label in labels} for key, labels in mapping.items()}
    out: dict[str, list[str]] = {key: [] for key in mapping}
    for raw_line in str(text or "").splitlines():
        cleaned = re.sub(r"^[\-\*\+\d\.\)\s]+", "", _normalize_text(raw_line, max_len=4000)).strip()
        if not cleaned:
            continue
        for sep in ("：", ":", "="):
            idx = cleaned.find(sep)
            if idx <= 0:
                continue
            key_text = cleaned[:idx].strip().lower()
            value_text = cleaned[idx + 1 :].strip()
            if not value_text:
                continue
            for field, labels in normalized_labels.items():
                if key_text in labels:
                    out[field].append(value_text)
                    break
            break
    return out


def _extract_natural_language_values(text: str) -> dict[str, list[str]]:
    patterns = {
        "role_name": (
            r"(?:角色名|角色名称|名字|名称)\s*(?:是|叫|为|[:：=])\s*([^\n，,。.!！？；;]{2,40})",
            r"(?:让它叫|就叫)\s*([^\n，,。.!！？；;]{2,40})",
        ),
        "role_goal": (
            r"(?:角色目标|目标|职责)\s*(?:是|为|[:：=])\s*([^\n。！？!?]{2,280})",
        ),
        "core_capabilities": (
            r"(?:核心能力|能力|擅长)\s*(?:有|是|为|包括|包含|[:：=])\s*([^\n。！？!?]{2,400})",
        ),
        "boundaries": (
            r"(?:禁止边界|边界|约束)\s*(?:是|为|[:：=])\s*([^\n。！？!?]{2,280})",
            r"((?:不要|不能|禁止|避免|别)[^\n。！？!?]{1,280})",
        ),
        "applicable_scenarios": (
            r"(?:适用场景|场景|适用)\s*(?:是|为|[:：=])\s*([^\n。！？!?]{2,280})",
        ),
        "collaboration_style": (
            r"(?:协作方式|输出风格|风格|协作)\s*(?:是|为|[:：=])\s*([^\n。！？!?]{2,280})",
        ),
    }
    out: dict[str, list[str]] = {key: [] for key in patterns}
    for field, field_patterns in patterns.items():
        for pattern in field_patterns:
            for match in re.finditer(pattern, str(text or ""), flags=re.IGNORECASE):
                candidate = _normalize_text(match.group(1), max_len=400)
                if candidate:
                    out[field].append(candidate)
    return out


def _normalize_role_name_candidate(text: str) -> str:
    candidate = _normalize_text(text, max_len=40).strip().strip("`'\"“”‘’[]()（）{}")
    if not candidate:
        return ""
    lowered = candidate.lower()
    invalid_exact = {
        "agent",
        "assistant",
        "role",
        "一个",
        "一个agent",
        "一位",
        "一位agent",
        "角色",
        "助手",
        "草稿",
        "当前不构成缺陷",
        "不构成缺陷",
    }
    if lowered in invalid_exact or candidate in invalid_exact:
        return ""
    if re.fullmatch(r"(?:一个|一位|这个|那个|该)(?:agent|助手|角色)?", candidate, flags=re.IGNORECASE):
        return ""
    if re.fullmatch(r"(?:当前)?(?:不构成)?缺陷", candidate, flags=re.IGNORECASE):
        return ""
    return candidate


def _guess_role_name(texts: list[str]) -> str:
    patterns = (
        re.compile(r"(?:创建|做|想要|需要)(?:一个|一位|个)?([^\n，,。.!！？]{2,32}?)(?:角色|助手|agent)", re.IGNORECASE),
        re.compile(r"(?:角色名|角色名称|名字)\s*(?:是|叫|为|[:：=])\s*([^\n，,。.!！？]{2,32})", re.IGNORECASE),
        re.compile(r"(?:让它叫|就叫)\s*([^\n，,。.!！？]{2,32})", re.IGNORECASE),
    )
    for text in texts:
        for pattern in patterns:
            match = pattern.search(text)
            if not match:
                continue
            candidate = _normalize_role_name_candidate(match.group(1))
            if candidate:
                return candidate
    return ""


def _guess_role_name_from_assistant_suggestions(texts: list[str]) -> str:
    cue_words = ("角色名", "名字", "命名", "收口", "建议", "先用", "叫", "英文名")
    patterns = (
        re.compile(r"`([^`\n]{2,40})`"),
        re.compile(r"「([^」\n]{2,40})」"),
        re.compile(r"“([^”\n]{2,40})”"),
    )
    for text in reversed(list(texts or [])):
        content = str(text or "")
        for pattern in patterns:
            for match in pattern.finditer(content):
                context = content[max(0, match.start() - 24) : min(len(content), match.end() + 24)]
                if not any(cue in context for cue in cue_words):
                    continue
                candidate = _normalize_role_name_candidate(match.group(1))
                if candidate:
                    return candidate
    return ""


def _collect_sentence_items(texts: list[str], keywords: tuple[str, ...], *, limit: int = 8) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for text in texts:
        for part in re.split(r"[。\n！？!?]", str(text or "")):
            sentence = _normalize_text(part, max_len=240)
            if not sentence:
                continue
            if not any(keyword in sentence for keyword in keywords):
                continue
            key = sentence.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(sentence)
            if len(out) >= limit:
                return out
    return out


def _build_role_spec(messages: list[dict[str, Any]]) -> tuple[dict[str, Any], list[str]]:
    user_messages = [item for item in messages if str(item.get("role") or "").strip().lower() == "user"]
    assistant_messages = [item for item in messages if str(item.get("role") or "").strip().lower() == "assistant"]
    user_texts = _session_messages_texts(user_messages, role="user")
    assistant_texts = _session_messages_texts(assistant_messages, role="assistant")
    labeled: dict[str, list[str]] = {key: [] for key in ROLE_CREATION_ALL_FIELDS if key != "example_assets"}
    for text in user_texts:
        extracted = _extract_labeled_values(text)
        natural = _extract_natural_language_values(text)
        for key, items in extracted.items():
            labeled.setdefault(key, []).extend(items)
        for key, items in natural.items():
            labeled.setdefault(key, []).extend(items)
    attachments: list[dict[str, Any]] = []
    for message in user_messages:
        for item in list(message.get("attachments") or []):
            if not isinstance(item, dict):
                continue
            attachments.append(
                {
                    "attachment_id": str(item.get("attachment_id") or "").strip(),
                    "file_name": str(item.get("file_name") or "").strip(),
                    "content_type": str(item.get("content_type") or "").strip(),
                    "size_bytes": int(item.get("size_bytes") or 0),
                    "data_url": str(item.get("data_url") or ""),
                }
            )
    role_name = _normalize_role_name_candidate((labeled.get("role_name") or [""])[-1])
    if not role_name:
        role_name = _guess_role_name(user_texts)
    if not role_name:
        role_name = _guess_role_name_from_assistant_suggestions(assistant_texts)
    role_goal = _normalize_text((labeled.get("role_goal") or [""])[-1], max_len=280)
    if not role_goal:
        guesses = _collect_sentence_items(user_texts, ("目标", "职责", "负责", "帮助", "用于", "希望它", "用来"), limit=3)
        role_goal = "；".join(guesses[:2])[:280]
    core_capabilities = _split_items(labeled.get("core_capabilities") or [], limit=12)
    if not core_capabilities:
        guesses = _collect_sentence_items(
            user_texts,
            ("能力", "擅长", "会", "生成", "整理", "拆解", "诊断", "设计", "沉淀"),
            limit=6,
        )
        core_capabilities = _split_items(guesses, limit=12)
    boundaries = _split_items(labeled.get("boundaries") or [], limit=10)
    if not boundaries:
        boundaries = _split_items(
            _collect_sentence_items(user_texts, ("边界", "约束", "不要", "不能", "禁止", "避免", "别"), limit=6),
            limit=10,
        )
    applicable_scenarios = _split_items(labeled.get("applicable_scenarios") or [], limit=10)
    if not applicable_scenarios:
        applicable_scenarios = _split_items(
            _collect_sentence_items(user_texts, ("场景", "适用", "用于", "面向"), limit=6),
            limit=10,
        )
    collaboration_style = _normalize_text((labeled.get("collaboration_style") or [""])[-1], max_len=280)
    if not collaboration_style:
        guesses = _collect_sentence_items(user_texts, ("协作", "风格", "输出", "语气", "回传"), limit=3)
        collaboration_style = "；".join(guesses[:2])[:280]
    role_spec = {
        "role_name": role_name,
        "role_goal": role_goal,
        "core_capabilities": core_capabilities,
        "boundaries": boundaries,
        "applicable_scenarios": applicable_scenarios,
        "collaboration_style": collaboration_style,
        "example_assets": attachments[:6],
    }
    missing_fields: list[str] = []
    for key in ROLE_CREATION_ALL_FIELDS:
        if key == "example_assets":
            continue
        value = role_spec.get(key)
        if isinstance(value, list):
            if not value:
                missing_fields.append(key)
            continue
        if not str(value or "").strip():
            missing_fields.append(key)
    return role_spec, missing_fields


def _session_can_start(role_spec: dict[str, Any]) -> bool:
    for key in ROLE_CREATION_REQUIRED_FIELDS:
        value = role_spec.get(key)
        if isinstance(value, list):
            if not value:
                return False
            continue
        if not str(value or "").strip():
            return False
    return True


def _role_creation_title_from_spec(role_spec: dict[str, Any], fallback: str = "") -> str:
    role_name = _normalize_text(role_spec.get("role_name"), max_len=40)
    if role_name:
        return role_name
    return _normalize_text(fallback, max_len=40) or "未命名角色草稿"


def _missing_field_labels(missing_fields: list[str]) -> list[str]:
    mapping = {
        "role_name": "角色名",
        "role_goal": "角色目标",
        "core_capabilities": "核心能力",
        "boundaries": "禁止边界",
        "applicable_scenarios": "适用场景",
        "collaboration_style": "协作方式",
        "example_assets": "示例图片",
    }
    return [mapping.get(item, item) for item in missing_fields]


def _build_assistant_reply(
    *,
    session_summary: dict[str, Any],
    role_spec: dict[str, Any],
    missing_fields: list[str],
    created_tasks: list[dict[str, Any]],
) -> str:
    title = _role_creation_title_from_spec(role_spec, session_summary.get("session_title") or "")
    missing_labels = _missing_field_labels(missing_fields)
    capability_lines = _split_items(role_spec.get("core_capabilities") or [], limit=4)
    if created_tasks:
        names = [str(item.get("task_name") or item.get("node_name") or "").strip() for item in created_tasks]
        names = [item for item in names if item]
        task_line = "；".join(names[:3])
        return (
            f"已按你的委派新建后台任务：{task_line}。"
            "右侧阶段图已经改成真实任务引用，我会继续在当前会话里帮你收口画像和验收。"
        )
    if session_summary.get("status") == "creating":
        if missing_labels:
            return (
                f"我已经把「{title}」的草案继续收口。"
                f"当前还建议补这几项：{'、'.join(missing_labels[:4])}。"
                "如果你想把某项工作单独丢到后台，直接说“另起一个任务去……”。"
            )
        if capability_lines:
            return (
                f"「{title}」当前核心能力已聚焦在：{' / '.join(capability_lines[:3])}。"
                "你可以继续补充方向，也可以把当前轮推到验收。"
            )
        return f"我会继续围绕「{title}」推进创建流程。"
    if missing_labels:
        return (
            f"我先按当前描述把「{title}」收口成草案了。"
            f"开始创建前最好再补：{'、'.join(missing_labels[:4])}。"
        )
    return f"「{title}」已经达到最小开工门槛，可以直接点“开始创建”。"


def _delegate_requests_from_text(text: str) -> list[str]:
    content = _normalize_text(text, max_len=4000)
    if not content or not ROLE_CREATION_DELEGATE_PATTERN.search(content):
        return []
    clauses = re.split(r"[。！？!?]\s*", content)
    return [
        _normalize_text(clause, max_len=400)
        for clause in clauses
        if _normalize_text(clause, max_len=400) and ROLE_CREATION_DELEGATE_PATTERN.search(clause)
    ][:3]


def _infer_task_stage_key(text: str, current_stage_key: str) -> str:
    content = str(text or "")
    if any(token in content for token in ("回传", "预览", "截图", "回看")):
        return "review_and_alignment"
    if any(token in content for token in ("生成", "样例", "草案", "模板", "页面", "html")):
        return "capability_generation"
    if any(token in content for token in ("资料", "案例", "调研", "画像", "整理", "收集")):
        return "persona_collection"
    if current_stage_key in {"persona_collection", "capability_generation", "review_and_alignment"}:
        return current_stage_key
    return "persona_collection"


def _delegate_task_title(text: str, role_name: str) -> str:
    content = _normalize_text(text, max_len=200)
    content = ROLE_CREATION_DELEGATE_PATTERN.sub("", content, count=1).strip("，,。.!！？；;：: ")
    content = re.sub(r"^(请|帮我|帮忙|先|再|就)\s*", "", content)
    content = re.sub(r"(然后|并且|并)\s*回传.*$", "", content)
    content = re.sub(r"(回头|之后|最后).*$", "", content)
    content = _normalize_text(content, max_len=60)
    if not content:
        return f"补充{role_name or '新角色'}后台任务"
    if re.match(r"^(收集|整理|生成|沉淀|补|回传|分析)", content):
        return content
    return "处理" + content
