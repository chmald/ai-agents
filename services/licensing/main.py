"""Licensing service main application."""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Licensing Service",
    description="Usage tracking and billing for AI agents",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Mock database - in production use PostgreSQL
TENANTS_DB = {}
USAGE_DB = {}
LICENSES_DB = {}


# Request/Response Models
class TenantUsage(BaseModel):
    tenant_id: str
    agent_type: str
    requests_count: int = 1
    tokens_used: int = 0
    timestamp: str = datetime.now().isoformat()


class UsageResponse(BaseModel):
    success: bool
    tenant_id: str = ""
    current_usage: Dict[str, int] = {}
    limits: Dict[str, int] = {}
    overage: bool = False
    error: str = ""


class LicenseInfo(BaseModel):
    tenant_id: str
    plan: str
    limits: Dict[str, int]
    expires_at: str
    active: bool = True


async def verify_service_token(token: str = Depends(security)):
    """Verify service-to-service token."""
    # Mock verification - in production use proper service authentication
    if not token or token.credentials != "licensing-service-token":
        raise HTTPException(status_code=401, detail="Invalid service token")
    return True


@app.post("/api/usage/record", response_model=UsageResponse)
async def record_usage(usage: TenantUsage, authenticated: bool = Depends(verify_service_token)):
    """Record agent usage for a tenant."""
    try:
        tenant_id = usage.tenant_id
        agent_type = usage.agent_type
        
        # Initialize tenant usage if not exists
        if tenant_id not in USAGE_DB:
            USAGE_DB[tenant_id] = {
                "coding": {"requests": 0, "tokens": 0},
                "marketing": {"requests": 0, "tokens": 0},
                "security": {"requests": 0, "tokens": 0},
                "bizdev": {"requests": 0, "tokens": 0}
            }
        
        # Record usage
        USAGE_DB[tenant_id][agent_type]["requests"] += usage.requests_count
        USAGE_DB[tenant_id][agent_type]["tokens"] += usage.tokens_used
        
        # Get tenant license info
        license_info = LICENSES_DB.get(tenant_id, {
            "plan": "basic",
            "limits": {"requests": 100, "tokens": 10000},
            "expires_at": (datetime.now() + timedelta(days=30)).isoformat(),
            "active": True
        })
        
        # Calculate current usage
        current_usage = {
            "total_requests": sum(data["requests"] for data in USAGE_DB[tenant_id].values()),
            "total_tokens": sum(data["tokens"] for data in USAGE_DB[tenant_id].values())
        }
        
        # Check for overages
        limits = license_info["limits"]
        overage = (
            current_usage["total_requests"] > limits["requests"] or
            current_usage["total_tokens"] > limits["tokens"]
        )
        
        logger.info(f"Usage recorded for tenant {tenant_id}: {usage.requests_count} requests, {usage.tokens_used} tokens")
        
        return UsageResponse(
            success=True,
            tenant_id=tenant_id,
            current_usage=current_usage,
            limits=limits,
            overage=overage
        )
        
    except Exception as e:
        logger.error(f"Failed to record usage: {e}")
        return UsageResponse(
            success=False,
            error=str(e)
        )


@app.get("/api/usage/{tenant_id}")
async def get_usage(tenant_id: str, authenticated: bool = Depends(verify_service_token)):
    """Get current usage for a tenant."""
    try:
        if tenant_id not in USAGE_DB:
            return {"tenant_id": tenant_id, "usage": {}, "total_requests": 0, "total_tokens": 0}
        
        usage_data = USAGE_DB[tenant_id]
        total_requests = sum(data["requests"] for data in usage_data.values())
        total_tokens = sum(data["tokens"] for data in usage_data.values())
        
        return {
            "tenant_id": tenant_id,
            "usage": usage_data,
            "total_requests": total_requests,
            "total_tokens": total_tokens
        }
        
    except Exception as e:
        logger.error(f"Failed to get usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/licenses")
async def create_license(license_info: LicenseInfo, authenticated: bool = Depends(verify_service_token)):
    """Create or update a license for a tenant."""
    try:
        tenant_id = license_info.tenant_id
        
        # Define plan limits
        plan_limits = {
            "basic": {"requests": 100, "tokens": 10000},
            "pro": {"requests": 1000, "tokens": 100000},
            "enterprise": {"requests": 10000, "tokens": 1000000}
        }
        
        # Set limits based on plan
        limits = plan_limits.get(license_info.plan, plan_limits["basic"])
        
        LICENSES_DB[tenant_id] = {
            "plan": license_info.plan,
            "limits": limits,
            "expires_at": license_info.expires_at,
            "active": license_info.active,
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"License created for tenant {tenant_id}: {license_info.plan} plan")
        
        return {
            "success": True,
            "tenant_id": tenant_id,
            "license": LICENSES_DB[tenant_id]
        }
        
    except Exception as e:
        logger.error(f"Failed to create license: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/licenses/{tenant_id}")
async def get_license(tenant_id: str, authenticated: bool = Depends(verify_service_token)):
    """Get license information for a tenant."""
    try:
        license_info = LICENSES_DB.get(tenant_id)
        
        if not license_info:
            raise HTTPException(status_code=404, detail="License not found")
        
        return {
            "tenant_id": tenant_id,
            "license": license_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get license: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/billing/{tenant_id}")
async def get_billing_info(tenant_id: str, authenticated: bool = Depends(verify_service_token)):
    """Get billing information for a tenant."""
    try:
        usage_data = USAGE_DB.get(tenant_id, {})
        license_info = LICENSES_DB.get(tenant_id, {})
        
        total_requests = sum(data["requests"] for data in usage_data.values()) if usage_data else 0
        total_tokens = sum(data["tokens"] for data in usage_data.values()) if usage_data else 0
        
        # Calculate billing based on usage and overages
        plan = license_info.get("plan", "basic")
        limits = license_info.get("limits", {"requests": 100, "tokens": 10000})
        
        # Basic pricing model
        base_prices = {"basic": 29, "pro": 99, "enterprise": 299}
        overage_rates = {"requests": 0.01, "tokens": 0.001}  # Per unit overage
        
        base_cost = base_prices.get(plan, 29)
        
        # Calculate overages
        request_overage = max(0, total_requests - limits["requests"])
        token_overage = max(0, total_tokens - limits["tokens"])
        
        overage_cost = (
            request_overage * overage_rates["requests"] +
            token_overage * overage_rates["tokens"]
        )
        
        total_cost = base_cost + overage_cost
        
        return {
            "tenant_id": tenant_id,
            "billing_period": datetime.now().strftime("%Y-%m"),
            "plan": plan,
            "base_cost": base_cost,
            "usage": {
                "requests": total_requests,
                "tokens": total_tokens
            },
            "limits": limits,
            "overages": {
                "requests": request_overage,
                "tokens": token_overage,
                "cost": round(overage_cost, 2)
            },
            "total_cost": round(total_cost, 2)
        }
        
    except Exception as e:
        logger.error(f"Failed to get billing info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "licensing"}


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "licensing",
        "version": "1.0.0",
        "description": "Usage tracking and billing for AI agents"
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8085))
    uvicorn.run(app, host="0.0.0.0", port=port)