"""FastAPI gateway for the AI-Powered Business Ecosystem."""

import logging
import os
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import httpx
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Business Ecosystem",
    description="Multi-tenant, agent-based platform for automation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Agent service URLs
AGENT_SERVICES = {
    "coding": os.getenv("CODING_AGENT_URL", "http://localhost:8081"),
    "marketing": os.getenv("MARKETING_AGENT_URL", "http://localhost:8082"),
    "security": os.getenv("SECURITY_AGENT_URL", "http://localhost:8083"),
    "bizdev": os.getenv("BIZDEV_AGENT_URL", "http://localhost:8084")
}


# Request/Response Models
class CodingRequest(BaseModel):
    repo: str
    branch: str
    requirements: str


class MarketingRequest(BaseModel):
    title: str
    body: str


class SecurityRequest(BaseModel):
    target: str
    scan_type: str = "comprehensive"


class BizDevRequest(BaseModel):
    lead_name: str
    lead_email: str
    lead_company: str
    context: str = ""


class TenantRequest(BaseModel):
    name: str
    email: str = ""
    plan: str = "basic"


# Mock authentication - replace with Keycloak integration
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token."""
    token = credentials.credentials
    
    # Mock verification - in production, validate with Keycloak
    if not token or token == "invalid":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Return mock user info
    return {
        "user_id": "demo_user",
        "tenant_id": "demo_tenant",
        "permissions": ["read", "write", "admin"]
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    agent_status = {}
    
    # Check agent service health
    async with httpx.AsyncClient() as client:
        for agent_name, url in AGENT_SERVICES.items():
            try:
                response = await client.get(f"{url}/health", timeout=5.0)
                agent_status[agent_name] = "healthy" if response.status_code == 200 else "unhealthy"
            except Exception:
                agent_status[agent_name] = "unreachable"
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "agents": agent_status
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AI-Powered Business Ecosystem",
        "version": "1.0.0",
        "description": "Multi-tenant, agent-based platform for automation",
        "agents": list(AGENT_SERVICES.keys()),
        "docs_url": "/docs"
    }


# Tenant management
@app.post("/api/tenants")
async def create_tenant(request: TenantRequest, user_info = Depends(verify_token)):
    """Create a new tenant."""
    try:
        # Mock tenant creation - integrate with database in production
        tenant_id = f"tenant_{hash(request.name) % 100000}"
        
        logger.info(f"Created tenant: {tenant_id} for {request.name}")
        
        return {
            "success": True,
            "tenant_id": tenant_id,
            "name": request.name,
            "plan": request.plan,
            "status": "active"
        }
        
    except Exception as e:
        logger.error(f"Failed to create tenant: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Coding Agent endpoints
@app.post("/api/coding_agent/consume")
async def trigger_coding_agent(request: CodingRequest, user_info = Depends(verify_token)):
    """Trigger the coding agent to process requirements."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AGENT_SERVICES['coding']}/generate",
                json=request.dict(),
                timeout=120.0
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.RequestError as e:
        logger.error(f"Coding agent request failed: {e}")
        raise HTTPException(status_code=503, detail="Coding agent service unavailable")
    except Exception as e:
        logger.error(f"Coding agent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Marketing Agent endpoints
@app.post("/api/marketing_agent/draft")
async def trigger_marketing_agent(request: MarketingRequest, user_info = Depends(verify_token)):
    """Trigger the marketing agent to create and publish content."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AGENT_SERVICES['marketing']}/generate",
                json=request.dict(),
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.RequestError as e:
        logger.error(f"Marketing agent request failed: {e}")
        raise HTTPException(status_code=503, detail="Marketing agent service unavailable")
    except Exception as e:
        logger.error(f"Marketing agent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Security Agent endpoints
@app.post("/api/security_agent/scan")
async def trigger_security_agent(request: SecurityRequest, user_info = Depends(verify_token)):
    """Trigger the security agent to perform security analysis."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AGENT_SERVICES['security']}/analyze",
                json=request.dict(),
                timeout=180.0
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.RequestError as e:
        logger.error(f"Security agent request failed: {e}")
        raise HTTPException(status_code=503, detail="Security agent service unavailable")
    except Exception as e:
        logger.error(f"Security agent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Business Development Agent endpoints
@app.post("/api/bizdev_agent/process_lead")
async def trigger_bizdev_agent(request: BizDevRequest, user_info = Depends(verify_token)):
    """Trigger the business development agent to process a lead."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AGENT_SERVICES['bizdev']}/process_lead",
                json=request.dict(),
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.RequestError as e:
        logger.error(f"BizDev agent request failed: {e}")
        raise HTTPException(status_code=503, detail="BizDev agent service unavailable")
    except Exception as e:
        logger.error(f"BizDev agent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Analytics and monitoring endpoints
@app.get("/api/analytics/usage")
async def get_usage_analytics(user_info = Depends(verify_token)):
    """Get usage analytics for the tenant."""
    # Mock analytics data
    return {
        "tenant_id": user_info["tenant_id"],
        "period": "last_30_days",
        "agent_usage": {
            "coding": {"requests": 45, "success_rate": 0.91},
            "marketing": {"requests": 23, "success_rate": 0.96},
            "security": {"requests": 12, "success_rate": 0.83},
            "bizdev": {"requests": 18, "success_rate": 0.94}
        },
        "total_requests": 98,
        "avg_response_time": 2.3
    }


@app.get("/api/system/status")
async def get_system_status():
    """Get system status and metrics."""
    return {
        "uptime": "72h 15m",
        "total_agents": len(AGENT_SERVICES),
        "active_tenants": 42,
        "requests_today": 234,
        "avg_response_time": 2.1,
        "error_rate": 0.02
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)