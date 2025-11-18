from typing import Dict, Any
from langchain_openai import ChatOpenAI
from tavily import TavilyClient
from datetime import datetime
import time
import os
from config import AGENT_MODELS, LANGSMITH_CONFIG, AGENT_TAGS, PERFORMANCE_THRESHOLDS

# Initialize tools
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Initialize models with config
models = {
    agent: ChatOpenAI(
        model=config["model"],
        temperature=config["temperature"],
        max_tokens=config.get("max_tokens", 1000)
    )
    for agent, config in AGENT_MODELS.items()
}

def research_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Research agent that gathers information on the topic"""
    start_time = time.time()
    
    topic = state["topic"]
    
    # Search using Tavily
    try:
        search_response = tavily.search(f"{topic} latest news 2024", max_results=5)
        search_results = "\n".join([f"- {r['content']}" for r in search_response['results']])
        sources = [r['url'] for r in search_response['results']][:3]  # Top 3 sources
    except Exception as e:
        # Fallback if search fails
        search_results = f"Search unavailable. Using general knowledge about {topic}."
        sources = ["General knowledge"]
    
    # Generate research findings
    research_prompt = f"""
    Based on these search results about {topic}:
    {search_results}
    
    Extract 5-7 key findings or important points.
    Format as a list of clear, concise statements.
    """
    
    findings = models["research"].invoke(research_prompt).content
    
    # Performance tracking
    duration = time.time() - start_time
    findings_list = [f.strip() for f in findings.split("\n") if f.strip()]
    
    performance_data = {
        "duration": duration,
        "findings_count": len(findings_list),
        "passed_thresholds": {
            "time": duration <= PERFORMANCE_THRESHOLDS["research"]["max_duration_seconds"],
            "findings": len(findings_list) >= PERFORMANCE_THRESHOLDS["research"]["min_findings"]
        }
    }
    
    return {
        **state,
        "research_findings": findings_list,
        "research_sources": sources,
        "status": "research_complete",
        "messages": state.get("messages", []) + [f"Research completed in {duration:.2f}s"],
        "performance_metrics": {
            **state.get("performance_metrics", {}),
            "research": performance_data
        }
    }

def writer_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Writer agent that creates full article"""
    start_time = time.time()
    
    topic = state["topic"]
    research = "\n".join(state["research_findings"])
    
    writer_prompt = f"""
    Write a comprehensive article about {topic}.
    
    Use these research findings:
    {research}
    
    Structure:
    1. Engaging introduction
    2. Main body with 3-4 sections
    3. Conclusion
    
    Make it informative and engaging. About 500-700 words.
    """
    
    article = models["writer"].invoke(writer_prompt).content
    
    # Generate title
    title_prompt = f"Create a catchy title for this article about {topic}"
    title = models["writer"].invoke(title_prompt).content
    
    # Performance tracking
    duration = time.time() - start_time
    word_count = len(article.split())
    
    performance_data = {
        "duration": duration,
        "word_count": word_count,
        "passed_thresholds": {
            "time": duration <= PERFORMANCE_THRESHOLDS["writer"]["max_duration_seconds"],
            "word_count": word_count >= PERFORMANCE_THRESHOLDS["writer"]["min_word_count"]
        }
    }
    
    return {
        **state,
        "full_article": article,
        "article_title": title,
        "status": "writing_complete",
        "messages": state.get("messages", []) + [f"Article written in {duration:.2f}s ({word_count} words)"],
        "performance_metrics": {
            **state.get("performance_metrics", {}),
            "writer": performance_data
        }
    }

def newsletter_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Newsletter agent that creates email summary"""
    start_time = time.time()
    
    article = state["full_article"]
    title = state["article_title"]
    
    summary_prompt = f"""
    Create a newsletter summary of this article:
    
    Title: {title}
    Article: {article}
    
    Make it:
    1. 150-200 words
    2. Highlight key points
    3. Include a call-to-action
    4. Email-friendly formatting
    """
    
    summary = models["newsletter"].invoke(summary_prompt).content
    
    # Create email subject
    subject = f"Newsletter: {title}"
    
    # Create email body
    email_body = f"""
    <h2>{title}</h2>
    
    {summary}
    
    <p><a href="#">Read Full Article</a></p>
    
    <hr>
    <p>Generated on {datetime.now().strftime('%B %d, %Y')}</p>
    """
    
    # Performance tracking
    duration = time.time() - start_time
    summary_word_count = len(summary.split())
    
    performance_data = {
        "duration": duration,
        "word_count": summary_word_count,
        "passed_thresholds": {
            "time": duration <= PERFORMANCE_THRESHOLDS["newsletter"]["max_duration_seconds"],
            "word_count": summary_word_count >= PERFORMANCE_THRESHOLDS["newsletter"]["min_word_count"]
        }
    }
    
    return {
        **state,
        "newsletter_summary": summary,
        "email_subject": subject,
        "email_body": email_body,
        "status": "newsletter_complete",
        "messages": state.get("messages", []) + [f"Newsletter created in {duration:.2f}s"],
        "performance_metrics": {
            **state.get("performance_metrics", {}),
            "newsletter": performance_data
        }
    }
