import os

# Model Configuration
AGENT_MODELS = {
    "research": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.3,
        "max_tokens": 1000
    },
    "writer": {
        "model": "gpt-4-turbo-preview", 
        "temperature": 0.7,
        "max_tokens": 2000
    },
    "newsletter": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.5,
        "max_tokens": 800
    }
}

# LangSmith Configuration
LANGSMITH_CONFIG = {
    "project_name": "contentflow-agents",
    "tags": ["production", "newsletter"],
}

# Agent-specific LangSmith tags
AGENT_TAGS = {
    "research": ["research", "web-search"],
    "writer": ["content-generation", "article"],
    "newsletter": ["summarization", "email"]
}

# Performance thresholds (for monitoring)
PERFORMANCE_THRESHOLDS = {
    "research": {
        "max_duration_seconds": 30,
        "min_findings": 3
    },
    "writer": {
        "max_duration_seconds": 45,
        "min_word_count": 400
    },
    "newsletter": {
        "max_duration_seconds": 20,
        "min_word_count": 150
    }
}
