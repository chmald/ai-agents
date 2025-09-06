"""HTTP server for the business development agent."""

import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .agent import BizDevAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Business Development Agent", description="AI-powered lead management and CRM automation")

# Initialize agent
bizdev_agent = BizDevAgent()


class LeadRequest(BaseModel):
    """Request model for lead processing."""
    lead_name: str
    lead_email: str
    lead_company: str
    context: str = ""


class LeadResponse(BaseModel):
    """Response model for lead processing."""
    success: bool
    lead_id: str = ""
    qualification_score: float = 0.0
    existing_contact: bool = False
    followup_scheduled: bool = False
    welcome_sent: bool = False
    recommendations: list = []
    error: str = ""


@app.post("/process_lead", response_model=LeadResponse)
async def process_lead(request: LeadRequest):
    """Process a new lead through the business development workflow."""
    try:
        logger.info(f"Processing lead: {request.lead_name} from {request.lead_company}")
        
        result = await bizdev_agent.process(
            lead_name=request.lead_name,
            lead_email=request.lead_email,
            lead_company=request.lead_company,
            context=request.context
        )
        
        return LeadResponse(**result)
        
    except Exception as e:
        logger.error(f"Lead processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "bizdev-agent"}


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "bizdev-agent",
        "version": "1.0.0",
        "description": "AI-powered business development and lead management"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8084)