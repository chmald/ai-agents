# Azure OpenAI Migration Guide

This guide helps you migrate from OpenAI to Azure OpenAI in the AI-Powered Business Ecosystem.

## Why Azure OpenAI?

Azure OpenAI provides several advantages:
- **Enterprise Security**: Enhanced security and compliance features
- **Data Residency**: Keep your data in specific Azure regions
- **Private Network**: Use Azure Virtual Networks for secure communication
- **SLA**: Enterprise-grade service level agreements
- **Cost Management**: Better cost control and budgeting tools
- **Integration**: Seamless integration with other Azure services

## Prerequisites

Before migrating, you need:

1. **Azure Subscription**: An active Azure subscription
2. **Azure OpenAI Resource**: Create an Azure OpenAI resource in the Azure Portal
3. **Model Deployment**: Deploy the desired model (e.g., gpt-4o-mini) in your Azure OpenAI resource
4. **API Credentials**: Obtain your API key and endpoint URL

## Setup Steps

### 1. Create Azure OpenAI Resource

```bash
# Using Azure CLI
az cognitiveservices account create \
  --name your-openai-resource \
  --resource-group your-resource-group \
  --kind OpenAI \
  --sku S0 \
  --location eastus
```

Or create through the Azure Portal:
1. Navigate to Azure Portal → Create a resource
2. Search for "Azure OpenAI"
3. Fill in the required details and create

### 2. Deploy a Model

```bash
# Using Azure CLI
az cognitiveservices account deployment create \
  --name your-openai-resource \
  --resource-group your-resource-group \
  --deployment-name gpt-4o-mini \
  --model-name gpt-4o-mini \
  --model-version "2024-07-18" \
  --model-format OpenAI \
  --sku-capacity 1 \
  --sku-name "Standard"
```

Or through the Azure Portal:
1. Go to your Azure OpenAI resource
2. Navigate to "Model deployments"
3. Click "Create new deployment"
4. Select model and configure deployment

### 3. Get Your Credentials

1. Navigate to your Azure OpenAI resource
2. Go to "Keys and Endpoint"
3. Copy:
   - **Key 1** or **Key 2** (either works)
   - **Endpoint URL** (format: `https://your-resource.openai.azure.com/`)

### 4. Update Environment Variables

Edit your `.env` file:

```bash
# Replace old OpenAI variables
# OPENAI_API_KEY=sk-...

# With Azure OpenAI variables
AZURE_OPENAI_API_KEY=your-azure-openai-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### 5. Restart Services

```bash
# Stop existing services
docker compose down

# Rebuild with new configuration
docker compose up -d --build

# Verify services are healthy
docker compose ps
curl http://localhost:8000/health
```

## Configuration Reference

### Environment Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `AZURE_OPENAI_API_KEY` | Your Azure OpenAI API key | `abc123...` | Yes |
| `AZURE_OPENAI_ENDPOINT` | Your Azure OpenAI endpoint URL | `https://my-resource.openai.azure.com/` | Yes |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Your model deployment name | `gpt-4o-mini` | No (defaults to `gpt-4o-mini`) |
| `AZURE_OPENAI_API_VERSION` | API version to use | `2024-02-15-preview` | No (defaults to `2024-02-15-preview`) |

### Supported API Versions

- `2024-02-15-preview` (recommended)
- `2023-12-01-preview`
- `2023-05-15`

Check the [Azure OpenAI documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference) for the latest versions.

### Supported Models

Common model deployments:
- `gpt-4o-mini` - Latest efficient model
- `gpt-4o` - Latest full model
- `gpt-4-turbo` - Fast and capable
- `gpt-4` - Original GPT-4
- `gpt-35-turbo` - GPT-3.5 Turbo

**Note**: Deployment names in Azure can be customized. Use your actual deployment name in the configuration.

## Code Changes

The migration is mostly configuration-based. The code automatically uses Azure OpenAI when the environment variables are set.

### LLM Client

The `llm/openai_client.py` now uses `AzureChatOpenAI` from LangChain:

```python
from langchain_openai import AzureChatOpenAI

client = AzureChatOpenAI(
    azure_deployment=deployment_name,
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version=api_version,
    temperature=0.7,
    max_tokens=1000
)
```

### Backward Compatibility

The system maintains backward compatibility with the old `OpenAIClient` class name:

```python
# Both work
from llm.openai_client import llm
from llm.openai_client import AzureOpenAIClient
from llm.openai_client import OpenAIClient  # Alias to AzureOpenAIClient
```

## Troubleshooting

### Common Issues

#### 1. Authentication Errors

**Error**: `Unauthorized` or `401` status code

**Solution**: 
- Verify your API key is correct
- Check that the key hasn't expired
- Ensure you're using Key 1 or Key 2 from Azure Portal

#### 2. Endpoint Not Found

**Error**: `Resource not found` or `404` status code

**Solution**:
- Verify the endpoint URL format: `https://YOUR-RESOURCE-NAME.openai.azure.com/`
- Don't include `/openai/deployments/` in the endpoint
- Ensure your resource name is correct

#### 3. Deployment Not Found

**Error**: `Deployment not found` or model name errors

**Solution**:
- Check that the deployment exists in Azure Portal
- Verify the deployment name matches exactly (case-sensitive)
- Ensure the deployment is in the same region as your endpoint

#### 4. Rate Limiting

