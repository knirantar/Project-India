"""Project India Research Dashboard — Streamlit App"""

import json
import os
from pathlib import Path
from datetime import datetime, UTC, timedelta
import re

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Project India Research Dashboard",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for branding
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .topic-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .status-active {
        color: #00b894;
        font-weight: bold;
    }
    .status-disabled {
        color: #d63031;
        font-weight: bold;
    }
    h1 {
        color: #1e3c72;
    }
    h2 {
        color: #2a5298;
    }
</style>
""", unsafe_allow_html=True)

# Constants
ROOT = Path(__file__).parent
CONFIG_PATH = ROOT / "research_config.json"
DATA_DIR = ROOT / "data" / "processed"
DOCS_DIR = ROOT / "docs"

# ============================================================================
# DATA LOADING & UTILITIES
# ============================================================================

@st.cache_data(ttl=300)  # Refresh every 5 minutes
def load_config():
    """Load research configuration."""
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {}

@st.cache_data(ttl=300)
def load_research_index():
    """Load research index."""
    index_path = DATA_DIR / "research_index.json"
    if index_path.exists():
        return json.loads(index_path.read_text(encoding="utf-8"))
    return {}

@st.cache_data(ttl=300)
def load_all_runs():
    """Load all research run records."""
    runs_dir = DATA_DIR / "research_runs"
    runs = []
    if runs_dir.exists():
        for run_file in sorted(runs_dir.glob("*.json"), reverse=True):
            try:
                run_data = json.loads(run_file.read_text(encoding="utf-8"))
                runs.append(run_data)
            except:
                pass
    return runs

@st.cache_data(ttl=300)
def load_topic_data(slug):
    """Load structured topic data."""
    data_path = DATA_DIR / "topic_data" / f"{slug}.json"
    if data_path.exists():
        return json.loads(data_path.read_text(encoding="utf-8"))
    return {}

def get_topic_summary(slug):
    """Get brief summary of a topic from docs."""
    for category in ["geopolitics", "internal-growth", "sectors", "research-notes"]:
        topic_path = DOCS_DIR / category / f"{slug}.md"
        if topic_path.exists():
            content = topic_path.read_text(encoding="utf-8")
            # Extract first paragraph
            lines = [l for l in content.split("\n") if l.strip() and not l.startswith("#")]
            return " ".join(lines[:3])[:200] + "..."
    return "No content available"

def get_status_color(status):
    """Return color for status badge."""
    colors = {
        "mature": "#00b894",
        "active": "#fdcb6e",
        "stub": "#e17055",
        "disabled": "#d63031",
    }
    return colors.get(status, "#636e72")

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

with st.sidebar:
    st.title("🇮🇳 Project India")
    st.divider()
    
    page = st.radio(
        "Navigation",
        ["📊 Overview", "🌍 Geopolitics", "🏛️ Internal Growth", "⚙️ Sectors", 
         "📈 Research History", "⚙️ Admin"],
        use_container_width=True,
    )
    
    st.divider()
    
    config = load_config()
    if config:
        st.subheader("💰 Budget Status")
        budget = config.get("budget", {})
        spent = budget.get("current_month_spent_usd", 0)
        limit = budget.get("monthly_limit_usd", 50)
        remaining = limit - spent
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Spent", f"${spent:.2f}")
        with col2:
            st.metric("Remaining", f"${remaining:.2f}")
        
        # Progress bar
        progress = min(spent / limit, 1.0)
        st.progress(progress)
        
        if progress > 0.8:
            st.warning("⚠️ Budget > 80%")

# ============================================================================
# PAGE: OVERVIEW
# ============================================================================

if page == "📊 Overview":
    st.title("📊 Project India Research Dashboard")
    st.markdown("Automated research on India's geopolitics, internal growth, and sectors — powered by GPT-5 and optimized for accuracy.")
    st.divider()
    
    config = load_config()
    index = load_research_index()
    
    if not config or "topics" not in config:
        st.error("No configuration found. Please check research_config.json.")
        st.stop()
    
    # Key Metrics
    st.subheader("📈 Key Metrics")
    
    topics = config.get("topics", [])
    enabled_topics = [t for t in topics if t.get("enabled", True)]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Topics", len(topics))
    with col2:
        st.metric("Active Research", len(enabled_topics))
    with col3:
        budget = config.get("budget", {})
        st.metric("Monthly Budget", f"${budget.get('monthly_limit_usd', 0)}")
    with col4:
        runs = load_all_runs()
        st.metric("Research Runs", len(runs))
    
    st.divider()
    
    # Topics Grid
    st.subheader("📑 Topics")
    
    # Filter by status
    col1, col2 = st.columns([3, 1])
    with col1:
        show_disabled = st.checkbox("Show disabled topics", value=False)
    
    display_topics = topics if show_disabled else enabled_topics
    
    # Display topics as cards
    cols = st.columns(3)
    for idx, topic in enumerate(display_topics):
        col = cols[idx % 3]
        
        with col:
            status = topic.get("metadata", {}).get("development_status", "unknown")
            enabled = topic.get("enabled", True)
            
            status_color = get_status_color(status)
            status_text = "🟢 ACTIVE" if enabled else "🔴 DISABLED"
            
            st.markdown(f"""
            <div class="topic-card">
                <h4>{topic['title']}</h4>
                <p><small>{get_topic_summary(topic['slug'])}</small></p>
                <p>
                    <b>Schedule:</b> {topic['schedule']['frequency'].capitalize()}<br>
                    <b>Status:</b> {status_text}<br>
                    <b>Last Run:</b> {topic['schedule'].get('last_run_date', 'Never')}<br>
                    <b>Cost (month):</b> ${topic.get('metadata', {}).get('last_cost_usd', 0):.2f}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Research Cost Breakdown
    st.subheader("💸 Cost Breakdown")
    
    cost_data = []
    for topic in topics:
        cost_data.append({
            "Topic": topic["title"],
            "Cost": topic.get("metadata", {}).get("last_cost_usd", 0),
            "Calls": topic.get("metadata", {}).get("api_calls_month", 0),
        })
    
    df_costs = pd.DataFrame(cost_data)
    
    if not df_costs.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                df_costs,
                values="Cost",
                names="Topic",
                title="Cost Distribution",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                df_costs,
                x="Topic",
                y="Calls",
                title="API Calls by Topic",
                color="Topic",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE: GEOPOLITICS
