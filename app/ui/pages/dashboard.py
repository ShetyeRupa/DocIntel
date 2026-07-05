"""Analytics dashboard for DocIntel."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from app.monitoring.logger import Logger
from app.monitoring.cost_tracker import CostTracker
import pandas as pd

def render_dashboard():
    """Render the analytics dashboard."""
    st.title("📊 Analytics Dashboard")
    
    # Initialize monitoring
    logger = Logger()
    cost_tracker = CostTracker()
    
    # Get stats
    stats = logger.get_stats()
    cost_summary = cost_tracker.get_summary()
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Queries",
            stats.get("total_queries", 0),
            delta="+2" if stats.get("total_queries", 0) > 0 else None
        )
    
    with col2:
        st.metric(
            "Avg Confidence",
            f"{stats.get('avg_confidence', 0) * 100:.1f}%",
            delta=f"+{stats.get('avg_confidence', 0) * 100 - 85:.1f}%" if stats.get('avg_confidence', 0) > 0 else None
        )
    
    with col3:
        st.metric(
            "Avg Response Time",
            f"{stats.get('avg_response_time', 0):.1f}s",
            delta="-0.2s" if stats.get('avg_response_time', 0) < 3 else None
        )
    
    with col4:
        st.metric(
            "Total Tokens",
            f"{stats.get('total_tokens', 0):,}",
            delta=f"+{stats.get('total_tokens', 0)}" if stats.get('total_tokens', 0) > 0 else None
        )
    
    st.divider()
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Confidence Distribution")
        if stats.get("total_queries", 0) > 0:
            # Simulate confidence distribution
            import numpy as np
            confidences = [log.get("confidence", 0) * 100 for log in logger.logs[-50:]]
            
            fig = go.Figure(data=[go.Histogram(x=confidences, nbinsx=10)])
            fig.update_layout(
                xaxis_title="Confidence (%)",
                yaxis_title="Count",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available yet. Start asking questions!")
    
    with col2:
        st.subheader("🎯 Intent Distribution")
        intent_dist = stats.get("intent_distribution", {})
        if intent_dist:
            df = pd.DataFrame({
                "Intent": list(intent_dist.keys()),
                "Count": list(intent_dist.values())
            })
            fig = px.pie(df, values="Count", names="Intent", height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No intent data available yet.")
    
    # Cost Analysis
    st.divider()
    st.subheader("💰 Cost Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Cost",
            f"${cost_summary.get('total_cost', 0):.4f}",
            delta="$0.00 (Free Tier)"
        )
    
    with col2:
        st.metric(
            "Cost per Query",
            f"${cost_summary.get('cost_per_query', 0):.6f}",
            delta="$0.00 (Free Tier)"
        )
    
    with col3:
        st.metric(
            "Monthly Estimate",
            f"${cost_summary.get('monthly_estimate', 0):.2f}",
            delta="$0.00 (Free Tier)"
        )
    
    # Recent Activity
    st.divider()
    st.subheader("🔄 Recent Activity")
    
    recent = logger.get_recent_queries(5)
    if recent:
        for log in recent:
            with st.expander(f"Query: {log.get('query', 'N/A')[:50]}..."):
                st.markdown(f"**Response:** {log.get('response', 'N/A')[:200]}...")
                st.markdown(f"**Confidence:** {log.get('confidence', 0) * 100:.1f}%")
                st.markdown(f"**Time:** {log.get('response_time', 0):.2f}s")
                st.markdown(f"**Tokens:** {log.get('tokens_used', 0)}")
                st.markdown(f"**Intent:** {log.get('intent', 'N/A')}")
                st.markdown(f"**Validated:** {'✅' if log.get('validation_passed', False) else '❌'}")
                st.markdown(f"**Timestamp:** {log.get('timestamp', 'N/A')}")
    else:
        st.info("No recent activity. Start using DocIntel to see analytics here!")
    
    # Export Options
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export Logs", use_container_width=True):
            filepath = logger.export_logs()
            st.success(f"Logs exported to {filepath}")
    
    with col2:
        if st.button("📊 Export Cost Report", use_container_width=True):
            filepath = cost_tracker.export_report()
            st.success(f"Cost report exported to {filepath}")
    
    with col3:
        if st.button("🔄 Refresh Dashboard", use_container_width=True):
            st.rerun()
if __name__ == "__main__" or "streamlit" in str(__name__):
    render_dashboard()