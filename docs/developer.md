# Developer Guide

## Getting Started

This guide helps developers understand, extend, and contribute to the AI-Powered Business Ecosystem.

## Architecture Overview

The system is built using a microservices architecture with the following key components:

- **API Gateway** (FastAPI): Routes requests and handles authentication
- **AI Agents** (LangGraph): Core business logic for each domain
- **External Actions**: Integrations with GitLab, Twitter, Slack, CRMs
- **LLM Abstraction**: Unified interface for OpenAI and local models
- **Supporting Services**: Licensing, metrics, monitoring

## Development Setup

### Prerequisites

```bash
# Required tools
python 3.11+
docker & docker-compose
git

# Optional for local development
node.js (for frontend development)
kubectl & helm (for K8s deployment)
```

### Local Environment

```bash
# Clone and setup
git clone https://github.com/your-org/ai-ecosystem.git
cd ai-ecosystem

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r api/requirements.txt
pip install -r llm/requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys
```

### Running Services Locally

```bash
# Start infrastructure services only
docker compose up -d postgres redis keycloak

# Run API gateway locally
cd api
python main.py

# Run agents individually (in separate terminals)
cd agents/coding_agent && python server.py
cd agents/marketing_agent && python server.py
cd agents/security_agent && python server.py
cd agents/bizdev_agent && python server.py
```

## Creating a New Agent

### 1. Agent Structure

Create a new agent following this structure:

```
agents/new_agent/
├── __init__.py
├── agent.py          # Main agent logic with LangGraph
├── actions.py        # External API interactions
├── server.py         # HTTP server (FastAPI)
├── Dockerfile
├── requirements.txt
└── tests/
    └── test_agent.py
```

### 2. Agent Implementation

```python
# agents/new_agent/agent.py
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain.schema import HumanMessage, SystemMessage
from llm.openai_client import llm

class NewAgentState(TypedDict):
    """State for the new agent workflow."""
    input_data: Dict[str, Any]
    processed_data: Dict[str, Any]
    result: str
    error: str

class NewAgent:
    """AI agent for [specific domain]."""
    
    def __init__(self):
        self.graph = StateGraph(NewAgentState)
        self._build_graph()
        self.workflow = self.graph.compile()
    
    def _build_graph(self):
        """Build the StateGraph workflow."""
        
        async def process_step(state: NewAgentState) -> NewAgentState:
            # Implement your processing logic
            try:
                # Use LLM for intelligent processing
                messages = [
                    SystemMessage(content="You are an expert in [domain]"),
                    HumanMessage(content=f"Process: {state['input_data']}")
                ]
                response = await llm.agenerate(messages)
                
                return {
                    **state,
                    "result": response[0].content,
                    "processed_data": {"status": "complete"}
                }
            except Exception as e:
                return {**state, "error": str(e)}
        
        # Define workflow
        self.graph.add_node("process", process_step)
        self.graph.add_edge(START, "process")
        self.graph.add_edge("process", END)
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent workflow."""
        initial_state = NewAgentState(
            input_data=input_data,
            processed_data={},
            result="",
            error=""
        )
        
        try:
            final_state = await self.workflow.ainvoke(initial_state)
            
            if final_state.get("error"):
                return {"success": False, "error": final_state["error"]}
            
            return {
                "success": True,
                "result": final_state["result"],
                "data": final_state["processed_data"]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
```

### 3. HTTP Server

```python
# agents/new_agent/server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .agent import NewAgent

app = FastAPI(title="New Agent")
agent = NewAgent()

class ProcessRequest(BaseModel):
    data: dict

@app.post("/process")
async def process_data(request: ProcessRequest):
    result = await agent.execute(request.data)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "new-agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8086)
```

### 4. Add to API Gateway

```python
# In api/main.py, add:

NEW_AGENT_URL = os.getenv("NEW_AGENT_URL", "http://localhost:8086")

@app.post("/api/new_agent/process")
async def trigger_new_agent(request: ProcessRequest, user_info = Depends(verify_token)):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{NEW_AGENT_URL}/process",
            json=request.dict(),
            timeout=60.0
        )
        response.raise_for_status()
        return response.json()
```

### 5. Add to Docker Compose

```yaml
# In docker-compose.yaml, add:

new-agent:
  build: ./agents/new_agent
  ports:
    - "8086:8086"
  environment:
    - OPENAI_API_KEY=${OPENAI_API_KEY}
  networks:
    - ecosystem
```

## External API Integration

### Adding New External APIs

1. Create integration in `actions/new_service.py`:

```python
# actions/new_service.py
import httpx
import os
from typing import Dict, Any

class NewServiceClient:
    def __init__(self):
        self.api_key = os.getenv("NEW_SERVICE_API_KEY")
        self.base_url = "https://api.newservice.com/v1"
    
    async def call_api(self, data: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/endpoint",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=data
            )
            response.raise_for_status()
            return response.json()

# Export convenience function
client = NewServiceClient()

async def perform_action(data: Dict[str, Any]) -> Dict[str, Any]:
    return await client.call_api(data)
```

