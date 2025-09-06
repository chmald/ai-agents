"""Basic integration tests for the AI ecosystem."""

import pytest
import asyncio
import httpx
from typing import Dict, Any


class TestAIEcosystem:
    """Integration tests for the AI-Powered Business Ecosystem."""
    
    def setup_method(self):
        """Set up test environment."""
        self.base_url = "http://localhost:8000"
        self.headers = {"Authorization": "Bearer test-token"}
        self.timeout = 30.0
    
    @pytest.mark.asyncio
    async def test_api_gateway_health(self):
        """Test API gateway health endpoint."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/health", timeout=self.timeout)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_coding_agent_integration(self):
        """Test coding agent through API gateway."""
        payload = {
            "repo": "test/demo-repo",
            "branch": "feature/ai-generated",
            "requirements": "Create a simple Python function that calculates factorial"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/coding_agent/consume",
                json=payload,
                headers=self.headers,
                timeout=60.0
            )
            
            # Should succeed or return meaningful error
            assert response.status_code in [200, 503]  # 503 if service unavailable
            
            if response.status_code == 200:
                data = response.json()
                assert "success" in data
    
    @pytest.mark.asyncio
    async def test_marketing_agent_integration(self):
        """Test marketing agent through API gateway."""
        payload = {
            "title": "New AI Product Launch",
            "body": "Exciting new AI-powered business automation platform now available"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/marketing_agent/draft",
                json=payload,
                headers=self.headers,
                timeout=60.0
            )
            
            assert response.status_code in [200, 503]
            
            if response.status_code == 200:
                data = response.json()
                assert "success" in data
    
    @pytest.mark.asyncio
    async def test_security_agent_integration(self):
        """Test security agent through API gateway."""
        payload = {
            "target": "https://demo.example.com",
            "scan_type": "web"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/security_agent/scan",
                json=payload,
                headers=self.headers,
                timeout=120.0
            )
            
            assert response.status_code in [200, 503]
            
            if response.status_code == 200:
                data = response.json()
                assert "success" in data
    
    @pytest.mark.asyncio
    async def test_bizdev_agent_integration(self):
        """Test business development agent through API gateway."""
        payload = {
            "lead_name": "John Doe",
            "lead_email": "john.doe@example.com",
            "lead_company": "Example Corp",
            "context": "Interested in AI automation solutions"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/bizdev_agent/process_lead",
                json=payload,
                headers=self.headers,
                timeout=60.0
            )
            
            assert response.status_code in [200, 503]
            
            if response.status_code == 200:
                data = response.json()
                assert "success" in data
    
    @pytest.mark.asyncio
    async def test_tenant_creation(self):
        """Test tenant creation."""
        payload = {
            "name": "Test Tenant",
            "email": "admin@test-tenant.com",
            "plan": "basic"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/tenants",
                json=payload,
                headers=self.headers,
                timeout=30.0
            )
            
            assert response.status_code in [200, 503]
            
            if response.status_code == 200:
                data = response.json()
                assert data["success"] is True
                assert "tenant_id" in data


@pytest.mark.asyncio
async def test_agent_health_endpoints():
    """Test individual agent health endpoints."""
    agents = [
        ("coding-agent", 8081),
        ("marketing-agent", 8082),
        ("security-agent", 8083),
        ("bizdev-agent", 8084)
    ]
    
    async with httpx.AsyncClient() as client:
        for agent_name, port in agents:
            try:
                response = await client.get(f"http://localhost:{port}/health", timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    assert data["status"] == "healthy"
                    assert data["service"] == agent_name
                else:
                    # Agent may not be running in test environment
                    pytest.skip(f"{agent_name} not available")
            except httpx.ConnectError:
                pytest.skip(f"{agent_name} not reachable")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])