import streamlit as st
import asyncio
import os
from datetime import datetime
import json

# Page config
st.set_page_config(
    page_title="AI Competitor Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🔍 AI Competitor Intelligence")
st.markdown("*Autonomous market research powered by 100% open-source AI*")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    groq_api_key = st.text_input(
        "Groq API Key",
        type="password",
        help="Get free API key at https://console.groq.com",
        value=os.getenv("GROQ_API_KEY", "")
    )
    
    if not groq_api_key:
        st.warning("⚠️ Please enter your Groq API key to start")
        st.markdown("[Get Free API Key →](https://console.groq.com)")
        st.stop()
    
    # Save to environment
    os.environ["GROQ_API_KEY"] = groq_api_key
    
    st.success("✅ API Key configured")
    
    st.markdown("---")
    
    # Research depth
    depth = st.selectbox(
        "Research Depth",
        ["Quick (2-3 min)", "Standard (5-7 min)", "Deep (10-15 min)"],
        index=1
    )
    
    depth_mapping = {
        "Quick (2-3 min)": "quick",
        "Standard (5-7 min)": "standard",
        "Deep (10-15 min)": "deep"
    }
    
    st.markdown("---")
    st.caption("Built with LangChain, Groq, and Streamlit")


# Main content
tab1, tab2, tab3 = st.tabs(["🎯 New Research", "📊 Results", "ℹ️ About"])

with tab1:
    st.header("Start New Research")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        company_name = st.text_input(
            "Company Name",
            placeholder="e.g., Stripe, Notion, Figma, OpenAI",
            help="Enter the exact company name"
        )
    
    with col2:
        st.write("")
        st.write("")
        start_button = st.button("🚀 Start Research", type="primary", use_container_width=True)
    
    if start_button:
        if not company_name:
            st.error("❌ Please enter a company name")
        else:
            # Import after API key is set
            from agents.orchestrator import run_research
            
            with st.spinner(f"🔍 Researching {company_name}..."):
                try:
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Run research
                    result = asyncio.run(run_research(
                        company_name=company_name,
                        depth=depth_mapping[depth],
                        progress_callback=lambda p, s: (
                            progress_bar.progress(p/100),
                            status_text.text(f"Status: {s} ({p}%)")
                        )
                    ))
                    
                    # Store in session state
                    st.session_state['latest_result'] = result
                    st.session_state['latest_company'] = company_name
                    
                    st.success("✅ Research complete!")
                    
                    # Display results
                    st.markdown("---")
                    display_results(result, company_name)
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.exception(e)

with tab2:
    st.header("📊 Latest Results")
    
    if 'latest_result' in st.session_state:
        company = st.session_state.get('latest_company', 'Unknown')
        result = st.session_state['latest_result']
        
        display_results(result, company)
    else:
        st.info("👆 Run a research first to see results here")

with tab3:
    st.header("About This Tool")
    
    st.markdown("""
    ### 🎯 What it does
    
    This AI agent automatically researches any company and provides:
    
    - 📊 **Company Overview** - Background, size, market position
    - 💪 **SWOT Analysis** - Strengths, Weaknesses, Opportunities, Threats
    - 💰 **Financial Health** - Funding, revenue, growth metrics
    - 🎨 **Product Analysis** - Features, pricing, positioning
    - 📰 **News & Sentiment** - Recent updates and market perception
    - 💡 **Strategic Recommendations** - Actionable insights
    
    ### 🛠️ Technology Stack
    
    - **LLM**: Groq (Llama 3.1 70B) - Lightning fast inference
    - **Framework**: LangChain - Agent orchestration
    - **Scraping**: BeautifulSoup, Trafilatura
    - **UI**: Streamlit
    
    ### 🆓 100% Free & Open Source
    
    - No vendor lock-in
    - Runs on free API tiers
    - Fully customizable
    - [View on GitHub →](https://github.com/yourusername/competitor-intelligence-ai)
    
    ### 🚀 Getting Started
    
    1. Get free Groq API key: https://console.groq.com
    2. Enter API key in sidebar
    3. Enter company name
    4. Click "Start Research"
    
    ### 📝 Example Companies to Try
    
    - **Tech**: Stripe, Notion, Figma, Linear, Vercel
    - **AI**: OpenAI, Anthropic, Hugging Face, Replicate
    - **SaaS**: Salesforce, HubSpot, Intercom, Zendesk
    
    ---
    
    Made with ❤️ using open-source AI
    """)


