from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from state import AgentState
from agents import research_agent, writer_agent, newsletter_agent
import os

# Create the workflow graph
def create_workflow():
    # Initialize the graph with state
    workflow = StateGraph(AgentState)
    
    # Add nodes (agents)
    workflow.add_node("research", research_agent)
    workflow.add_node("writer", writer_agent)
    workflow.add_node("newsletter", newsletter_agent)
    
    # Define the edges (flow)
    workflow.add_edge("research", "writer")
    workflow.add_edge("writer", "newsletter")
    workflow.add_edge("newsletter", END)
    
    # Set entry point
    workflow.set_entry_point("research")
    
    # Initialize memory (for conversation continuity)
    memory = MemorySaver()
    
    # Compile the graph
    app = workflow.compile(checkpointer=memory)
    
    return app

# Create a function to run the workflow
def run_newsletter_workflow(topic: str, email: str):
    """Run the complete newsletter generation workflow"""
    
    # Initialize the workflow
    app = create_workflow()
    
    # Initial state
    initial_state = {
        "topic": topic,
        "recipient_email": email,
        "research_findings": [],
        "research_sources": [],
        "full_article": "",
        "article_title": "",
        "newsletter_summary": "",
        "email_subject": "",
        "email_body": "",
        "status": "starting",
        "error": None,
        "messages": ["Workflow started"],
        "performance_metrics": {}
    }
    
    # Configuration for the run
    config = {
        "configurable": {
            "thread_id": f"newsletter_{topic.replace(' ', '_')}_{email}"
        }
    }
    
    try:
        # Run the workflow
        final_state = app.invoke(initial_state, config)
        return {
            "success": True,
            "data": final_state,
            "thread_id": config["configurable"]["thread_id"]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None
        }

# Function to visualize the graph (optional)
def visualize_workflow():
    """Generate a visual representation of the workflow"""
    app = create_workflow()
    try:
        # This will return a mermaid diagram
        return app.get_graph().draw_mermaid()
    except Exception as e:
        return f"Could not generate visualization: {str(e)}"
