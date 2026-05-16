"""Project India public research dashboard."""

from __future__ import annotations

import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data" / "processed"
SOURCES_DIR = ROOT / "sources"
PROD_URL = "https://project-india-nflujcnhq3f7xfj2d6q6sh.streamlit.app/"
DATABASE_URL_ENV = "PROJECT_INDIA_DATABASE_URL"
DEFAULT_DATABASE_URL = "postgresql://project_india:project_india_local@localhost:5433/project_india"
STATUS_TABLES = [
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


st.set_page_config(
    page_title="Project India Intelligence Dashboard",
    page_icon="IN",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .block-container { padding-top: 1.4rem; padding-bottom: 2rem; }
    .pi-kicker {
        color: #4f5d75;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }
    .pi-hero {
        border-left: 4px solid #1b998b;
        padding: 0.25rem 0 0.25rem 1rem;
        margin: 0.5rem 0 1rem 0;
    }
    .pi-muted { color: #5d6676; }
    .pi-chip {
        display: inline-block;
        border: 1px solid #d8dee8;
        border-radius: 999px;
        padding: 0.12rem 0.55rem;
        margin: 0 0.25rem 0.25rem 0;
        color: #354052;
        background: #f7f9fc;
        font-size: 0.78rem;
    }
    .pi-section-note {
        border: 1px solid #d8dee8;
        border-radius: 8px;
        padding: 0.75rem 0.9rem;
        background: #fbfcfe;
        color: #354052;
    }
    h1, h2, h3 { letter-spacing: 0; }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data(ttl=300)
def read_json(path: Path, fallback: Any) -> Any:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return fallback


@st.cache_data(ttl=300)
def read_text(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def database_url() -> str:
    if os.environ.get(DATABASE_URL_ENV):
        return os.environ[DATABASE_URL_ENV]

    try:
        secret_url = st.secrets.get(DATABASE_URL_ENV)
    except (FileNotFoundError, KeyError, AttributeError):
        secret_url = None

    return str(secret_url) if secret_url else DEFAULT_DATABASE_URL


@st.cache_data(ttl=60)
def load_database_status() -> dict[str, Any]:
    try:
        import psycopg
    except ImportError as error:
        return {
            "connected": False,
            "error": f"psycopg is not installed: {error}",
            "counts": {},
        }

    try:
        with psycopg.connect(database_url(), connect_timeout=5) as conn:
            counts = {}
            for table in STATUS_TABLES:
                counts[table] = conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            return {"connected": True, "error": "", "counts": counts}
    except Exception as error:
        return {"connected": False, "error": str(error), "counts": {}}


@st.cache_data(ttl=60)
def load_postgres_topics() -> list[dict[str, Any]]:
    try:
        import psycopg
        from psycopg.rows import dict_row
    except ImportError:
        return []

    try:
        with psycopg.connect(database_url(), connect_timeout=5, row_factory=dict_row) as conn:
            rows = conn.execute(
                """
                SELECT
                    t.id,
                    t.slug,
                    t.title,
                    t.category,
                    t.status,
                    t.metadata,
                    t.updated_at,
                    b.content AS brief_content,
                    b.bottom_line,
                    b.key_takeaways
                FROM topics t
                LEFT JOIN briefs b ON b.topic_id = t.id
                ORDER BY t.category, t.title
                """
            ).fetchall()
    except Exception:
        return []

    topics = []
    for row in rows:
        item = dict(row)
        item["source"] = "postgres"
        item["updated_at"] = item["updated_at"].isoformat() if item.get("updated_at") else "unknown"
        topics.append(item)
    return topics


@st.cache_data(ttl=60)
def load_postgres_topic_data(slug: str) -> dict[str, Any]:
    try:
        import psycopg
        from psycopg.rows import dict_row
    except ImportError:
        return {}

    try:
        with psycopg.connect(database_url(), connect_timeout=5, row_factory=dict_row) as conn:
            topic = conn.execute("SELECT id, status FROM topics WHERE slug = %s", (slug,)).fetchone()
            if not topic:
                return {}

            topic_id = topic["id"]
            metrics = conn.execute(
                """
                SELECT
                    label,
                    COALESCE(value_text, numeric_value::text) AS value,
                    unit,
                    context,
                    source
                FROM topic_metrics
                WHERE topic_id = %s
                ORDER BY label
                """,
                (topic_id,),
            ).fetchall()

            comparisons = []
            comparison_rows = conn.execute(
                """
                SELECT id, title, unit, source
                FROM topic_comparisons
                WHERE topic_id = %s
                ORDER BY title
                """,
                (topic_id,),
            ).fetchall()
            for comparison in comparison_rows:
                items = conn.execute(
                    """
                    SELECT
                        label,
                        COALESCE(value_text, numeric_value::text) AS value
                    FROM comparison_items
                    WHERE comparison_id = %s
                    ORDER BY label
                    """,
                    (comparison["id"],),
                ).fetchall()
                comparisons.append(
                    {
                        "title": comparison["title"],
                        "unit": comparison["unit"],
                        "source": comparison["source"],
                        "items": [dict(item) for item in items],
                    }
                )

            timeline = conn.execute(
                """
                SELECT event_date AS date, event, significance, source
                FROM timeline_events
                WHERE topic_id = %s
                ORDER BY event_date, event
                """,
                (topic_id,),
            ).fetchall()

            tables = conn.execute(
                """
                SELECT title, columns, rows, source
                FROM topic_tables
                WHERE topic_id = %s
                ORDER BY title
                """,
                (topic_id,),
            ).fetchall()

            gaps = conn.execute(
                """
                SELECT gap
                FROM data_gaps
                WHERE topic_id = %s
                ORDER BY gap
                """,
                (topic_id,),
            ).fetchall()

    except Exception:
        return {}

    return {
        "status": topic["status"],
        "metrics": [dict(metric) for metric in metrics],
        "comparisons": comparisons,
        "timeline": [dict(event) for event in timeline],
        "tables": [dict(table) for table in tables],
        "data_gaps": [gap["gap"] for gap in gaps],
    }


@st.cache_data(ttl=300)
def load_research_index() -> list[dict[str, Any]]:
    data = read_json(DATA_DIR / "research_index.json", [])
    return data if isinstance(data, list) else []


@st.cache_data(ttl=300)
def load_topic_data(slug: str) -> dict[str, Any]:
    postgres_data = load_postgres_topic_data(slug)
    if postgres_data:
        return postgres_data

    data = read_json(DATA_DIR / "topic_data" / f"{slug}.json", {})
    return data if isinstance(data, dict) else {}


@st.cache_data(ttl=300)
def load_research_runs() -> list[dict[str, Any]]:
    runs_dir = DATA_DIR / "research_runs"
    runs: list[dict[str, Any]] = []
    if not runs_dir.exists():
        return runs

    for run_file in sorted(runs_dir.glob("*.json"), reverse=True):
        try:
            data = json.loads(run_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                runs.append(data)
        except json.JSONDecodeError:
            continue
    return runs


def section_text(markdown: str, heading: str) -> str:
    """Extract a markdown section by heading text."""
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s+|\Z)",
        re.MULTILINE,
    )
    match = pattern.search(markdown)
    return match.group(1).strip() if match else ""


def first_paragraph(markdown: str, limit: int = 340) -> str:
    lines = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(stripped)
        if len(" ".join(lines)) >= limit:
            break
    text = " ".join(lines)
    return text[:limit].rstrip() + ("..." if len(text) > limit else "")


def file_label(path: str | None) -> str:
    return path or "Not available"


def topic_markdown_path(record: dict[str, Any]) -> Path | None:
    path = record.get("topic_path")
    return ROOT / path if path else None


def brief_markdown_path(record: dict[str, Any]) -> Path | None:
    path = record.get("brief_path")
    return ROOT / path if path else None


def topic_summary(record: dict[str, Any]) -> str:
    if record.get("bottom_line"):
        return str(record["bottom_line"])
    if record.get("brief_content"):
        return first_paragraph(str(record["brief_content"]))

    topic_path = topic_markdown_path(record)
    if topic_path and topic_path.exists():
        return first_paragraph(read_text(topic_path))
    brief_path = brief_markdown_path(record)
    if brief_path and brief_path.exists():
        return first_paragraph(read_text(brief_path))
    return "Research note is present in the index, but no readable summary has been added yet."


def merged_topics() -> list[dict[str, Any]]:
    postgres_topics = load_postgres_topics()
    if postgres_topics:
        return postgres_topics

    index = load_research_index()
    by_slug: dict[str, dict[str, Any]] = {}

    for item in index:
        slug = item.get("slug")
        if slug:
            by_slug[slug] = dict(item)

    return sorted(
        by_slug.values(),
        key=lambda item: (
            0 if load_topic_data(item.get("slug", "")) else 1,
            item.get("category", ""),
            item.get("title", ""),
        ),
    )


def has_structured_data(topic_data: dict[str, Any]) -> bool:
    return any(
        topic_data.get(key)
        for key in ["metrics", "comparisons", "timeline", "tables", "data_gaps"]
    )


def display_metric_cards(topic_data: dict[str, Any]) -> None:
    metrics = topic_data.get("metrics")
    if not metrics:
        return

    if isinstance(metrics, dict):
        metric_items = [
            {"label": str(label), "value": value, "unit": ""}
            for label, value in metrics.items()
        ]
    elif isinstance(metrics, list):
        metric_items = [
            metric for metric in metrics if isinstance(metric, dict) and metric.get("label")
        ]
    else:
        return

    if not metric_items:
        return

    st.subheader("Evidence Metrics")
    cols = st.columns(min(4, len(metric_items)))
    for idx, metric in enumerate(metric_items[:8]):
        value = metric.get("value", "N/A")
        unit = metric.get("unit")
        display_value = f"{value} {unit}" if unit and unit not in {"count", "number"} else value
        with cols[idx % len(cols)]:
            st.metric(
                str(metric.get("label", "Metric")),
                display_value,
                help=metric.get("context") or metric.get("source"),
            )

    with st.expander("Metric evidence table", expanded=False):
        st.dataframe(pd.DataFrame(metric_items), width="stretch", hide_index=True)


def display_comparisons(topic_data: dict[str, Any]) -> None:
    comparisons = topic_data.get("comparisons")
    if not isinstance(comparisons, list) or not comparisons:
        return

    st.subheader("Comparisons")
    for comparison in comparisons:
        if not isinstance(comparison, dict):
            continue
        items = comparison.get("items")
        if not isinstance(items, list) or not items:
            continue
        df = pd.DataFrame(items)
        title = comparison.get("title", "Comparison")
        unit = comparison.get("unit", "")

        left, right = st.columns([1.3, 1])
        with left:
            fig = px.bar(
                df,
                x="label",
                y="value",
                title=title,
                labels={"label": "", "value": unit or "Value"},
                color="label",
                color_discrete_sequence=px.colors.qualitative.Safe,
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, width="stretch")
        with right:
            st.dataframe(df, width="stretch", hide_index=True)
            if comparison.get("source"):
                st.caption(f"Source: {comparison['source']}")


def display_timeline(topic_data: dict[str, Any]) -> None:
    timeline = topic_data.get("timeline")
    if not isinstance(timeline, list) or not timeline:
        return

    st.subheader("Timeline")
    df = pd.DataFrame(timeline)
    st.dataframe(df, width="stretch", hide_index=True)


def display_tables(topic_data: dict[str, Any]) -> None:
    tables = topic_data.get("tables")
    if not isinstance(tables, list) or not tables:
        return

    st.subheader("Tables")
    for table in tables:
        if not isinstance(table, dict):
            continue
        title = table.get("title", "Table")
        columns = table.get("columns", [])
        rows = table.get("rows", [])
        if not rows:
            continue
        st.markdown(f"**{title}**")
        st.dataframe(pd.DataFrame(rows, columns=columns or None), width="stretch", hide_index=True)
        if table.get("source"):
            st.caption(f"Source: {table['source']}")


def display_gaps(topic_data: dict[str, Any]) -> None:
    gaps = topic_data.get("data_gaps")
    if not isinstance(gaps, list) or not gaps:
        return

    st.subheader("Open Research Questions")
    for gap in gaps:
        st.markdown(f"- {gap}")


def display_brief(record: dict[str, Any]) -> None:
    if record.get("brief_content") or record.get("bottom_line") or record.get("key_takeaways"):
        brief = str(record.get("brief_content") or "")
        bottom_line = str(record.get("bottom_line") or section_text(brief, "Bottom Line"))
        takeaways = str(record.get("key_takeaways") or section_text(brief, "Key Takeaways"))
        context = section_text(brief, "Strategic Context")
        implications = section_text(brief, "Implications")
        next_research = section_text(brief, "Recommended Next Research")

        if bottom_line:
            st.subheader("Bottom Line")
            st.markdown(bottom_line)

        if takeaways:
            st.subheader("Key Takeaways")
            st.markdown(takeaways)

        if context or implications:
            tab_context, tab_implications = st.tabs(["Strategic Context", "Implications"])
            with tab_context:
                st.markdown(context or "No strategic context has been written yet.")
            with tab_implications:
                st.markdown(implications or "No implication analysis has been written yet.")

        if next_research:
            with st.expander("Recommended next research", expanded=False):
                st.markdown(next_research)
        return

    brief_path = brief_markdown_path(record)
    if not brief_path or not brief_path.exists():
        st.info("No written brief has been added for this topic yet.")
        return

    brief = read_text(brief_path)
    bottom_line = section_text(brief, "Bottom Line")
    takeaways = section_text(brief, "Key Takeaways")
    context = section_text(brief, "Strategic Context")
    implications = section_text(brief, "Implications")
    next_research = section_text(brief, "Recommended Next Research")

    if bottom_line:
        st.subheader("Bottom Line")
        st.markdown(bottom_line)

    if takeaways:
        st.subheader("Key Takeaways")
        st.markdown(takeaways)

    if context or implications:
        tab_context, tab_implications = st.tabs(["Strategic Context", "Implications"])
        with tab_context:
            st.markdown(context or "No strategic context has been written yet.")
        with tab_implications:
            st.markdown(implications or "No implication analysis has been written yet.")

    if next_research:
        with st.expander("Recommended next research", expanded=False):
            st.markdown(next_research)


def display_topic(record: dict[str, Any], *, expanded_evidence: bool = True) -> None:
    title = record.get("title", record.get("slug", "Untitled topic"))
    slug = record.get("slug", "")
    category = record.get("category", "research-notes")
    topic_data = load_topic_data(slug)
    metadata = record.get("metadata", {})
    status = topic_data.get("status") or metadata.get("development_status", "developing")

    st.markdown(f"<div class='pi-kicker'>{category} / {status}</div>", unsafe_allow_html=True)
    st.header(title)
    st.markdown(f"<div class='pi-section-note'>{topic_summary(record)}</div>", unsafe_allow_html=True)

    st.caption(
        " | ".join(
            [
                f"Slug: {slug}",
                f"Data source: {record.get('source', 'legacy files')}",
                f"Updated: {record.get('updated_at', 'unknown')}",
                f"Topic note: {file_label(record.get('topic_path'))}",
                f"Brief: {file_label(record.get('brief_path'))}",
            ]
        )
    )

    st.divider()
    display_brief(record)

    if has_structured_data(topic_data):
        with st.expander("Structured evidence board", expanded=expanded_evidence):
            display_metric_cards(topic_data)
            display_comparisons(topic_data)
            display_timeline(topic_data)
            display_tables(topic_data)
            display_gaps(topic_data)
    else:
        st.info(
            "This topic has no structured evidence rows yet. Add metrics, timelines, "
            "comparisons, tables, and gaps in Postgres to unlock charts and evidence boards."
        )


def display_topic_cards(records: list[dict[str, Any]]) -> None:
    cols = st.columns(3)
    for idx, record in enumerate(records):
        slug = record.get("slug", "")
        topic_data = load_topic_data(slug)
        metric_count = len(topic_data.get("metrics", [])) if topic_data else 0
        gap_count = len(topic_data.get("data_gaps", [])) if topic_data else 0
        with cols[idx % 3]:
            st.markdown(f"**{record.get('title', slug)}**")
            st.caption(f"{record.get('category', 'research-notes')} | {record.get('updated_at', 'unknown')}")
            st.write(topic_summary(record))
            st.markdown(
                f"<span class='pi-chip'>{metric_count} metrics</span>"
                f"<span class='pi-chip'>{gap_count} gaps</span>"
                f"<span class='pi-chip'>{'structured' if has_structured_data(topic_data) else 'brief only'}</span>",
                unsafe_allow_html=True,
            )


with st.sidebar:
    st.title("Project India")
    st.caption("Public research intelligence dashboard")
    st.link_button("Open production app", PROD_URL)
    st.divider()

    page = st.radio(
        "Navigation",
        ["Insight Briefs", "Topic Explorer", "Research Library", "Operations"],
    )

    st.divider()
    st.caption("Insight pages show research conclusions. Local Postgres is the working data layer.")


topics = merged_topics()
runs = load_research_runs()
structured_topics = [
    topic for topic in topics if has_structured_data(load_topic_data(topic.get("slug", "")))
]


if page == "Insight Briefs":
    st.markdown("<div class='pi-kicker'>Project India</div>", unsafe_allow_html=True)
    st.title("Research Intelligence Dashboard")
    st.markdown(
        "<div class='pi-hero'>A public-facing surface for India's geopolitical, electoral, "
        "and sector research. This page leads with conclusions, evidence, timelines, and "
        "open questions rather than operational machinery.</div>",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tracked topics", len(topics))
    c2.metric("Structured datasets", len(structured_topics))
    c3.metric("Research runs", len(runs))
    c4.metric("Source logs", len(list(SOURCES_DIR.glob("*-sources.md"))))

    st.divider()
    st.subheader("Featured Research")

    featured = structured_topics or topics
    if not featured:
        st.info("No topics are indexed yet. Import or create research data in the local Postgres flow.")
    else:
        labels = [f"{record.get('title', record.get('slug'))} ({record.get('category')})" for record in featured]
        selected_label = st.selectbox("Select a topic", labels, label_visibility="collapsed")
        selected = featured[labels.index(selected_label)]
        display_topic(selected, expanded_evidence=True)

    st.divider()
    st.subheader("Coverage Map")
    display_topic_cards(topics)


elif page == "Topic Explorer":
    st.title("Topic Explorer")
    st.markdown("Browse research by category and open the full evidence board for each topic.")

    categories = ["all"] + sorted({topic.get("category", "research-notes") for topic in topics})
    selected_category = st.segmented_control("Category", categories, default="all")
    only_structured = st.toggle("Only topics with structured data", value=False)

    filtered = [
        topic
        for topic in topics
        if (selected_category == "all" or topic.get("category") == selected_category)
        and (not only_structured or load_topic_data(topic.get("slug", "")))
    ]

    if not filtered:
        st.info("No topics match this filter.")
    for record in filtered:
        with st.expander(record.get("title", record.get("slug", "Untitled")), expanded=False):
            display_topic(record, expanded_evidence=False)


elif page == "Research Library":
    st.title("Research Library")
    st.markdown("Indexed files that power the dashboard and future research reuse.")

    index = load_research_index()
    if not index:
        st.info("No research index has been generated yet.")
    else:
        df = pd.DataFrame(index)
        visible_cols = [
            "title",
            "slug",
            "category",
            "topic_path",
            "brief_path",
            "source_path",
            "topic_data_path",
            "updated_at",
        ]
        st.dataframe(df[[col for col in visible_cols if col in df.columns]], width="stretch", hide_index=True)

    with st.expander("Raw index JSON", expanded=False):
        st.json(index)


elif page == "Operations":
    st.title("Operations")
    st.markdown(
        "Database and deployment status live here. GitHub Actions research controls have been "
        "removed as part of the Postgres-first cleanup."
    )

    tab_database, tab_history, tab_config = st.tabs(
        ["Database", "Research History", "Configuration"]
    )

    with tab_database:
        st.subheader("Postgres")
        st.markdown(
            "Postgres is the research data layer for both local development and the deployed app. "
            "Use local Docker Postgres for development and a hosted Postgres URL in Streamlit secrets."
        )
        st.code(
            "\n".join(
                [
                    "docker compose up -d postgres",
                    "python3 -m pip install -e \".[db]\"",
                    "python3 -m project_india.cli db-init",
                    "python3 -m project_india.cli db-status",
                ]
            ),
            language="bash",
        )

        db_status = load_database_status()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Database", "Connected" if db_status["connected"] else "Unavailable")
        c1.metric("Indexed topics", len(topics))
        c2.metric("Structured datasets", len(structured_topics))
        c3.metric("Postgres topics", db_status["counts"].get("topics", 0))
        c4.metric("Source entries", db_status["counts"].get("source_entries", 0))

        if db_status["connected"]:
            with st.expander("Postgres table counts", expanded=False):
                st.dataframe(
                    pd.DataFrame(
                        [
                            {"table": table, "rows": count}
                            for table, count in db_status["counts"].items()
                        ]
                    ),
                    width="stretch",
                    hide_index=True,
                )
        else:
            st.warning("Postgres is not connected. Add PROJECT_INDIA_DATABASE_URL in Streamlit secrets.")
            st.caption(db_status["error"])

    with tab_history:
        if not runs:
            st.info("No research runs recorded yet.")
        else:
            df_runs = pd.DataFrame(runs)
            st.dataframe(df_runs, width="stretch", hide_index=True)
            if "timestamp" in df_runs.columns and "api_cost_usd" in df_runs.columns:
                trend = df_runs.copy()
                trend["timestamp"] = pd.to_datetime(trend["timestamp"], errors="coerce")
                trend = trend.dropna(subset=["timestamp"]).sort_values("timestamp")
                trend["cumulative_cost"] = trend["api_cost_usd"].fillna(0).cumsum()
                fig = px.line(
                    trend,
                    x="timestamp",
                    y="cumulative_cost",
                    color="title" if "title" in trend.columns else None,
                    markers=True,
                    title="Cumulative API cost over time",
                )
                st.plotly_chart(fig, width="stretch")

    with tab_config:
        st.markdown("**Production URL**")
        st.code(PROD_URL)
        st.markdown("**Archive inputs**")
        st.json(
            {
                "database_url_secret": DATABASE_URL_ENV,
                "postgres_schema": "db/schema.sql",
                "deployment_guide": "docs/DEPLOYMENT.md",
            }
        )


st.divider()
st.caption(
    f"Project India research dashboard | Production: {PROD_URL} | "
    f"Last rendered {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}"
)