# ============================================================================

elif page == "🌍 Geopolitics":
    st.title("🌍 Geopolitics")
    st.markdown("Strategic analysis of India's international relations and global positioning.")
    st.divider()
    
    config = load_config()
    geopolitics_topics = [t for t in config.get("topics", []) if t["category"] == "geopolitics"]
    
    if not geopolitics_topics:
        st.info("No geopolitics topics configured yet.")
    else:
        for topic in geopolitics_topics:
            with st.expander(f"📌 {topic['title']}", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    status = topic.get("metadata", {}).get("development_status", "unknown")
                    st.metric("Status", status.upper())
                
                with col2:
                    st.metric("Schedule", topic["schedule"]["frequency"].capitalize())
                
                with col3:
                    st.metric("Monthly Cost", f"${topic.get('metadata', {}).get('last_cost_usd', 0):.2f}")
                
                st.markdown("**Topic Summary:**")
                st.write(get_topic_summary(topic["slug"]))
                
                # Load and display structured data if available
                topic_data = load_topic_data(topic["slug"])
                
                if topic_data:
                    st.markdown("**Key Metrics:**")
                    
                    # Display metrics as columns
                    metrics = topic_data.get("metrics", {})
                    if metrics:
                        metric_cols = st.columns(len(metrics))
                        for idx, (metric_name, metric_value) in enumerate(metrics.items()):
                            with metric_cols[idx % len(metric_cols)]:
                                st.metric(metric_name, metric_value)
                    
                    # Display comparisons
                    if "comparisons" in topic_data:
                        st.markdown("**Comparisons:**")
                        comparisons = topic_data["comparisons"]
                        if isinstance(comparisons, list) and comparisons:
                            df_comp = pd.DataFrame(comparisons)
                            st.dataframe(df_comp, use_container_width=True)
                    
                    # Display timeline
                    if "timeline" in topic_data:
                        st.markdown("**Timeline:**")
                        timeline = topic_data["timeline"]
                        if isinstance(timeline, list) and timeline:
                            df_timeline = pd.DataFrame(timeline)
                            st.dataframe(df_timeline, use_container_width=True)

# ============================================================================
# PAGE: INTERNAL GROWTH
# ============================================================================

elif page == "🏛️ Internal Growth":
    st.title("🏛️ Internal Growth")
    st.markdown("Analysis of India's internal development, governance, and elections.")
    st.divider()
    
    config = load_config()
    internal_topics = [t for t in config.get("topics", []) if t["category"] == "internal-growth"]
    
    if not internal_topics:
        st.info("No internal growth topics configured yet.")
    else:
        for topic in internal_topics:
            with st.expander(f"📌 {topic['title']}", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    status = topic.get("metadata", {}).get("development_status", "unknown")
                    st.metric("Status", status.upper())
                
                with col2:
                    st.metric("Schedule", topic["schedule"]["frequency"].capitalize())
                
                with col3:
                    st.metric("Monthly Cost", f"${topic.get('metadata', {}).get('last_cost_usd', 0):.2f}")
                
                st.markdown("**Topic Summary:**")
                st.write(get_topic_summary(topic["slug"]))
                
                # Load and display structured data if available
                topic_data = load_topic_data(topic["slug"])
                
                if topic_data:
                    st.markdown("**Key Metrics:**")
                    
                    # Display metrics as columns
                    metrics = topic_data.get("metrics", {})
                    if metrics:
                        metric_cols = st.columns(len(metrics))
                        for idx, (metric_name, metric_value) in enumerate(metrics.items()):
                            with metric_cols[idx % len(metric_cols)]:
                                st.metric(metric_name, metric_value)
                    
                    # Display comparisons
                    if "comparisons" in topic_data:
                        st.markdown("**Comparisons:**")
                        comparisons = topic_data["comparisons"]
                        if isinstance(comparisons, list) and comparisons:
                            df_comp = pd.DataFrame(comparisons)
                            st.dataframe(df_comp, use_container_width=True)

# ============================================================================
# PAGE: SECTORS
# ============================================================================

elif page == "⚙️ Sectors":
    st.title("⚙️ Sectors")
    st.markdown("India's sectoral analysis: semiconductors, infrastructure, economy, and strategic industries.")
    st.divider()
    
    config = load_config()
    sectors_topics = [t for t in config.get("topics", []) if t["category"] == "sectors"]
    
    if not sectors_topics:
        st.info("No sector topics configured yet.")
    else:
        for topic in sectors_topics:
            with st.expander(f"📌 {topic['title']}", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    status = topic.get("metadata", {}).get("development_status", "unknown")
                    st.metric("Status", status.upper())
                
                with col2:
                    st.metric("Schedule", topic["schedule"]["frequency"].capitalize())
                
                with col3:
                    st.metric("Monthly Cost", f"${topic.get('metadata', {}).get('last_cost_usd', 0):.2f}")
                
                st.markdown("**Topic Summary:**")
                st.write(get_topic_summary(topic["slug"]))
                
                # Load and display structured data if available
                topic_data = load_topic_data(topic["slug"])
                
                if topic_data:
                    st.markdown("**Key Metrics:**")
                    
                    # Display metrics as columns
                    metrics = topic_data.get("metrics", {})
                    if metrics:
                        metric_cols = st.columns(len(metrics))
                        for idx, (metric_name, metric_value) in enumerate(metrics.items()):
                            with metric_cols[idx % len(metric_cols)]:
                                st.metric(metric_name, metric_value)

# ============================================================================
# PAGE: RESEARCH HISTORY
# ============================================================================

elif page == "📈 Research History":
    st.title("📈 Research History")
    st.markdown("Track all incremental research runs, costs, and changes over time.")
    st.divider()
    
    runs = load_all_runs()
    
    if not runs:
        st.info("No research runs recorded yet.")
    else:
        st.subheader(f"📊 {len(runs)} Research Runs")
        
        # Create dataframe from runs
        runs_data = []
        for run in runs:
            runs_data.append({
                "Timestamp": run.get("timestamp", "Unknown"),
                "Topic": run.get("title", "Unknown"),
                "Strategy": run.get("strategy", "Unknown"),
                "Cost": run.get("api_cost_usd", 0),
                "Summary": run.get("summary", "No summary")[:100] + "...",
            })
        
        df_runs = pd.DataFrame(runs_data)
        
        # Display table
        st.dataframe(df_runs, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # Cost trend
        st.subheader("💰 Cost Trend")
        df_runs["Timestamp"] = pd.to_datetime(df_runs["Timestamp"])
        df_runs = df_runs.sort_values("Timestamp")
        df_runs["Cumulative Cost"] = df_runs["Cost"].cumsum()
        
        fig = px.line(
            df_runs,
            x="Timestamp",
            y="Cumulative Cost",
            title="Cumulative API Cost Over Time",
            markers=True,
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Strategy distribution
        st.subheader("🎯 Strategy Distribution")
        strategy_counts = df_runs["Strategy"].value_counts()
        
        fig = px.pie(
            values=strategy_counts.values,
            names=strategy_counts.index,
            title="Research Runs by Strategy",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE: ADMIN
# ============================================================================

elif page == "⚙️ Admin":
    st.title("⚙️ Administration")
    st.markdown("Manage topics, schedules, and research configuration.")
    st.divider()
    
    admin_tab1, admin_tab2, admin_tab3 = st.tabs(
        ["Topics", "Schedules", "Configuration"]
    )
    
    with admin_tab1:
        st.subheader("📝 Topic Management")
        
        config = load_config()
        topics = config.get("topics", [])
        
        st.markdown("**Current Topics:**")
        for topic in topics:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{topic['title']}** ({topic['slug']})")
            with col2:
                status = "🟢 Active" if topic.get("enabled") else "🔴 Disabled"
                st.write(status)
            with col3:
                if st.button("Edit", key=f"edit_{topic['slug']}"):
                    st.info("Edit functionality coming soon. Use GitHub Issues to modify topics.")
        
        st.divider()
        
        st.markdown("**Add New Topic:**")
        st.info("To add a new topic, create a GitHub Issue using the 'Add New Research Topic' template.")
        st.markdown("👉 [Go to GitHub Issues](https://github.com/knirantar/Project-India/issues/new?template=01-add-topic.md)")
    
    with admin_tab2:
        st.subheader("⏰ Schedule Management")
        
        config = load_config()
        topics = config.get("topics", [])
        
        st.markdown("**Current Schedules:**")
        for topic in topics:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**{topic['title']}**")
            with col2:
                st.write(f"Frequency: {topic['schedule']['frequency']}")
            with col3:
                st.write(f"Time: {topic['schedule']['time_utc']} UTC")
            with col4:
                next_run = topic['schedule'].get('next_scheduled_run', 'Unknown')
                st.write(f"Next: {next_run}")
        
        st.divider()
        
        st.markdown("**Modify Schedule:**")
        st.info("To modify a topic's schedule, create a GitHub Issue using the 'Modify Research Schedule' template.")
        st.markdown("👉 [Go to GitHub Issues](https://github.com/knirantar/Project-India/issues/new?template=02-modify-schedule.md)")
    
    with admin_tab3:
        st.subheader("⚙️ Configuration")
        
        config = load_config()
        
        st.markdown("**Budget Configuration:**")
        budget = config.get("budget", {})
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Monthly Limit", f"${budget.get('monthly_limit_usd', 50)}")
        with col2:
            st.metric("Current Month Spent", f"${budget.get('current_month_spent_usd', 0):.2f}")
        with col3:
            remaining = budget.get("monthly_limit_usd", 50) - budget.get("current_month_spent_usd", 0)
            st.metric("Remaining", f"${remaining:.2f}")
        
        st.divider()
        
        st.markdown("**Research Strategies:**")
        strategies = config.get("strategies", {})
        for strategy_name, strategy_config in strategies.items():
            st.markdown(f"**{strategy_name.upper()}**")
            st.write(f"Description: {strategy_config.get('description', 'N/A')}")
            st.write(f"Est. Cost: ${strategy_config.get('api_cost_estimate_usd', 0)}")
        
        st.divider()
        
        st.markdown("**Raw Configuration:**")
        st.json(config)

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
---
<div style="text-align: center;">
    <p>🇮🇳 <b>Project India</b> — Research Dashboard</p>
    <p><small>Powered by Streamlit • Data updated every 5 minutes</small></p>
    <p><small>Last Updated: {}</small></p>
</div>
""".format(datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")), unsafe_allow_html=True)
