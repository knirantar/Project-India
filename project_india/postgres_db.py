"""Local Postgres storage for Project India research evidence."""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from project_india import paths


DEFAULT_DATABASE_URL = "postgresql://project_india:project_india_local@localhost:5433/project_india"
DATABASE_URL_ENV = "PROJECT_INDIA_DATABASE_URL"


@dataclass(frozen=True)
class ImportSummary:
    topics: int
    topic_documents: int
    source_logs: int
    briefs: int
    research_runs: int
    metrics: int
    comparisons: int
    comparison_items: int
    timeline_events: int
    tables: int
    data_gaps: int
    artifacts: int


def database_url() -> str:
    if os.environ.get(DATABASE_URL_ENV):
        return os.environ[DATABASE_URL_ENV]

    env_file = paths.ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            key, separator, value = line.partition("=")
            if separator and key.strip() == DATABASE_URL_ENV:
                return value.strip().strip('"').strip("'")

    return DEFAULT_DATABASE_URL


def _connect():
    try:
        import psycopg
    except ImportError as error:
        raise SystemExit(
            "psycopg is required for Postgres commands. Install with: "
            "python3 -m pip install -e '.[db]'"
        ) from error

    try:
        return psycopg.connect(database_url())
    except psycopg.OperationalError as error:
        raise SystemExit(
            "Could not connect to local Postgres. Start it with `docker compose up -d postgres` "
            f"and check {DATABASE_URL_ENV}."
        ) from error


def _json(value: Any) -> str:
    return json.dumps(value if value is not None else {}, sort_keys=True)


def _read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text_from_repo(relative_path: str | None) -> str:
    if not relative_path:
        return ""
    path = paths.ROOT / relative_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _numeric(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, AttributeError, ValueError):
        return None


def _section(markdown: str, heading: str) -> str:
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s+|\Z)",
        re.MULTILINE,
    )
    match = pattern.search(markdown)
    return match.group(1).strip() if match else ""


