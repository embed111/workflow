#!/usr/bin/env python3
"""Enforce the maintained-workspace line budget gate."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


MAX_LINES = 1000
TARGET_EXTENSIONS = {
    ".bat",
    ".css",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".sql",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


@dataclass(frozen=True)
class Offender:
    path: str
    line_count: int


class ExclusionRule:
    label: str
    reason: str

    def matches(self, relative_path: Path) -> bool:
        raise NotImplementedError


@dataclass(frozen=True)
class DirectoryNameRule(ExclusionRule):
    label: str
    reason: str
    names: tuple[str, ...]

    def matches(self, relative_path: Path) -> bool:
        return any(part in self.names for part in relative_path.parts)


@dataclass(frozen=True)
class PrefixRule(ExclusionRule):
    label: str
    reason: str
    prefix: tuple[str, ...]

    def matches(self, relative_path: Path) -> bool:
        parts = relative_path.parts
        return parts[: len(self.prefix)] == self.prefix


EXCLUSION_RULES: tuple[ExclusionRule, ...] = (
    DirectoryNameRule(
        label="runtime_artifacts",
        reason="运行态、审计和测试产物不纳入工程重构预算。",
        names=(
            ".codex",
            ".git",
            ".output",
            ".runtime",
            ".test",
            ".venv",
            "__pycache__",
            "incidents",
            "logs",
            "metrics",
            "node_modules",
            "state",
            "test-results",
        ),
    ),
    PrefixRule(
        label="workflow_prototypes",
        reason="原型图不需要重构。",
        prefix=("docs", "workflow", "prototypes"),
    ),
    PrefixRule(
        label="workflow_requirements",
        reason="需求文档不需要重构。",
        prefix=("docs", "workflow", "requirements"),
    ),
    PrefixRule(
        label="workflow_screenshots",
        reason="截图证据不纳入代码体量门禁。",
        prefix=("docs", "workflow", "screenshots"),
    ),
    PrefixRule(
        label="workflow_archive",
        reason="归档文档不纳入当前维护预算。",
        prefix=("docs", "workflow", "governance", "archive"),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check maintained workspace files stay under the line budget.")
    parser.add_argument("--root", default=".", help="Workspace root path.")
    parser.add_argument("--max-lines", type=int, default=MAX_LINES, help="Maximum allowed line count per file.")
    parser.add_argument(
        "--report",
        default=".test/reports/WORKSPACE_LINE_BUDGET_REPORT.md",
        help="Report file path (absolute or relative to root).",
    )
    return parser.parse_args()


def resolve_report_path(root: Path, report_arg: str) -> Path:
    report_path = Path(report_arg)
    if report_path.is_absolute():
        return report_path
    return root / report_path


def resolve_exclusion(relative_path: Path) -> ExclusionRule | None:
    for rule in EXCLUSION_RULES:
        if rule.matches(relative_path):
            return rule
    return None


def should_scan(path: Path) -> bool:
    return path.suffix.lower() in TARGET_EXTENSIONS


def count_lines(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        return sum(1 for _ in handle)


def scan_workspace(root: Path, max_lines: int) -> list[Offender]:
    offenders: list[Offender] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative_path = path.relative_to(root)
        if resolve_exclusion(relative_path) is not None:
            continue
        if not should_scan(path):
            continue
        line_count = count_lines(path)
        if line_count > max(1, int(max_lines)):
            offenders.append(Offender(path=relative_path.as_posix(), line_count=line_count))
    offenders.sort(key=lambda item: (-item.line_count, item.path))
    return offenders


def render_report(root: Path, report_path: Path, max_lines: int, offenders: list[Offender]) -> str:
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    passed = not offenders
    lines: list[str] = [
        "# WORKSPACE_LINE_BUDGET_REPORT",
        "",
        f"- generated_at: {now}",
        f"- root: {root.as_posix()}",
        f"- report_path: {report_path.as_posix()}",
        f"- max_lines: {max_lines}",
        "- scan_scope: maintained_workspace_text_files",
        f"- pass: {'true' if passed else 'false'}",
        f"- offender_count: {len(offenders)}",
        f"- trigger_action: {'none' if passed else 'trigger_refactor_skill'}",
        "",
        "## Exclusions",
        "",
        "| rule | reason |",
        "|---|---|",
    ]
    for rule in EXCLUSION_RULES:
        lines.append(f"| `{rule.label}` | {rule.reason} |")
    lines.extend(
        [
            "",
            "## Result",
            "",
        ]
    )
    if offenders:
        lines.extend(
            [
                "| file | lines | action |",
                "|---|---:|---|",
            ]
        )
        for offender in offenders:
            lines.append(
                f"| `{offender.path}` | {offender.line_count} | `trigger_refactor_skill` |"
            )
    else:
        lines.append(f"all maintained files are <= {max_lines} lines.")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- 原型图、需求文档、运行态/日志/证据目录默认不纳入本门禁。",
            "- 命中超限时，门禁直接失败，并输出 `trigger_refactor_skill` 作为后续动作信号。",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    report_path = resolve_report_path(root, args.report)
    offenders = scan_workspace(root, args.max_lines)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_report(root, report_path, args.max_lines, offenders),
        encoding="utf-8",
    )
    print(report_path.as_posix())
    return 0 if not offenders else 1


if __name__ == "__main__":
    raise SystemExit(main())
