# Quick Start with Azure OpenAI

This guide will help you get the AI-Powered Business Ecosystem running locally with Azure OpenAI.

## Prerequisites

- **Docker Desktop** installed and running
- **Azure subscription** with Azure OpenAI access
- **Git** installed

## Step 1: Set Up Azure OpenAI

### Option A: Using Azure Portal

1. **Create Azure OpenAI Resource**
   - Go to [Azure Portal](https://portal.azure.com)
   - Search for "Azure OpenAI" and click Create
   - Fill in:
     - Subscription: Your subscription
     - Resource Group: Create new or use existing
     - Region: Choose closest region (e.g., East US, West Europe)
     - Name: Choose a unique name (e.g., `my-ai-agents-openai`)
     - Pricing Tier: Standard S0
   - Click "Review + Create" then "Create"

2. **Deploy a Model**
   - Navigate to your Azure OpenAI resource
   - Click "Go to Azure OpenAI Studio" or go to [Azure OpenAI Studio](https://oai.azure.com)
   - Go to "Deployments" → "Create new deployment"
   - Select:
     - Model: `gpt-4o-mini` (recommended) or `gpt-4o`
     - Deployment name: `gpt-4o-mini` (or your preferred name)
     - Capacity: Start with 1, increase as needed
   - Click "Create"

3. **Get Your Credentials**
   - In Azure Portal, go to your Azure OpenAI resource
   - Click "Keys and Endpoint" under Resource Management
   - Copy:
     - **KEY 1** (your API key)
     - **Endpoint** (should look like `https://YOUR-RESOURCE.openai.azure.com/`)

### Option B: Using Azure CLI

```bash
# Login to Azure
az login

# Create resource group
az group create --name ai-agents-rg --location eastus

# Create Azure OpenAI resource
az cognitiveservices account create \
  --name my-ai-agents-openai \
  --resource-group ai-agents-rg \
  --kind OpenAI \
  --sku S0 \
  --location eastus

# Deploy the model
az cognitiveservices account deployment create \
  --name my-ai-agents-openai \
  --resource-group ai-agents-rg \
  --deployment-name gpt-4o-mini \
  --model-name gpt-4o-mini \
  --model-version "2024-07-18" \
  --model-format OpenAI \
  --sku-capacity 1 \
  --sku-name "Standard"

# Get your API key and endpoint
az cognitiveservices account keys list \
  --name my-ai-agents-openai \
  --resource-group ai-agents-rg

az cognitiveservices account show \
  --name my-ai-agents-openai \
  --resource-group ai-agents-rg \
  --query "properties.endpoint" \
  --output tsv
```

## Step 2: Clone and Configure the Project

```bash
# Clone the repository
git clone https://github.com/chmald/ai-agents.git
cd ai-agents

# Copy environment template
cp .env.example .env
```

## Step 3: Configure Environment Variables

Edit the `.env` file with your Azure OpenAI credentials:

```bash
# Azure OpenAI Configuration (REQUIRED)
AZURE_OPENAI_API_KEY=your-api-key-from-azure-portal
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Optional: External Service Integrations
# Leave these blank to use mock/demo mode

# GitLab (for Coding Agent)
GITLAB_TOKEN=
GITLAB_URL=https://gitlab.com/api/v4

# Twitter (for Marketing Agent)
TWITTER_BEARER_TOKEN=
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_TOKEN_SECRET=

# Slack (for Marketing & BizDev Agents)
SLACK_BOT_TOKEN=

# Salesforce (for BizDev Agent)
SALESFORCE_INSTANCE_URL=
SALESFORCE_ACCESS_TOKEN=

# Application Configuration
ENV=development
DEBUG=true
LOG_LEVEL=INFO
```

### Important Notes:

- **AZURE_OPENAI_ENDPOINT**: Must include the protocol (`https://`) and end with a forward slash
- **AZURE_OPENAI_DEPLOYMENT_NAME**: Must match exactly the deployment name you created in Azure
- **External services**: Can be left blank - agents will use mock responses for testing

## Step 4: Start the Application

### Windows (PowerShell)

```powershell
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Check service status
docker compose ps
```

### Linux/Mac

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Check service status
docker compose ps
```

## Step 5: Verify Installation

### Check System Health

Open your browser or use curl:

```bash
# Check API Gateway
curl http://localhost:8000/health

# View API documentation
# Open: http://localhost:8000/docs
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "agents": {
    "coding": "healthy",
    "marketing": "healthy",
    "security": "healthy",
    "bizdev": "healthy"
  }
}
```

### Test an Agent

```bash
# Test the Coding Agent
curl -X POST http://localhost:8000/api/coding_agent/consume \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "demo/test-repo",
    "branch": "feature/hello-world",
    "requirements": "Create a Python function that prints Hello World"
  }'
```

## Step 6: Access the Services

Once running, you can access:

| Service | URL | Credentials |
|---------|-----|-------------|
| **API Gateway** | http://localhost:8000 | None required |
| **API Documentation** | http://localhost:8000/docs | None required |
| **Grafana** | http://localhost:3000 | admin / admin |
| **Prometheus** | http://localhost:9090 | None required |
| **Keycloak** | http://localhost:8080 | admin / admin |
| **Traefik Dashboard** | http://localhost:8090 | None required |

## Testing All Agents

### Coding Agent
```bash
curl -X POST http://localhost:8000/api/coding_agent/consume \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "myorg/myproject",
    "branch": "feature/new-feature",
    "requirements": "Add a new API endpoint for user authentication"
  }'
