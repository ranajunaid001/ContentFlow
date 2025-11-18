from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    # Input
    topic: str
    recipient_email: str
    
    # Research Agent Output
    research_findings: List[str]
    research_sources: List[str]
    
    # Writer Agent Output
    full_article: str
    article_title: str
    
    # Newsletter Agent Output
    newsletter_summary: str
    email_subject: str
    email_body: str
    
    # Workflow Control
    status: str
    error: Optional[str]
    messages: List[str]