2. Use in agent actions:

```python
# agents/your_agent/actions.py
from actions.new_service import perform_action

async def agent_action(input_data):
    result = await perform_action(input_data)
    return result
```

## LLM Integration

### Using Different LLM Providers

```python
# For OpenAI (default)
from llm.openai_client import llm

# For local models
from llm.local_client import LocalClient
local_llm = LocalClient(model="llama2:70b")

# Usage in agents
async def generate_response(prompt: str):
    messages = [HumanMessage(content=prompt)]
    response = await llm.agenerate(messages)
    return response[0].content
```

### Prompt Engineering Best Practices

```python
def create_system_prompt(domain: str, role: str) -> str:
    return f"""
    You are a {role} expert specializing in {domain}.
    
    Guidelines:
    - Be concise and actionable
    - Use domain-specific terminology appropriately
    - Provide specific recommendations
    - Format responses consistently
    
    Always respond in valid JSON format when requested.
    """

def create_user_prompt(task: str, context: Dict[str, Any]) -> str:
    return f"""
    Task: {task}
    
    Context:
    {json.dumps(context, indent=2)}
    
    Please provide a detailed response following the guidelines.
    """
```

## Testing

### Unit Tests

```python
# tests/test_new_agent.py
import pytest
from agents.new_agent.agent import NewAgent

@pytest.mark.asyncio
async def test_agent_processing():
    agent = NewAgent()
    result = await agent.execute({"test": "data"})
    
    assert result["success"] is True
    assert "result" in result
```

### Integration Tests

```python
# tests/test_integration_new_agent.py
import pytest
import httpx

@pytest.mark.asyncio
async def test_agent_endpoint():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8086/process",
            json={"data": {"test": "value"}}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run specific test file
pytest tests/test_new_agent.py -v

# Run all tests
pytest tests/ -v

# Run with coverage
pip install pytest-cov
pytest tests/ --cov=agents --cov-report=html
```

## Monitoring and Observability

### Adding Metrics

```python
# In your agent/service
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('agent_requests_total', 'Total requests', ['agent', 'method'])
REQUEST_DURATION = Histogram('agent_request_duration_seconds', 'Request duration')

@app.middleware("http")
async def add_metrics(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(agent="new_agent", method=request.method).inc()
    REQUEST_DURATION.observe(duration)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Structured Logging

```python
import logging
import json

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def info(self, message: str, **kwargs):
        log_data = {
            "level": "info",
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        self.logger.info(json.dumps(log_data))

# Usage
logger = StructuredLogger("new_agent")
logger.info("Processing request", user_id="123", request_id="abc")
```

## Security Guidelines

### Input Validation

```python
from pydantic import BaseModel, validator

class AgentRequest(BaseModel):
    data: Dict[str, Any]
    
    @validator('data')
    def validate_data(cls, v):
        # Add validation logic
        if not isinstance(v, dict):
            raise ValueError('Data must be a dictionary')
        return v
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/process")
@limiter.limit("5/minute")
async def process_data(request: Request, data: ProcessRequest):
    # Your endpoint logic
    pass
```

### Environment Variables

```python
import os
from typing import Optional

def get_required_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Required environment variable {key} is not set")
    return value

def get_optional_env(key: str, default: str) -> str:
    return os.getenv(key, default)

# Usage
API_KEY = get_required_env("NEW_SERVICE_API_KEY")
DEBUG = get_optional_env("DEBUG", "false").lower() == "true"
```

## Deployment

### Building Images

```bash
# Build specific agent
docker build -t your-org/new-agent agents/new_agent

# Build all images
docker compose build

# Push to registry
docker tag your-org/new-agent registry.example.com/new-agent:v1.0.0
docker push registry.example.com/new-agent:v1.0.0
```

### Environment Configuration

```yaml
# docker-compose.override.yml for local development
version: '3.8'
services:
  new-agent:
    environment:
      - DEBUG=true
      - LOG_LEVEL=debug
    volumes:
      - ./agents/new_agent:/app
```

## Contributing

### Code Style

```bash
# Install development tools
pip install black flake8 isort mypy

# Format code
black agents/ api/ llm/
isort agents/ api/ llm/

# Lint code
flake8 agents/ api/ llm/ --max-line-length=100

# Type checking
mypy agents/new_agent/
```

### Pull Request Process

1. Create feature branch: `git checkout -b feature/new-agent`
2. Implement changes with tests
3. Run linting and tests: `make test lint`
4. Update documentation
5. Submit pull request with description
6. Address review feedback

### Documentation

- Update `README.md` for user-facing changes
- Update `docs/` for architectural changes
- Add inline docstrings for new functions
- Update API documentation in FastAPI apps

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Import errors | Check Python path and virtual environment |
| API key errors | Verify environment variables are set |
| Connection timeouts | Check service health and network connectivity |
| Memory issues | Increase container limits or optimize code |

### Debugging

```bash
# Check service logs
docker compose logs -f new-agent

# Connect to container
docker compose exec new-agent bash

# Debug with Python
python -c "from agents.new_agent.agent import NewAgent; print('OK')"
```