"""Project India public research dashboard."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


ROOT = Path(__file__).parent
CONFIG_PATH = ROOT / "research_config.json"
DATA_DIR = ROOT / "data" / "processed"
DOCS_DIR = ROOT / "docs"
REPORTS_DIR = ROOT / "analyses" / "reports"
SOURCES_DIR = ROOT / "sources"
PROD_URL = "https://project-india-nflujcnhq3f7xfj2d6q6sh.streamlit.app/"
TOPIC_INTAKE_WORKFLOW = "topic-intake-research.yml"
CONFIGURE_SCHEDULE_WORKFLOW = "configure-topic-schedule.yml"
INCREMENTAL_RESEARCH_WORKFLOW = "incremental-research.yml"
DEFAULT_OWNER = "knirantar"
DEFAULT_REPO = "Project-India"


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


@st.cache_data(ttl=300)
def load_config() -> dict[str, Any]:
    return read_json(CONFIG_PATH, {})


@st.cache_data(ttl=300)
def load_research_index() -> list[dict[str, Any]]:
    data = read_json(DATA_DIR / "research_index.json", [])
    return data if isinstance(data, list) else []


@st.cache_data(ttl=300)
def load_topic_data(slug: str) -> dict[str, Any]:
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


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def app_secret(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name, default)
    except (FileNotFoundError, KeyError):
        return default
    return str(value) if value is not None else default


def dispatch_workflow(workflow_file: str, inputs: dict[str, str]) -> tuple[bool, str]:
    token = app_secret("GITHUB_DISPATCH_TOKEN")
    owner = app_secret("GITHUB_OWNER", DEFAULT_OWNER)
    repo = app_secret("GITHUB_REPO", DEFAULT_REPO)
    if not token:
        return False, "GITHUB_DISPATCH_TOKEN is not configured in Streamlit secrets."

    response = requests.post(
        f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_file}/dispatches",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json={"ref": "main", "inputs": inputs},
        timeout=20,
    )

    if response.status_code == 204:
        return True, f"GitHub workflow started: {workflow_file}"
    return False, f"GitHub API returned {response.status_code}: {response.text[:500]}"


def dispatch_topic_workflow(
    *,
    title: str,
    slug: str,
    category: str,
    context: str,
    questions: str,
    sources: str,
    model: str,
    depth: str,
) -> tuple[bool, str]:
    return dispatch_workflow(
        TOPIC_INTAKE_WORKFLOW,
        {
            "title": title,
            "slug": slug,
            "category": category,
            "context": context,
            "questions": questions,
            "sources": sources,
            "research_model": model,
            "depth": depth,
        },
    )


def dispatch_schedule_workflow(
    *,
    slug: str,
    frequency: str,
    enabled: bool,
    time_utc: str,
    day_of_week: str,
    day_of_month: int,
    strategies: list[str],
) -> tuple[bool, str]:
    return dispatch_workflow(
        CONFIGURE_SCHEDULE_WORKFLOW,
        {
            "slug": slug,
            "frequency": frequency,
            "enabled": "true" if enabled else "false",
            "time_utc": time_utc,
            "day_of_week": day_of_week,
            "day_of_month": str(day_of_month),
            "strategies": ",".join(strategies),
        },
    )


def dispatch_incremental_workflow(
    *,
    slug: str,
    strategy: str,
    model: str,
) -> tuple[bool, str]:
    return dispatch_workflow(
        INCREMENTAL_RESEARCH_WORKFLOW,
        {
            "topic_slug": slug,
            "strategy": strategy,
            "model": model,
        },
    )


def topic_markdown_path(record: dict[str, Any]) -> Path | None:
    path = record.get("topic_path")
    return ROOT / path if path else None


def brief_markdown_path(record: dict[str, Any]) -> Path | None:
    path = record.get("brief_path")
    return ROOT / path if path else None


def topic_summary(record: dict[str, Any]) -> str:
    topic_path = topic_markdown_path(record)
    if topic_path and topic_path.exists():
        return first_paragraph(read_text(topic_path))
    brief_path = brief_markdown_path(record)
    if brief_path and brief_path.exists():
        return first_paragraph(read_text(brief_path))
    return "Research note is present in the index, but no readable summary has been added yet."


def merged_topics() -> list[dict[str, Any]]:
    config = load_config()
    index = load_research_index()
    by_slug: dict[str, dict[str, Any]] = {}

    for item in index:
        slug = item.get("slug")
        if slug:
            by_slug[slug] = dict(item)

    for topic in config.get("topics", []):
        slug = topic.get("slug")
        if not slug:
            continue
        record = by_slug.setdefault(slug, {})
        record.update(
            {
                "title": topic.get("title", record.get("title", slug)),
                "slug": slug,
                "category": topic.get("category", record.get("category", "research-notes")),
                "enabled": topic.get("enabled", True),
                "schedule": topic.get("schedule", {}),
                "strategy": topic.get("strategy", {}),
                "metadata": topic.get("metadata", {}),
            }
        )

    return sorted(
        by_slug.values(),
        key=lambda item: (
            0 if load_topic_data(item.get("slug", "")) else 1,
            item.get("category", ""),
            item.get("title", ""),
        ),
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
                f"Updated: {record.get('updated_at', 'unknown')}",
                f"Topic note: {file_label(record.get('topic_path'))}",
                f"Brief: {file_label(record.get('brief_path'))}",
            ]
        )
    )

    st.divider()
    display_brief(record)

    if topic_data:
        with st.expander("Structured evidence board", expanded=expanded_evidence):
            display_metric_cards(topic_data)
            display_comparisons(topic_data)
            display_timeline(topic_data)
            display_tables(topic_data)
            display_gaps(topic_data)
    else:
        st.info(
            "This topic has prose research but no structured topic-data file yet. "
            "Add metrics, timelines, comparisons, and tables under data/processed/topic_data/ "
            "to unlock charts and evidence boards."
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
                f"<span class='pi-chip'>{'structured' if topic_data else 'prose only'}</span>",
                unsafe_allow_html=True,
            )


with st.sidebar:
    st.title("Project India")
    st.caption("Public research intelligence dashboard")
    st.link_button("Open production app", PROD_URL)
    st.divider()

    page = st.radio(
        "Navigation",
        ["Start Research", "Insight Briefs", "Topic Explorer", "Research Library", "Operations"],
    )

    st.divider()
    st.caption("Insight pages show research conclusions. API spend and workflow controls are kept in Operations.")


topics = merged_topics()
config = load_config()
runs = load_research_runs()
structured_topics = [topic for topic in topics if load_topic_data(topic.get("slug", ""))]


if page == "Start Research":
    st.markdown("<div class='pi-kicker'>New Topic Intake</div>", unsafe_allow_html=True)
    st.title("Start a Research Topic")
    st.markdown(
        "<div class='pi-hero'>Give Project India a topic, your starting context, questions, "
        "and source leads. The app will trigger GitHub Actions to run source-backed research, "
        "write structured evidence, open a PR, and update the dashboard after the PR is merged. "
        "This flow does not generate a separate presentation deck because the app is the presentation surface.</div>",
        unsafe_allow_html=True,
    )

    secrets_ready = bool(app_secret("GITHUB_DISPATCH_TOKEN"))
    pin_configured = bool(app_secret("APP_ADMIN_PIN"))
    if not secrets_ready or not pin_configured:
        st.warning(
            "Workflow dispatch is not fully configured yet. Add Streamlit secrets "
            "`GITHUB_DISPATCH_TOKEN` and `APP_ADMIN_PIN` to enable one-click research starts."
        )

    with st.form("topic_intake_form"):
        title = st.text_input("Topic title", placeholder="Example: India's shipbuilding strategy")
        category = st.selectbox(
            "Category",
            ["sectors", "geopolitics", "internal-growth", "research-notes"],
            index=0,
        )
        slug = st.text_input("Slug", placeholder="Auto-generated from title if left blank")
        context = st.text_area(
            "Starting context",
            placeholder="What do you already know? Why does this topic matter? What angle should the research take?",
            height=160,
        )
        questions = st.text_area(
            "Questions to answer",
            placeholder="One question per line. Example: What are India's current capacity gaps?",
            height=140,
        )
        sources = st.text_area(
            "Source leads or URLs",
            placeholder="Paste any official sources, articles, PDFs, datasets, or names of institutions to check.",
            height=120,
        )

        c1, c2 = st.columns(2)
        with c1:
            model = st.text_input("Research model", value="gpt-5")
        with c2:
            depth = st.selectbox("Depth", ["deep", "standard"], index=0)

        admin_pin = st.text_input("Admin PIN", type="password")
        submitted = st.form_submit_button("Start GitHub research workflow")

    if submitted:
        clean_title = title.strip()
        clean_slug = slugify(slug or title)
        expected_pin = app_secret("APP_ADMIN_PIN")

        if not clean_title:
            st.error("Add a topic title first.")
        elif not clean_slug:
            st.error("Add a valid title or slug.")
        elif not expected_pin or admin_pin != expected_pin:
            st.error("Admin PIN is missing or incorrect.")
        else:
            ok, message = dispatch_topic_workflow(
                title=clean_title,
                slug=clean_slug,
                category=category,
                context=context.strip(),
                questions=questions.strip(),
                sources=sources.strip(),
                model=model.strip() or "gpt-5",
                depth=depth,
            )
            if ok:
                st.success(message)
                st.markdown(
                    "Research usually takes a few minutes. Watch the workflow in "
                    "[GitHub Actions](https://github.com/knirantar/Project-India/actions/workflows/topic-intake-research.yml). "
                    "If auto-merge is configured, refresh this app after completion. Otherwise merge the generated PR. "
                    "After the topic appears, use Operations -> Schedules to turn on incremental tracking."
                )
            else:
                st.error(message)

    st.divider()
    st.subheader("Required Setup")
    st.markdown(
        """