```

### Marketing Agent
```bash
curl -X POST http://localhost:8000/api/marketing_agent/draft \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Product Launch Announcement",
    "body": "We are excited to announce the launch of our new AI-powered platform!"
  }'
```

### Security Agent
```bash
curl -X POST http://localhost:8000/api/security_agent/scan \
  -H "Content-Type: application/json" \
  -d '{
    "target": "https://example.com",
    "scan_type": "comprehensive"
  }'
```

### BizDev Agent
```bash
curl -X POST http://localhost:8000/api/bizdev_agent/process_lead \
  -H "Content-Type: application/json" \
  -d '{
    "lead_name": "John Smith",
    "lead_email": "john@example.com",
    "lead_company": "Acme Corp",
    "context": "Interested in enterprise plan"
  }'
```

## Troubleshooting

### Common Issues

#### 1. Docker Services Won't Start

```bash
# Check Docker is running
docker ps

# Check for port conflicts
netstat -an | findstr "8000 8081 8082 8083 8084"  # Windows
lsof -i :8000-8084  # Linux/Mac

# Restart Docker Desktop and try again
```

#### 2. Azure OpenAI Authentication Errors

**Error**: `401 Unauthorized` or `InvalidApiKey`

**Solutions**:
- Verify your API key in `.env` matches Azure Portal
- Check there are no extra spaces or quotes in the `.env` file
- Ensure you copied the full key (should be 32+ characters)
- Try using KEY 2 if KEY 1 doesn't work

#### 3. Deployment Not Found

**Error**: `DeploymentNotFound` or `404` errors

**Solutions**:
- Verify deployment name matches exactly (case-sensitive)
- Check deployment exists in Azure OpenAI Studio
- Ensure deployment is in "Succeeded" state
- Wait a few minutes after creating deployment

#### 4. Endpoint URL Issues

**Error**: Connection refused or invalid endpoint

**Solutions**:
- Ensure endpoint includes `https://`
- Verify endpoint ends with `.openai.azure.com/`
- Check for typos in resource name
- Don't include `/openai/deployments/` in the endpoint URL

### View Detailed Logs

```bash
# All services
docker compose logs

# Specific service
docker compose logs api-gateway
docker compose logs coding-agent

# Follow logs in real-time
docker compose logs -f coding-agent

# Last 100 lines
docker compose logs --tail=100 marketing-agent
```

### Restart a Service

```bash
# Restart specific service
docker compose restart coding-agent

# Rebuild and restart
docker compose up -d --build coding-agent

# Restart all services
docker compose restart
```

### Clean Start

```bash
# Stop everything
docker compose down

# Remove volumes (clean database)
docker compose down -v

# Rebuild and start fresh
docker compose up -d --build
```

## Cost Monitoring

### Check Token Usage

Monitor your Azure OpenAI usage:

1. Go to Azure Portal → Your OpenAI Resource
2. Click "Metrics" under Monitoring
3. Add metrics:
   - Total Calls
   - Total Tokens
   - Token Transaction

### Set Cost Alerts

```bash
# Create a budget alert
az consumption budget create \
  --resource-group ai-agents-rg \
  --budget-name openai-budget \
  --amount 100 \
  --time-grain Monthly \
  --category Cost
```

Or in Azure Portal:
1. Go to Cost Management
2. Create Budget
3. Set threshold alerts (e.g., 80%, 100%, 120%)

### Estimate Costs

Approximate costs for testing (as of October 2025):

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Typical Request |
|-------|----------------------|------------------------|-----------------|
| gpt-4o-mini | $0.15 | $0.60 | ~$0.001 |
| gpt-4o | $5.00 | $15.00 | ~$0.03 |
| gpt-35-turbo | $0.50 | $1.50 | ~$0.003 |

**Recommendation**: Start with `gpt-4o-mini` for development and testing.

## Next Steps

### 1. Explore the API

Visit http://localhost:8000/docs to see all available endpoints and try them interactively.

### 2. Configure External Services

To enable full functionality:

- **GitLab**: Create personal access token with `api` and `write_repository` scopes
- **Slack**: Create a bot app and get bot token
- **Twitter**: Set up developer account and get API keys
- **Salesforce**: Create connected app and get OAuth tokens

### 3. Set Up Monitoring

- Configure Grafana dashboards: http://localhost:3000
- Set up alerts in Prometheus
- Enable Azure Application Insights for production

### 4. Learn More

- Read `docs/architecture.md` for system design
- Check `docs/developer.md` to add custom agents
- Review `docs/azure-openai-migration.md` for advanced configuration

### 5. Production Deployment

- See `docs/deployment.md` for Kubernetes setup
- Configure proper authentication with Keycloak
- Set up SSL/TLS certificates
- Enable proper logging and monitoring
- Implement backup and disaster recovery

## Getting Help

### Documentation
- Project README: `README.md`
- Architecture: `docs/architecture.md`
- Developer Guide: `docs/developer.md`
- Azure OpenAI Guide: `docs/azure-openai-migration.md`

### Support
- GitHub Issues: [Report a bug](https://github.com/chmald/ai-agents/issues)
- Discussions: [Ask questions](https://github.com/chmald/ai-agents/discussions)
- Azure Support: [Azure Portal Support](https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade)

## Cleanup

When you're done testing:

```bash
# Stop services
docker compose down

# Remove volumes and clean up
docker compose down -v

# Optional: Delete Azure resources
az group delete --name ai-agents-rg --yes
```

---

**Congratulations!** 🎉 You now have the AI-Powered Business Ecosystem running with Azure OpenAI!

Start building intelligent automation workflows with your AI agents.
