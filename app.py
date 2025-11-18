from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import os
from datetime import datetime
import uvicorn

from graph import run_newsletter_workflow, visualize_workflow

# Initialize FastAPI app
app = FastAPI(
    title="ContentFlow API",
    description="AI-powered newsletter generation system",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class NewsletterRequest(BaseModel):
    topic: str
    recipient_email: EmailStr
    
class NewsletterResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[Any, Any]] = None
    thread_id: Optional[str] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

# Store workflow results (in production, use Redis/Database)
workflow_results = {}

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Main newsletter generation endpoint
@app.post("/generate-newsletter", response_model=NewsletterResponse)
async def generate_newsletter(
    request: NewsletterRequest,
    background_tasks: BackgroundTasks
):
    """Generate a newsletter from a topic"""
    try:
        # Validate inputs
        if not request.topic.strip():
            raise HTTPException(status_code=400, detail="Topic cannot be empty")
        
        # Run the workflow
        result = run_newsletter_workflow(
            topic=request.topic,
            email=request.recipient_email
        )
        
        if result["success"]:
            # Store result
            thread_id = result["thread_id"]
            workflow_results[thread_id] = result["data"]
            
            # Add email sending to background tasks
            background_tasks.add_task(
                send_newsletter_email,
                email=request.recipient_email,
                subject=result["data"]["email_subject"],
                body=result["data"]["email_body"]
            )
            
            return NewsletterResponse(
                success=True,
                message="Newsletter generated successfully",
                data={
                    "article_title": result["data"]["article_title"],
                    "article_preview": result["data"]["full_article"][:200] + "...",
                    "email_subject": result["data"]["email_subject"],
                    "performance_metrics": result["data"].get("performance_metrics", {})
                },
                thread_id=thread_id
            )
        else:
            return NewsletterResponse(
                success=False,
                message="Failed to generate newsletter",
                error=result["error"]
            )
            
    except Exception as e:
        return NewsletterResponse(
            success=False,
            message="An error occurred",
            error=str(e)
        )

# Get workflow result endpoint
@app.get("/workflow/{thread_id}")
async def get_workflow_result(thread_id: str):
    """Get the full result of a workflow run"""
    if thread_id not in workflow_results:
        raise HTTPException(status_code=404, detail="Workflow result not found")
    
    return {
        "thread_id": thread_id,
        "data": workflow_results[thread_id]
    }

# Visualize workflow endpoint
@app.get("/workflow/visualize/graph")
async def get_workflow_visualization():
    """Get a visual representation of the workflow"""
    try:
        diagram = visualize_workflow()
        return {
            "diagram": diagram,
            "format": "mermaid"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Email sending function (implement with actual email service)
async def send_newsletter_email(email: str, subject: str, body: str):
    """Send newsletter email (placeholder - implement with SendGrid/SES/etc)"""
    # TODO: Implement actual email sending
    # For now, just log
    print(f"Would send email to {email}")
    print(f"Subject: {subject}")
    print(f"Body preview: {body[:100]}...")
    
    # In production, use:
    # - SendGrid
    # - AWS SES
    # - Mailgun
    # - SMTP

# Serve the UI
@app.get("/ui", response_class=HTMLResponse)
async def serve_ui():
    with open("index.html", "r") as f:
        return f.read()
        
# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "ContentFlow API",
        "docs": "/docs",
        "health": "/health"
    }

# Run the server (for local development)
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
