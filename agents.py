from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from datetime import datetime

# Initialize tools
llm = ChatOpenAI(temperature=0.7, model="gpt-4-turbo-preview")
search = DuckDuckGoSearchRun()

def research_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Research agent that gathers information on the topic"""
    topic = state["topic"]
    
    # Search for information
    search_results = search.run(f"{topic} latest news 2024")
    
    # Generate research findings
    research_prompt = f"""
    Based on these search results about {topic}:
    {search_results}
    
    Extract 5-7 key findings or important points.
    Format as a list of clear, concise statements.
    """
    
    findings = llm.invoke(research_prompt).content
    
    return {
        **state,
        "research_findings": findings.split("\n"),
        "research_sources": [search_results[:200]],
        "status": "research_complete",
        "messages": state.get("messages", []) + ["Research completed"]
    }

def writer_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Writer agent that creates full article"""
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
    
    article = llm.invoke(writer_prompt).content
    
    # Generate title
    title_prompt = f"Create a catchy title for this article about {topic}"
    title = llm.invoke(title_prompt).content
    
    return {
        **state,
        "full_article": article,
        "article_title": title,
        "status": "writing_complete",
        "messages": state.get("messages", []) + ["Article written"]
    }

def newsletter_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Newsletter agent that creates email summary"""
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
    
    summary = llm.invoke(summary_prompt).content
    
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
    
    return {
        **state,
        "newsletter_summary": summary,
        "email_subject": subject,
        "email_body": email_body,
        "status": "newsletter_complete",
        "messages": state.get("messages", []) + ["Newsletter created"]
    }
