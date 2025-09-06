"""HTTP server for the security agent."""

import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .agent import SecurityAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Security Agent", description="AI-powered security analysis and compliance monitoring")

# Initialize agent
security_agent = SecurityAgent()


class SecurityRequest(BaseModel):
    """Request model for security operations."""
    target: str
    scan_type: str = "comprehensive"


class SecurityResponse(BaseModel):
    """Response model for security operations."""
    success: bool
    target: str = ""
    vulnerabilities_found: int = 0
    risk_score: float = 0.0
    compliance_score: float = 0.0
    security_report: str = ""
    recommendations: list = []
    detailed_findings: list = []
    error: str = ""


@app.post("/analyze", response_model=SecurityResponse)
async def analyze_security(request: SecurityRequest):
    """Perform security analysis on target system."""
    try:
        logger.info(f"Processing security analysis for: {request.target}")
        
        result = await security_agent.process(
            target=request.target,
            scan_type=request.scan_type
        )
        
        return SecurityResponse(**result)
        
    except Exception as e:
        logger.error(f"Security analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "security-agent"}


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "security-agent",
        "version": "1.0.0",
        "description": "AI-powered security analysis and compliance monitoring"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8083)