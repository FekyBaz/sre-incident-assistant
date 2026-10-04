from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any


_TIMESTAMP = re.compile(
    r"(?P<timestamp>\\d{4}-\\d{2}-\\d{2}[T ]\\d{2}:\\d{2}:\\d{2}(?:\\.\\d+)?(?:Z|[+-]\\d{2}:?\\d{2})?)"
)
_LEVEL = re.compile(r"\\b(?P<level>TRACE|DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL)\\b", re.I)


@dataclass(frozen=True)
class ParsedLog:
    timestamp: str | None
    level: str | None
    message: str
    raw: str


@dataclass(frozen=True)
class LogAnalysis:
    format: str
    total_entries: int
    level_counts: dict[str, int]
    error_entries: list[ParsedLog]
    representative_entries: list[ParsedLog]
    warnings: list[str]


class LogAnalyzer:
    def __init__(self, max_entries: int = 2000, max_error_entries: int = 100) -> None:
        self.max_entries = max_entries
        self.max_error_entries = max_error_entries

    def analyze(self, content: str, filename: str = "incident.log") -> LogAnalysis:
        text = content.replace("\\x00", "").strip()
        if not text:
            return LogAnalysis("empty", 0, {}, [], [], ["Log input is empty."])

        if filename.lower().endswith(".json") or self._looks_like_json(text):
            return self._analyze_json(text)

        return self._analyze_text(text)

    def _analyze_text(self, text: str) -> LogAnalysis:
        lines = text.splitlines()
        warnings: list[str] = []
        if len(lines) > self.max_entries:
            warnings.append(
                f"Input contained {len(lines)} lines; only the first {self.max_entries} were analyzed."
            )
            lines = lines[: self.max_entries]

        entries = [self._parse_line(line) for line in lines if line.strip()]
        level_counts = Counter(
            entry.level.upper() for entry in entries if entry.level
        )
        errors = [
            entry
            for entry in entries
            if entry.level and entry.level.upper() in {"ERROR", "FATAL", "CRITICAL"}
        ][: self.max_error_entries]

        return LogAnalysis(
            format="text",
            total_entries=len(entries),
            level_counts=dict(level_counts),
            error_entries=errors,
            representative_entries=entries[:50],
            warnings=warnings,
        )

    def _analyze_json(self, text: str) -> LogAnalysis:
        warnings: list[str] = []
        records: list[Any] = []

        try:
            decoded = json.loads(text)
            records = decoded if isinstance(decoded, list) else [decoded]
        except json.JSONDecodeError:
            for line in text.splitlines():
                if not line.strip():
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    warnings.append("Some JSON lines could not be parsed.")
        if len(records) > self.max_entries:
            warnings.append(
                f"Input contained {len(records)} JSON records; only the first {self.max_entries} were analyzed."
            )
            records = records[: self.max_entries]

        entries = [self._parse_json_record(record) for record in records]
        level_counts = Counter(
            entry.level.upper() for entry in entries if entry.level
        )
        errors = [
            entry
            for entry in entries
            if entry.level and entry.level.upper() in {"ERROR", "FATAL", "CRITICAL"}
        ][: self.max_error_entries]

        return LogAnalysis(
            format="json",
            total_entries=len(entries),
            level_counts=dict(level_counts),
            error_entries=errors,
            representative_entries=entries[:50],
            warnings=warnings,
        )

    @staticmethod
    def _looks_like_json(text: str) -> bool:
        return text.startswith("{") or text.startswith("[")

    @staticmethod
    def _parse_line(line: str) -> ParsedLog:
        timestamp_match = _TIMESTAMP.search(line)
        level_match = _LEVEL.search(line)
        message = line
        if level_match:
            message = line[level_match.end() :].lstrip(" :-|")
        return ParsedLog(
            timestamp=timestamp_match.group("timestamp") if timestamp_match else None,
            level=level_match.group("level").upper() if level_match else None,
            message=message[:2000],
            raw=line[:4000],
        )

    @staticmethod
    def _parse_json_record(record: Any) -> ParsedLog:
        if not isinstance(record, dict):
            return ParsedLog(None, None, str(record)[:2000], str(record)[:4000])

        timestamp = next(
            (record.get(key) for key in ("timestamp", "time", "datetime", "@timestamp") if record.get(key)),
            None,
        )
        level = next(
            (record.get(key) for key in ("level", "severity", "log_level") if record.get(key)),
            None,
        )
        message = next(
            (record.get(key) for key in ("message", "msg", "error", "exception") if record.get(key)),
            None,
        )
        raw = json.dumps(record, ensure_ascii=False, default=str)
        return ParsedLog(
            timestamp=str(timestamp)[:200],
            level=str(level).upper()[:30] if level else None,
            message=str(message)[:2000] if message is not None else raw[:2000],
            raw=raw[:4000],
        )
