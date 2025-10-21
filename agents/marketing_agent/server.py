"""HTTP server for the marketing agent."""

import logging
import sys
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from agents.marketing_agent.agent import MarketingAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Marketing Agent", description="AI-powered social media and marketing automation")

# Initialize agent
marketing_agent = MarketingAgent()


class MarketingRequest(BaseModel):
    """Request model for marketing operations."""
    title: str
    body: str


class MarketingResponse(BaseModel):
    """Response model for marketing operations."""
    success: bool
    tweet: str = ""
    tweet_id: str = ""
    sentiment_analysis: dict = {}
    engagement_score: float = 0.0
    error: str = ""


@app.post("/generate", response_model=MarketingResponse)
async def generate_content(request: MarketingRequest):
    """Generate and publish marketing content."""
    try:
        logger.info(f"Processing marketing request: {request.title}")
        
        result = await marketing_agent.process(
            title=request.title,
            body=request.body
        )
        
        return MarketingResponse(**result)
        
    except Exception as e:
        logger.error(f"Marketing request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "marketing-agent"}


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "marketing-agent",
        "version": "1.0.0",
        "description": "AI-powered social media and marketing automation"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8082)