def display_results(result: dict, company_name: str):
    """Display research results"""
    
    synthesis = result.get('synthesis', {})
    
    # Executive Summary
    st.subheader("📋 Executive Summary")
    summary = synthesis.get('executive_summary', 'No summary available')
    st.info(summary)
    
    st.markdown("---")
    
    # Key Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        score = synthesis.get('competitive_score', 0)
        st.metric(
            "Competitive Score",
            f"{score}/100",
            help="Overall competitive strength"
        )
    
    with col2:
        health = synthesis.get('financial_health', {})
        health_score = health.get('health_score', 0)
        st.metric(
            "Financial Health",
            f"{health_score}/100",
            help="Financial stability and growth"
        )
    
    with col3:
        product = synthesis.get('product_analysis', {})
        pmf = product.get('product_market_fit_score', 0)
        st.metric(
            "Product-Market Fit",
            f"{pmf}/100",
            help="How well product matches market needs"
        )
    
    st.markdown("---")
    
    # Company Overview
    st.subheader("🏢 Company Overview")
    overview = synthesis.get('company_overview', {})
    
    if overview:
        st.write(f"**Background:** {overview.get('background', 'N/A')}")
        st.write(f"**Size & Scale:** {overview.get('size_and_scale', 'N/A')}")
        st.write(f"**Market Position:** {overview.get('market_position', 'N/A')}")
    
    st.markdown("---")
    
    # SWOT Analysis
    st.subheader("📊 SWOT Analysis")
    swot = synthesis.get('swot_analysis', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("💪 Strengths", expanded=True):
            strengths = swot.get('strengths', [])
            if strengths:
                for s in strengths:
                    st.write(f"✓ {s}")
            else:
                st.write("No data")
        
        with st.expander("🎯 Opportunities", expanded=True):
            opps = swot.get('opportunities', [])
            if opps:
                for o in opps:
                    st.write(f"✓ {o}")
            else:
                st.write("No data")
    
    with col2:
        with st.expander("⚠️ Weaknesses", expanded=True):
            weaknesses = swot.get('weaknesses', [])
            if weaknesses:
                for w in weaknesses:
                    st.write(f"⚠ {w}")
            else:
                st.write("No data")
        
        with st.expander("🚨 Threats", expanded=True):
            threats = swot.get('threats', [])
            if threats:
                for t in threats:
                    st.write(f"⚠ {t}")
            else:
                st.write("No data")
    
    st.markdown("---")
    
    # Product Analysis
    st.subheader("🎨 Product Analysis")
    product_analysis = synthesis.get('product_analysis', {})
    
    if product_analysis:
        st.write(f"**Core Offerings:** {product_analysis.get('core_offerings', 'N/A')}")
        st.write(f"**Pricing Strategy:** {product_analysis.get('pricing_strategy', 'N/A')}")
        
        differentiators = product_analysis.get('differentiators', [])
        if differentiators:
            st.write("**Key Differentiators:**")
            for d in differentiators:
                st.write(f"- {d}")
    
    st.markdown("---")
    
    # Strategic Recommendations
    st.subheader("💡 Strategic Recommendations")
    recommendations = synthesis.get('strategic_recommendations', [])
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            st.write(f"**{i}.** {rec}")
    else:
        st.write("No recommendations available")
    
    st.markdown("---")
    
    # Download options
    st.subheader("💾 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # JSON download
        json_data = json.dumps(result, indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name=f"{company_name}_research.json",
            mime="application/json"
        )
    
    with col2:
        # Text summary download
        text_summary = f"""
# Competitor Intelligence Report: {company_name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
{summary}

## Competitive Score: {score}/100
## Financial Health: {health_score}/100
## Product-Market Fit: {pmf}/100

## SWOT Analysis

### Strengths
{chr(10).join(f'- {s}' for s in strengths) if strengths else 'No data'}

### Weaknesses
{chr(10).join(f'- {w}' for w in weaknesses) if weaknesses else 'No data'}

### Opportunities
{chr(10).join(f'- {o}' for o in opps) if opps else 'No data'}

### Threats
{chr(10).join(f'- {t}' for t in threats) if threats else 'No data'}

## Strategic Recommendations
{chr(10).join(f'{i}. {r}' for i, r in enumerate(recommendations, 1)) if recommendations else 'No recommendations'}
"""
        st.download_button(
            label="📄 Download Report (TXT)",
            data=text_summary,
            file_name=f"{company_name}_report.txt",
            mime="text/plain"
        )


# Run app
if __name__ == "__main__":
    pass
