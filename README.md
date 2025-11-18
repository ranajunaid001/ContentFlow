# ContentFlow - Technical Documentation

## 🏗️ Architecture Overview

ContentFlow is a multi-agent system built with LangGraph that orchestrates three specialized AI agents to research topics, write articles, and generate email newsletters. The system uses a state-based workflow where each agent reads from and writes to a shared state.

### System Architecture
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│ Research Agent  │────▶│  Writer Agent   │────▶│Newsletter Agent │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                       │
         └───────────────┬───────────────────────────────┘
                         │
                    ┌────▼────┐
                    │ Shared  │
                    │  State  │
                    └─────────┘
```

## 📁 File Structure & Detailed Explanation

### 1. `state.py` - State Management
**Purpose**: Defines the shared state structure that flows between agents.
```python
class AgentState(TypedDict):
    # Input fields
    topic: str                    # User's requested topic
    recipient_email: str          # Email to send newsletter to
    
    # Research Agent outputs
    research_findings: List[str]  # Key findings from web search
    research_sources: List[str]   # URLs/sources used
    
    # Writer Agent outputs
    full_article: str            # Complete article text
    article_title: str           # Generated title
    
    # Newsletter Agent outputs
    newsletter_summary: str      # Email-ready summary
    email_subject: str          # Email subject line
    email_body: str             # HTML email content
    
    # Workflow control
    status: str                 # Current workflow status
    error: Optional[str]        # Error messages if any
    messages: List[str]         # Debug/status messages
```

**Key Concept**: State is immutable - each agent returns a new state with updates.

### 2. `config.py` - Configuration Management
**Purpose**: Centralized configuration for models, performance thresholds, and monitoring.
```python
AGENT_MODELS = {
    "research": {
        "model": "gpt-3.5-turbo",      # Cheaper for web search
        "temperature": 0.3,            # Low = more factual
        "max_tokens": 1000
    },
    "writer": {
        "model": "gpt-4-turbo-preview", # Better for creative writing
        "temperature": 0.7,            # Higher = more creative
        "max_tokens": 2000
    },
    "newsletter": {
        "model": "gpt-3.5-turbo",      # Summarization doesn't need GPT-4
        "temperature": 0.5,
        "max_tokens": 800
    }
}

PERFORMANCE_THRESHOLDS = {
    "research": {"max_duration_seconds": 30, "min_findings": 3},
    "writer": {"max_duration_seconds": 45, "min_word_count": 400},
    "newsletter": {"max_duration_seconds": 20, "min_word_count": 150}
}
```

### 3. `agents.py` - Agent Implementations
**Purpose**: Contains the three specialized agents with their logic.

#### Research Agent
```python
def research_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    1. Takes topic from state
    2. Uses DuckDuckGo search to find information
    3. Extracts 5-7 key findings using LLM
    4. Returns updated state with research
    """
```

#### Writer Agent
```python
def writer_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    1. Takes research findings from state
    2. Writes comprehensive article (500-700 words)
    3. Generates catchy title
    4. Returns updated state with article
    """
