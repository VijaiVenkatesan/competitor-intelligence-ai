"""Prompt templates for different agents"""

RESEARCH_SYSTEM_PROMPT = """You are an expert market research analyst specializing in competitive intelligence.

Your responsibilities:
- Analyze companies, products, and market trends
- Extract key insights from raw data
- Identify competitive advantages and weaknesses
- Provide actionable strategic recommendations

Be thorough, accurate, and cite your sources when possible."""


WEB_RESEARCH_PROMPT = """Analyze the following company: {company_name}

Extract the following information:
1. Company Overview
   - Mission/Vision statement
   - Founded date
   - Headquarters location
   - Employee count (approximate)
   - Funding/Revenue (if publicly available)

2. Products/Services
   - Main offerings
   - Pricing (if available)
   - Target market/customers

3. Key Differentiators
   - Unique value propositions
   - Technology stack (if known)
   - Market positioning

4. Recent News/Updates
   - Product launches
   - Funding rounds
   - Strategic partnerships

Available data:
{scraped_content}

Return the information in structured JSON format."""


SOCIAL_MEDIA_ANALYSIS_PROMPT = """Analyze social media presence for: {company_name}

Based on the following data, provide insights on:

1. Overall Sentiment (positive/neutral/negative)
2. Key Themes in discussions
3. Customer Feedback highlights
4. Trending topics
5. Community engagement level

Data:
{social_data}

Return JSON with sentiment analysis and key insights."""


FINANCIAL_ANALYSIS_PROMPT = """Analyze financial health for: {company_name}

Based on available data:
{financial_data}

Provide:
1. Financial Status Summary
2. Growth Assessment
3. Funding History (if applicable)
4. Revenue estimates (if available)
5. Financial Health Score (0-100)
6. Key financial risks

Return as structured JSON."""


PRODUCT_ANALYSIS_PROMPT = """Analyze the product offering for: {company_name}

Data available:
{product_data}

Extract and analyze:
1. Core Value Proposition
2. Key Features (list top 5-10)
3. Pricing Strategy
4. Target User Persona
5. Competitive Advantages
6. Product Weaknesses
7. Product-Market Fit Score (0-100)

Return comprehensive JSON analysis."""


SYNTHESIS_PROMPT = """You are synthesizing competitive intelligence on: {company_name}

Input data from multiple research agents:
{agent_outputs}

Create a comprehensive strategic analysis with:

1. Executive Summary (3-4 sentences capturing the essence)

2. Company Overview
   - Background
   - Size and scale
   - Market position

3. SWOT Analysis
   - Strengths (3-5 points)
   - Weaknesses (3-5 points)
   - Opportunities (3-5 points)
   - Threats (3-5 points)

4. Product Analysis
   - Core offerings
   - Pricing strategy
   - Key differentiators

5. Market Position
   - Competitive landscape
   - Target customers
   - Market share (if known)

6. Financial Health
   - Funding status
   - Growth trajectory
   - Health assessment

7. Strategic Recommendations (5-7 actionable recommendations)

8. Competitive Score (0-100)

Be analytical, strategic, and provide actionable insights.
Return as structured JSON."""


# JSON Schemas

COMPANY_OVERVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "company_name": {"type": "string"},
        "tagline": {"type": "string"},
        "founded_year": {"type": ["integer", "null"]},
        "headquarters": {"type": "string"},
        "employee_count": {"type": "string"},
        "funding_total": {"type": "string"},
        "products": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"}
                }
            }
        },
        "key_differentiators": {"type": "array", "items": {"type": "string"}},
        "target_market": {"type": "string"}
    },
    "required": ["company_name"]
}

SOCIAL_SENTIMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "overall_sentiment": {"type": "string", "enum": ["positive", "neutral", "negative"]},
        "sentiment_score": {"type": "number", "minimum": 0, "maximum": 100},
        "key_themes": {"type": "array", "items": {"type": "string"}},
        "positive_feedback": {"type": "array", "items": {"type": "string"}},
        "negative_feedback": {"type": "array", "items": {"type": "string"}},
        "trending_topics": {"type": "array", "items": {"type": "string"}}
    }
}

SYNTHESIS_SCHEMA = {
    "type": "object",
    "properties": {
        "executive_summary": {"type": "string"},
        "company_overview": {
            "type": "object",
            "properties": {
                "background": {"type": "string"},
                "size_and_scale": {"type": "string"},
                "market_position": {"type": "string"}
            }
        },
        "swot_analysis": {
            "type": "object",
            "properties": {
                "strengths": {"type": "array", "items": {"type": "string"}},
                "weaknesses": {"type": "array", "items": {"type": "string"}},
                "opportunities": {"type": "array", "items": {"type": "string"}},
                "threats": {"type": "array", "items": {"type": "string"}}
            }
        },
        "product_analysis": {
            "type": "object",
            "properties": {
                "core_offerings": {"type": "string"},
                "pricing_strategy": {"type": "string"},
                "differentiators": {"type": "array", "items": {"type": "string"}},
                "product_market_fit_score": {"type": "integer", "minimum": 0, "maximum": 100}
            }
        },
        "financial_health": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "growth_trajectory": {"type": "string"},
                "health_score": {"type": "integer", "minimum": 0, "maximum": 100}
            }
        },
        "strategic_recommendations": {
            "type": "array",
            "items": {"type": "string"}
        },
        "competitive_score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
        }
    },
    "required": ["executive_summary", "swot_analysis", "strategic_recommendations", "competitive_score"]
}