Add these Streamlit secrets:

```toml
GITHUB_OWNER = "knirantar"
GITHUB_REPO = "Project-India"
GITHUB_DISPATCH_TOKEN = "github_pat_or_classic_token_with_actions_write"
APP_ADMIN_PIN = "choose-a-private-pin"
```

Add these GitHub Actions secrets:

```text
OPENAI_API_KEY
PROJECT_INDIA_ADMIN_TOKEN   # optional, only if you want workflow PRs auto-merged
```
"""
    )


elif page == "Insight Briefs":
    st.markdown("<div class='pi-kicker'>Project India</div>", unsafe_allow_html=True)
    st.title("Research Intelligence Dashboard")
    st.markdown(
        "<div class='pi-hero'>A public-facing surface for India's geopolitical, electoral, "
        "and sector research. This page leads with conclusions, evidence, timelines, and "
        "open questions rather than workflow costs.</div>",
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
        st.info("No topics are indexed yet. Use Start Research to launch the first topic workflow.")
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
    st.markdown("Workflow, schedule, budget, and API-use controls live here so public insight pages stay clean.")

    tab_budget, tab_schedules, tab_history, tab_config = st.tabs(
        ["Budget", "Schedules", "Research History", "Configuration"]
    )

    with tab_budget:
        budget = config.get("budget", {})
        spent = float(budget.get("current_month_spent_usd", 0))
        limit = float(budget.get("monthly_limit_usd", 50))
        remaining = max(limit - spent, 0)
        c1, c2, c3 = st.columns(3)
        c1.metric("Monthly limit", f"${limit:.2f}")
        c2.metric("Current spend", f"${spent:.2f}")
        c3.metric("Remaining", f"${remaining:.2f}")
        st.progress(min(spent / limit, 1.0) if limit else 0)

        cost_rows = []
        for topic in config.get("topics", []):
            metadata = topic.get("metadata", {})
            cost_rows.append(
                {
                    "Topic": topic.get("title"),
                    "Last cost": metadata.get("last_cost_usd", 0),
                    "Calls this month": metadata.get("api_calls_month", 0),
                    "Total cost this month": metadata.get("total_cost_month", 0),
                }
            )
        if cost_rows:
            st.dataframe(pd.DataFrame(cost_rows), width="stretch", hide_index=True)

    with tab_schedules:
        rows = []
        for topic in config.get("topics", []):
            schedule = topic.get("schedule", {})
            rows.append(
                {
                    "Topic": topic.get("title"),
                    "Enabled": topic.get("enabled", True),
                    "Frequency": schedule.get("frequency"),
                    "Time UTC": schedule.get("time_utc"),
                    "Last run": schedule.get("last_run_date"),
                    "Next run": schedule.get("next_scheduled_run"),
                    "Strategy rotation": ", ".join(topic.get("strategy", {}).get("rotation", [])),
                }
            )
        if rows:
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        else:
            st.info("No topics have been added to research_config.json yet.")

        st.divider()
        st.subheader("Configure Incremental Tracking")
        st.markdown(
            "Use this after the first deep research run. It sets a frequency for focused updates "
            "so the scheduled workflow checks the topic hourly but only researches it when it is due."
        )

        configured_topics = config.get("topics", [])
        if not configured_topics:
            st.info("Start a topic first, then return here to configure its incremental cadence.")
        else:
            topic_options = {
                f"{topic.get('title', topic.get('slug'))} ({topic.get('slug')})": topic
                for topic in configured_topics
            }
            selected_schedule_label = st.selectbox(
                "Topic to track",
                list(topic_options),
                key="schedule_topic",
            )
            selected_schedule_topic = topic_options[selected_schedule_label]
            current_schedule = selected_schedule_topic.get("schedule", {})
            current_strategy = selected_schedule_topic.get("strategy", {})
            current_rotation = [
                strategy
                for strategy in current_strategy.get("rotation", ["developments", "gaps", "factcheck"])
                if strategy in {"developments", "gaps", "factcheck"}
            ] or ["developments", "gaps", "factcheck"]

            with st.form("configure_schedule_form"):
                c1, c2 = st.columns(2)
                with c1:
                    frequency = st.selectbox(
                        "Frequency",
                        ["manual", "daily", "weekly", "monthly"],
                        index=["manual", "daily", "weekly", "monthly"].index(
                            current_schedule.get("frequency", "manual")
                            if current_schedule.get("frequency") in {"manual", "daily", "weekly", "monthly"}
                            else "manual"
                        ),
                    )
                    enabled = st.checkbox(
                        "Enable scheduled tracking",
                        value=bool(selected_schedule_topic.get("enabled", False)),
                        disabled=frequency == "manual",
                    )
                    time_utc = st.text_input(
                        "Run time UTC",
                        value=current_schedule.get("time_utc") or "06:00",
                        help="Use HH:MM, for example 06:00. The scheduler checks once every hour.",
                    )
                with c2:
                    day_of_week = st.selectbox(
                        "Weekly day",
                        ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
                        index=[
                            "monday",
                            "tuesday",
                            "wednesday",
                            "thursday",
                            "friday",
                            "saturday",
                            "sunday",
                        ].index(current_schedule.get("day_of_week", "monday"))
                        if current_schedule.get("day_of_week", "monday")
                        in {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}
                        else 0,
                    )
                    day_of_month = st.number_input(
                        "Monthly day",
                        min_value=1,
                        max_value=28,
                        value=int(current_schedule.get("day_of_month") or 1),
                    )
                    strategies = st.multiselect(
                        "Incremental strategy rotation",
                        ["developments", "gaps", "factcheck"],
                        default=current_rotation,
                    )

                schedule_pin = st.text_input("Admin PIN", type="password", key="schedule_pin")
                schedule_submitted = st.form_submit_button("Save schedule through GitHub workflow")

            if schedule_submitted:
                expected_pin = app_secret("APP_ADMIN_PIN")
                if not expected_pin or schedule_pin != expected_pin:
                    st.error("Admin PIN is missing or incorrect.")
                elif not strategies:
                    st.error("Choose at least one incremental strategy.")
                else:
                    ok, message = dispatch_schedule_workflow(
                        slug=selected_schedule_topic.get("slug", ""),
                        frequency=frequency,
                        enabled=enabled and frequency != "manual",
                        time_utc=time_utc.strip() or "06:00",
                        day_of_week=day_of_week,
                        day_of_month=int(day_of_month),
                        strategies=strategies,
                    )
                    if ok:
                        st.success(message)
                        st.markdown(
                            "[Watch schedule configuration in GitHub Actions]"
                            "(https://github.com/knirantar/Project-India/actions/workflows/configure-topic-schedule.yml)."
                        )
                    else:
                        st.error(message)

        st.divider()
        st.subheader("Run One Incremental Update Now")
        st.markdown(
            "This triggers the focused incremental workflow for an existing topic. "
            "It reuses existing repo memory and runs only the selected update strategy."
        )
        if configured_topics:
            manual_options = {
                f"{topic.get('title', topic.get('slug'))} ({topic.get('slug')})": topic
                for topic in configured_topics
            }
            with st.form("manual_incremental_form"):
                manual_label = st.selectbox("Topic", list(manual_options), key="manual_increment_topic")
                manual_strategy = st.selectbox(
                    "Strategy",
                    ["rotate", "developments", "gaps", "factcheck"],
                    help="Rotate uses the topic's configured strategy rotation.",
                )
                manual_model = st.text_input("Model", value="gpt-5", key="manual_increment_model")
                manual_pin = st.text_input("Admin PIN", type="password", key="manual_increment_pin")
                manual_submitted = st.form_submit_button("Run incremental research now")

            if manual_submitted:
                expected_pin = app_secret("APP_ADMIN_PIN")
                selected_manual_topic = manual_options[manual_label]
                if not expected_pin or manual_pin != expected_pin:
                    st.error("Admin PIN is missing or incorrect.")
                else:
                    ok, message = dispatch_incremental_workflow(
                        slug=selected_manual_topic.get("slug", ""),
                        strategy=manual_strategy,
                        model=manual_model.strip() or "gpt-5",
                    )
                    if ok:
                        st.success(message)
                        st.markdown(
                            "[Watch incremental research in GitHub Actions]"
                            "(https://github.com/knirantar/Project-India/actions/workflows/incremental-research.yml)."
                        )
                    else:
                        st.error(message)

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
        st.markdown("**Raw research configuration**")
        st.json(config)


st.divider()
st.caption(
    f"Project India research dashboard | Production: {PROD_URL} | "
    f"Last rendered {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}"
)
