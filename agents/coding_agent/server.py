"""HTTP server for the coding agent."""

import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .agent import CodingAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Coding Agent", description="AI-powered code generation agent")

# Initialize agent
coding_agent = CodingAgent()


class CodingRequest(BaseModel):
    """Request model for coding operations."""
    repo: str
    branch: str
    requirements: str


class CodingResponse(BaseModel):
    """Response model for coding operations."""
    success: bool
    merge_request_url: str = ""
    files_created: int = 0
    analysis: dict = {}
    error: str = ""


@app.post("/generate", response_model=CodingResponse)
async def generate_code(request: CodingRequest):
    """Generate code based on requirements."""
    try:
        logger.info(f"Processing coding request for repo: {request.repo}")
        
        result = await coding_agent.process(
            repo=request.repo,
            branch=request.branch,
            requirements=request.requirements
        )
        
        return CodingResponse(**result)
        
    except Exception as e:
        logger.error(f"Coding request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "coding-agent"}


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "coding-agent",
        "version": "1.0.0",
        "description": "AI-powered code generation and repository management"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)