def _parse_generated_at(payload: dict[str, Any]) -> datetime | None:
    raw_value = payload.get("generated_at") or payload.get("timestamp")
    if not raw_value:
        return None
    try:
        return datetime.fromisoformat(str(raw_value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _topic_config_by_slug() -> dict[str, dict[str, Any]]:
    config = _read_json(paths.ROOT / "research_config.json", {})
    return {
        str(topic.get("slug")): topic
        for topic in config.get("topics", [])
        if topic.get("slug")
    }


def _extract_source_entries(source_log: str) -> list[dict[str, str | None]]:
    entries: list[dict[str, str | None]] = []
    url_pattern = re.compile(r"https?://[^\s)|]+")
    for line in source_log.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("| ---"):
            continue
        urls = url_pattern.findall(stripped)
        if not urls:
            continue

        parts = [part.strip() for part in stripped.strip("|").split("|")]
        title = parts[1] if len(parts) >= 3 else parts[0]
        notes = parts[-1] if len(parts) >= 2 else stripped
        source_date = parts[0] if len(parts) >= 3 else None
        entries.append(
            {
                "source_type": "source-log",
                "title": title or None,
                "url": urls[0],
                "source_date": source_date,
                "notes": notes or None,
                "raw_entry": stripped,
            }
        )
    return entries


def init_db(schema_path: Path | None = None) -> None:
    schema = schema_path or paths.DB_SCHEMA
    with _connect() as conn:
        conn.execute(schema.read_text(encoding="utf-8"))


def count_tables() -> dict[str, int]:
    tables = [
        "topics",
        "topic_documents",
        "briefs",
        "source_logs",
        "source_entries",
        "research_runs",
        "topic_metrics",
        "topic_comparisons",
        "comparison_items",
        "timeline_events",
        "topic_tables",
        "data_gaps",
        "research_artifacts",
    ]
    with _connect() as conn:
        counts = {}
        for table in tables:
            counts[table] = conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
    return counts


def import_repo_data() -> ImportSummary:
    index = _read_json(paths.PROCESSED_DATA / "research_index.json", [])
    config_by_slug = _topic_config_by_slug()

    counters = {
        "topics": 0,
        "topic_documents": 0,
        "source_logs": 0,
        "briefs": 0,
        "research_runs": 0,
        "metrics": 0,
        "comparisons": 0,
        "comparison_items": 0,
        "timeline_events": 0,
        "tables": 0,
        "data_gaps": 0,
        "artifacts": 0,
    }

    with _connect() as conn:
        for record in index:
            slug = record.get("slug")
            if not slug:
                continue

            topic_data = _read_json(paths.TOPIC_DATA / f"{slug}.json", {})
            topic_config = config_by_slug.get(slug, {})
            schedule = topic_config.get("schedule", {})
            strategy = topic_config.get("strategy", {})
            metadata = topic_config.get("metadata", {})
            status = topic_data.get("status") or metadata.get("development_status") or "developing"

            topic_id = conn.execute(
                """
                INSERT INTO topics (
                    slug, title, category, status, enabled, schedule_frequency,
                    schedule_time_utc, schedule_day_of_week, schedule_day_of_month,
                    last_run_date, next_scheduled_run, strategy_rotation, metadata,
                    topic_path, source_path, brief_path, topic_data_path, updated_at
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb,
                    %s, %s, %s, %s, now()
                )
                ON CONFLICT (slug) DO UPDATE SET
                    title = EXCLUDED.title,
                    category = EXCLUDED.category,
                    status = EXCLUDED.status,
                    enabled = EXCLUDED.enabled,
                    schedule_frequency = EXCLUDED.schedule_frequency,
                    schedule_time_utc = EXCLUDED.schedule_time_utc,
                    schedule_day_of_week = EXCLUDED.schedule_day_of_week,
                    schedule_day_of_month = EXCLUDED.schedule_day_of_month,
                    last_run_date = EXCLUDED.last_run_date,
                    next_scheduled_run = EXCLUDED.next_scheduled_run,
                    strategy_rotation = EXCLUDED.strategy_rotation,
                    metadata = EXCLUDED.metadata,
                    topic_path = EXCLUDED.topic_path,
                    source_path = EXCLUDED.source_path,
                    brief_path = EXCLUDED.brief_path,
                    topic_data_path = EXCLUDED.topic_data_path,
                    updated_at = now()
                RETURNING id
                """,
                (
                    slug,
                    record.get("title", slug),
                    record.get("category", "research-notes"),
                    status,
                    bool(topic_config.get("enabled", False)),
                    schedule.get("frequency", "manual"),
                    schedule.get("time_utc"),
                    schedule.get("day_of_week"),
                    schedule.get("day_of_month"),
                    schedule.get("last_run_date"),
                    schedule.get("next_scheduled_run"),
                    _json(strategy.get("rotation", [])),
                    _json(metadata),
                    record.get("topic_path"),
                    record.get("source_path"),
                    record.get("brief_path"),
                    record.get("topic_data_path"),
                ),
            ).fetchone()[0]
            counters["topics"] += 1

            topic_markdown = _read_text_from_repo(record.get("topic_path"))
            if topic_markdown:
                conn.execute(
                    """
                    INSERT INTO topic_documents (topic_id, document_type, path, content, metadata)
                    VALUES (%s, 'topic_note', %s, %s, %s::jsonb)
                    ON CONFLICT (topic_id, document_type, path) DO UPDATE SET
                        content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata,
                        updated_at = now()
                    """,
                    (topic_id, record.get("topic_path"), topic_markdown, _json({"slug": slug})),
                )
                counters["topic_documents"] += 1
                _upsert_artifact(conn, topic_id, slug, "topic_note", record.get("topic_path"), topic_markdown)
                counters["artifacts"] += 1

            source_log = _read_text_from_repo(record.get("source_path"))
            if source_log:
                conn.execute(
                    """
                    INSERT INTO source_logs (topic_id, path, content, metadata)
                    VALUES (%s, %s, %s, %s::jsonb)
                    ON CONFLICT (topic_id) DO UPDATE SET
                        path = EXCLUDED.path,
                        content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata,
                        updated_at = now()
                    """,
                    (topic_id, record.get("source_path"), source_log, _json({"slug": slug})),
                )
                counters["source_logs"] += 1
                conn.execute("DELETE FROM source_entries WHERE topic_id = %s", (topic_id,))
                for entry in _extract_source_entries(source_log):
                    conn.execute(
                        """
                        INSERT INTO source_entries (
                            topic_id, source_type, title, url, source_date, notes, raw_entry
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            topic_id,
                            entry["source_type"],
                            entry["title"],
                            entry["url"],
                            entry["source_date"],
                            entry["notes"],
                            entry["raw_entry"],
                        ),
                    )
                _upsert_artifact(conn, topic_id, slug, "source_log", record.get("source_path"), source_log)
                counters["artifacts"] += 1

            brief = _read_text_from_repo(record.get("brief_path"))
            if brief:
                conn.execute(
                    """
                    INSERT INTO briefs (topic_id, title, bottom_line, key_takeaways, content, path)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (topic_id) DO UPDATE SET
                        title = EXCLUDED.title,
                        bottom_line = EXCLUDED.bottom_line,
                        key_takeaways = EXCLUDED.key_takeaways,
                        content = EXCLUDED.content,
                        path = EXCLUDED.path,
                        updated_at = now()
                    """,
                    (
                        topic_id,
                        f"Brief: {record.get('title', slug)}",
                        _section(brief, "Bottom Line"),
                        _section(brief, "Key Takeaways"),
                        brief,
                        record.get("brief_path"),
                    ),
                )
                counters["briefs"] += 1
                _upsert_artifact(conn, topic_id, slug, "brief", record.get("brief_path"), brief)
                counters["artifacts"] += 1

            counters["metrics"] += _import_metrics(conn, topic_id, topic_data)
            comparison_count, item_count = _import_comparisons(conn, topic_id, topic_data)
            counters["comparisons"] += comparison_count
            counters["comparison_items"] += item_count
            counters["timeline_events"] += _import_timeline(conn, topic_id, topic_data)
            counters["tables"] += _import_tables(conn, topic_id, topic_data)
            counters["data_gaps"] += _import_gaps(conn, topic_id, topic_data)

        counters["research_runs"] += _import_runs(conn)

    return ImportSummary(**counters)


def _upsert_artifact(conn: Any, topic_id: int, slug: str, artifact_type: str, path: str | None, content: str) -> None:
    conn.execute(
        """
        INSERT INTO research_artifacts (topic_id, slug, artifact_type, path, content_hash, payload)
        VALUES (%s, %s, %s, %s, %s, %s::jsonb)
        ON CONFLICT (slug, artifact_type, path) DO UPDATE SET
            topic_id = EXCLUDED.topic_id,
            content_hash = EXCLUDED.content_hash,
            payload = EXCLUDED.payload,
            created_at = now()
        """,
        (
            topic_id,
            slug,
            artifact_type,
            path,
            _content_hash(content),
            _json({"length": len(content)}),
        ),
    )


def _import_metrics(conn: Any, topic_id: int, topic_data: dict[str, Any]) -> int:
    conn.execute("DELETE FROM topic_metrics WHERE topic_id = %s", (topic_id,))
    metrics = topic_data.get("metrics", [])
    if isinstance(metrics, dict):
        metrics = [{"label": key, "value": value} for key, value in metrics.items()]
    if not isinstance(metrics, list):
        return 0

    count = 0
    for metric in metrics:
        if not isinstance(metric, dict) or not metric.get("label"):
            continue
        value = metric.get("value")
        conn.execute(
            """
            INSERT INTO topic_metrics (
                topic_id, label, value_text, numeric_value, unit, date_label,
                context, source, confidence, payload
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            """,
            (
                topic_id,
                str(metric.get("label")),
                None if value is None else str(value),
                _numeric(value),
                metric.get("unit"),
                metric.get("date"),
                metric.get("context"),
                metric.get("source"),
                metric.get("confidence"),
                _json(metric),
            ),
        )
        count += 1
    return count


def _import_comparisons(conn: Any, topic_id: int, topic_data: dict[str, Any]) -> tuple[int, int]:
    comparison_ids = [
        row[0]
        for row in conn.execute(
            "SELECT id FROM topic_comparisons WHERE topic_id = %s", (topic_id,)
        ).fetchall()
    ]
    for comparison_id in comparison_ids:
        conn.execute("DELETE FROM comparison_items WHERE comparison_id = %s", (comparison_id,))
    conn.execute("DELETE FROM topic_comparisons WHERE topic_id = %s", (topic_id,))

    comparisons = topic_data.get("comparisons", [])
    if not isinstance(comparisons, list):
        return 0, 0

    comparison_count = 0
    item_count = 0
    for comparison in comparisons:
        if not isinstance(comparison, dict) or not comparison.get("title"):
            continue
        comparison_id = conn.execute(
            """
            INSERT INTO topic_comparisons (topic_id, title, unit, source, payload)
            VALUES (%s, %s, %s, %s, %s::jsonb)
            RETURNING id
            """,
            (
                topic_id,
                comparison.get("title"),
                comparison.get("unit"),
                comparison.get("source"),
                _json(comparison),
            ),
        ).fetchone()[0]
        comparison_count += 1

        for item in comparison.get("items", []):
            if not isinstance(item, dict) or not item.get("label"):
                continue
            value = item.get("value")
            conn.execute(
                """
                INSERT INTO comparison_items (
                    comparison_id, label, value_text, numeric_value, payload
                )
                VALUES (%s, %s, %s, %s, %s::jsonb)
                """,
                (
                    comparison_id,
                    item.get("label"),
                    None if value is None else str(value),
                    _numeric(value),
                    _json(item),
                ),
            )
            item_count += 1
    return comparison_count, item_count


def _import_timeline(conn: Any, topic_id: int, topic_data: dict[str, Any]) -> int:
    conn.execute("DELETE FROM timeline_events WHERE topic_id = %s", (topic_id,))
    timeline = topic_data.get("timeline", [])
    if not isinstance(timeline, list):
        return 0
    count = 0
    for event in timeline:
        if not isinstance(event, dict) or not event.get("event"):
            continue
        conn.execute(
            """
            INSERT INTO timeline_events (
                topic_id, event_date, event, significance, source, payload
            )
            VALUES (%s, %s, %s, %s, %s, %s::jsonb)
            """,
            (
                topic_id,
                event.get("date"),
                event.get("event"),
                event.get("significance"),
                event.get("source"),
                _json(event),
            ),
        )
        count += 1
    return count


def _import_tables(conn: Any, topic_id: int, topic_data: dict[str, Any]) -> int:
    conn.execute("DELETE FROM topic_tables WHERE topic_id = %s", (topic_id,))
    tables = topic_data.get("tables", [])
    if not isinstance(tables, list):
        return 0
    count = 0
    for table in tables:
        if not isinstance(table, dict) or not table.get("title"):
            continue
        conn.execute(
            """
            INSERT INTO topic_tables (topic_id, title, columns, rows, source, payload)
            VALUES (%s, %s, %s::jsonb, %s::jsonb, %s, %s::jsonb)
            """,
            (
                topic_id,
                table.get("title"),
                _json(table.get("columns", [])),
                _json(table.get("rows", [])),
                table.get("source"),
                _json(table),
            ),
        )
        count += 1
    return count


def _import_gaps(conn: Any, topic_id: int, topic_data: dict[str, Any]) -> int:
    conn.execute("DELETE FROM data_gaps WHERE topic_id = %s", (topic_id,))
    gaps = topic_data.get("data_gaps", [])
    if not isinstance(gaps, list):
        return 0
    count = 0
    for gap in gaps:
        if not gap:
            continue
        conn.execute(
            "INSERT INTO data_gaps (topic_id, gap) VALUES (%s, %s)",
            (topic_id, str(gap)),
        )
        count += 1
    return count


def _import_runs(conn: Any) -> int:
    count = 0
    for run_path in sorted(paths.RESEARCH_RUNS.glob("*.json")):
        payload = _read_json(run_path, {})
        slug = payload.get("slug") or run_path.stem.split("-increment-", 1)[0]
        topic_row = conn.execute("SELECT id FROM topics WHERE slug = %s", (slug,)).fetchone()
        topic_id = topic_row[0] if topic_row else None
        run_type = "incremental" if "-increment-" in run_path.stem else payload.get("depth", "deep")
        strategy = payload.get("strategy")
        summary = payload.get("summary")
        if isinstance(summary, list):
            summary = "\n".join(str(item) for item in summary)

        conn.execute(
            """
            INSERT INTO research_runs (
                topic_id, slug, run_key, run_type, strategy, model, generated_at,
                api_cost_usd, skipped_api_call, summary, path, payload
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (run_key) DO UPDATE SET
                topic_id = EXCLUDED.topic_id,
                run_type = EXCLUDED.run_type,
                strategy = EXCLUDED.strategy,
                model = EXCLUDED.model,
                generated_at = EXCLUDED.generated_at,
                api_cost_usd = EXCLUDED.api_cost_usd,
                skipped_api_call = EXCLUDED.skipped_api_call,
                summary = EXCLUDED.summary,
                path = EXCLUDED.path,
                payload = EXCLUDED.payload
            """,
            (
                topic_id,
                slug,
                str(run_path.relative_to(paths.ROOT)),
                run_type,
                strategy,
                payload.get("model"),
                _parse_generated_at(payload),
                payload.get("api_cost_usd") or 0,
                bool(payload.get("skipped_api_call", False)),
                summary,
                str(run_path.relative_to(paths.ROOT)),
                _json(payload),
            ),
        )
        count += 1
    return count