**Error**: `429 Too Many Requests`

**Solution**:
- Check your deployment's TPM (Tokens Per Minute) limit
- Increase the deployment capacity in Azure Portal
- Implement retry logic with exponential backoff

#### 5. API Version Mismatch

**Error**: API version not supported

**Solution**:
- Use a supported API version (see Configuration Reference above)
- Update to the latest stable version: `2024-02-15-preview`

### Debug Mode

Enable debug logging to troubleshoot issues:

```bash
# In your .env file
LOG_LEVEL=DEBUG
DEBUG=true
```

View detailed logs:

```bash
docker compose logs -f coding-agent
docker compose logs -f api-gateway
```

### Testing Your Configuration

Test your Azure OpenAI setup:

```python
# test_azure_openai.py
import os
from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage

client = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

response = client.invoke([HumanMessage(content="Hello!")])
print(response.content)
```

Run the test:

```bash
python test_azure_openai.py
```

## Cost Optimization

### 1. Monitor Token Usage

Enable metrics collection in Prometheus to track token usage:

```yaml
# Grafana dashboard for token monitoring
- Token consumption per agent
- Cost estimation per request
- Rate limiting metrics
```

### 2. Optimize Prompts

- Keep prompts concise (≤300 tokens recommended)
- Use system messages efficiently
- Cache common responses
- Implement prompt templates

### 3. Scale Deployments

Adjust TPM (Tokens Per Minute) based on usage:

```bash
# Increase deployment capacity
az cognitiveservices account deployment update \
  --name your-openai-resource \
  --resource-group your-resource-group \
  --deployment-name gpt-4o-mini \
  --sku-capacity 10
```

### 4. Use Appropriate Models

- **Development**: Use `gpt-35-turbo` or `gpt-4o-mini` for lower costs
- **Production**: Use `gpt-4o` or `gpt-4-turbo` for better quality
- **Evaluation**: Test with smaller models before scaling

## Security Best Practices

### 1. Protect API Keys

```bash
# Use Azure Key Vault
az keyvault secret set \
  --vault-name your-keyvault \
  --name azure-openai-key \
  --value "your-api-key"
```

### 2. Network Security

Configure private endpoints:

```bash
# Create private endpoint for Azure OpenAI
az network private-endpoint create \
  --resource-group your-resource-group \
  --name openai-private-endpoint \
  --vnet-name your-vnet \
  --subnet your-subnet \
  --private-connection-resource-id /subscriptions/.../OpenAI/... \
  --group-id account \
  --connection-name openai-connection
```

### 3. Enable Managed Identity

Use Azure Managed Identity instead of API keys when possible:

```python
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
# Use credential for authentication
```

### 4. Audit Logging

Enable diagnostic logs:

```bash
az monitor diagnostic-settings create \
  --name openai-diagnostics \
  --resource /subscriptions/.../OpenAI/... \
  --logs '[{"category": "Audit", "enabled": true}]' \
  --workspace your-log-analytics-workspace
```

## Multi-Region Deployment

Deploy across multiple Azure regions for high availability:

```yaml
# docker-compose.override.yml
services:
  coding-agent:
    environment:
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT_PRIMARY}
      - AZURE_OPENAI_ENDPOINT_FAILOVER=${AZURE_OPENAI_ENDPOINT_SECONDARY}
```

Implement failover logic in the client for production resilience.

## Migration Checklist

- [ ] Create Azure OpenAI resource
- [ ] Deploy required models
- [ ] Obtain API credentials
- [ ] Update `.env` file with Azure variables
- [ ] Remove old `OPENAI_API_KEY` from `.env`
- [ ] Rebuild Docker containers
- [ ] Test all agents (coding, marketing, security, bizdev)
- [ ] Verify health check endpoints
- [ ] Monitor logs for errors
- [ ] Update monitoring dashboards
- [ ] Document deployment name and region
- [ ] Set up cost alerts in Azure Portal
- [ ] Configure backup API keys
- [ ] Enable diagnostic logging
- [ ] Update team documentation

## Rollback Plan

If you need to rollback to standard OpenAI:

1. Update `llm/openai_client.py` to use `ChatOpenAI` instead of `AzureChatOpenAI`
2. Restore `OPENAI_API_KEY` in `.env`
3. Remove Azure-specific environment variables
4. Rebuild and restart services

## Support and Resources

### Documentation
- [Azure OpenAI Service Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [LangChain Azure OpenAI Integration](https://python.langchain.com/docs/integrations/chat/azure_chat_openai)
- [Azure OpenAI Pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/)

### Getting Help
- Azure OpenAI Support: [Azure Support Portal](https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade)
- Project Issues: [GitHub Issues](https://github.com/chmald/ai-agents/issues)
- Community: [Project Discussions](https://github.com/chmald/ai-agents/discussions)

## Next Steps

After successful migration:

1. **Monitor Performance**: Track latency, success rates, and costs
2. **Optimize Deployments**: Adjust capacity based on usage patterns
3. **Implement Caching**: Add Redis caching for common prompts
4. **Set Up Alerts**: Configure Azure Monitor alerts for issues
5. **Document Configuration**: Keep a record of all deployment settings
6. **Train Team**: Ensure team understands the new setup
7. **Plan Scaling**: Prepare for increased usage and costs

---

**Last Updated**: October 21, 2025
**Version**: 1.0.0