```

#### Newsletter Agent
```python
def newsletter_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    1. Takes full article from state
    2. Creates 150-200 word summary
    3. Formats as HTML email
    4. Returns updated state with email content
    """
```

**Key Features**:
- LangSmith tracing for each agent
- Performance tracking (duration, word count)
- Error handling
- Configurable models per agent

### 4. `graph.py` - Workflow Orchestration
**Purpose**: Defines the workflow graph and execution logic using LangGraph.
```python
def create_workflow():
    # Create directed graph
    workflow = StateGraph(AgentState)
    
    # Add agent nodes
    workflow.add_node("research", research_agent)
    workflow.add_node("writer", writer_agent)
    workflow.add_node("newsletter", newsletter_agent)
    
    # Define edges (flow)
    workflow.add_edge("research", "writer")
    workflow.add_edge("writer", "newsletter")
    workflow.add_edge("newsletter", END)
    
    # Set entry point
    workflow.set_entry_point("research")
    
    # Add memory for conversation continuity
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)
```

**Workflow Execution**:
1. Entry → Research Agent
2. Research Agent → Writer Agent
3. Writer Agent → Newsletter Agent
4. Newsletter Agent → END

### 5. `app.py` - FastAPI Server
**Purpose**: REST API server that exposes the workflow.

**Endpoints**:
- `GET /` - Root endpoint with API info
- `GET /health` - Health check
- `POST /generate-newsletter` - Main workflow endpoint
- `GET /workflow/{thread_id}` - Get workflow results
- `GET /workflow/visualize/graph` - Get Mermaid diagram

**Key Features**:
- CORS enabled for frontend access
- Background tasks for email sending
- Pydantic models for validation
- Error handling and logging
- Thread-based workflow tracking

### 6. `requirements.txt` - Dependencies
**Core Dependencies**:
- `fastapi` & `uvicorn` - Web server
- `langchain` ecosystem - Agent framework
- `langgraph` - Workflow orchestration
- `langsmith` - Monitoring/tracing
- `duckduckgo-search` - Web search
- `openai` - LLM provider

### 7. `Dockerfile` - Container Configuration
**Multi-stage build**:
1. **Builder stage**: Installs dependencies
2. **Runtime stage**: Copies dependencies and code

**Key optimization**: Dependencies cached separately from code

### 8. `railway.json` - Deployment Configuration
```json
{
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## 🔄 Complete Request Flow

1. **User Request**:
```
   POST /generate-newsletter
   {
     "topic": "AI developments",
     "recipient_email": "user@example.com"
   }
```

2. **API Layer** (`app.py`):
   - Validates request
   - Creates initial state
   - Invokes workflow

3. **Workflow Execution** (`graph.py`):
   - Loads workflow graph
   - Executes agents in sequence
   - Maintains state between agents

4. **Agent Execution**:
   - **Research**: Searches web → extracts findings
   - **Writer**: Uses findings → writes article
   - **Newsletter**: Summarizes article → creates email

5. **Response**:
```json
   {
     "success": true,
     "article_title": "Breaking: AI Advances...",
     "thread_id": "newsletter_ai_developments_user@example.com",
     "performance_metrics": {...}
   }
```

## 🔧 Environment Variables
```bash
# OpenAI API access
OPENAI_API_KEY=sk-...

# LangSmith monitoring
LANGSMITH_API_KEY=ls-...
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=contentflow-production
LANGSMITH_ENDPOINT=https://api.smith.langchain.com

# Railway provides
PORT=<auto-set>
```

## 📊 State Flow Example
```python
# Initial State
{
    "topic": "quantum computing",
    "recipient_email": "user@example.com",
    "research_findings": [],
    "status": "starting"
}
↓
# After Research Agent
{
    ...previous,
    "research_findings": ["IBM announced...", "Google achieved..."],
    "research_sources": ["https://..."],
    "status": "research_complete"
}
↓
# After Writer Agent
{
    ...previous,
    "full_article": "Quantum Computing Breakthrough...",
    "article_title": "The Quantum Leap",
    "status": "writing_complete"
}
↓
# After Newsletter Agent
{
    ...previous,
    "newsletter_summary": "This week in quantum...",
    "email_subject": "Newsletter: The Quantum Leap",
    "email_body": "<html>...",
    "status": "newsletter_complete"
}
```

## 🚀 Deployment Architecture
```
Railway Platform
    │
    ├── Docker Container
    │   ├── Python 3.11
    │   ├── FastAPI Server (port $PORT)
    │   └── All Dependencies
    │
    ├── Environment Variables
    │   ├── OPENAI_API_KEY
    │   └── LANGSMITH_*
    │
    └── Public URL
        └── contentflow-production-a81e.up.railway.app
```

## 📈 Monitoring & Debugging

### LangSmith Integration
- Every agent execution is traced
- View in dashboard: https://smith.langchain.com
- Tracks: latency, token usage, errors

### Performance Metrics
Each agent tracks:
- Execution duration
- Output quality (word count, findings count)
- Pass/fail against thresholds

### Error Handling
- Agent-level try/catch
- Workflow-level error state
- API-level error responses

## 🔮 Future Enhancements

1. **Email Integration**: Add SendGrid/AWS SES
2. **Persistent Storage**: Add database for results
3. **Advanced Routing**: Conditional agent selection
4. **More Agents**: Fact-checker, Image finder
5. **UI Dashboard**: React frontend for configuration
