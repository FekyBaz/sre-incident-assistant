from app.tools.log_analyzer import LogAnalyzer


def test_text_logs_are_normalized():
    content = """2026-10-04T10:00:00Z INFO request started
2026-10-04T10:00:02Z ERROR database timeout
2026-10-04T10:00:03Z WARN retrying request
"""
    result = LogAnalyzer().analyze(content, "app.log")

    assert result.format == "text"
    assert result.total_entries == 3
    assert result.level_counts == {"INFO": 1, "ERROR": 1, "WARN": 1}
    assert result.error_entries[0].message == "database timeout"


def test_json_logs_are_normalized():
    content = '[{"timestamp":"2026-10-04T10:00:00Z","level":"ERROR","message":"connection refused"}]'
    result = LogAnalyzer().analyze(content, "app.json")

    assert result.format == "json"
    assert result.total_entries == 1
    assert result.error_entries[0].level == "ERROR"
    assert result.error_entries[0].message == "connection refused"


def test_large_input_is_bounded():
    content = "\n".join(f"2026-10-04T10:00:{i:02d}Z INFO line {i}" for i in range(20))
    result = LogAnalyzer(max_entries=5).analyze(content)

    assert result.total_entries == 5
    assert result.warnings


def test_fractional_second_timestamp_is_parsed():
    content = "2026-10-04T10:05:47.123Z WARN queries=51"
    result = LogAnalyzer().analyze(content, "app.log")

    assert result.representative_entries[0].timestamp == "2026-10-04T10:05:47.123Z"
