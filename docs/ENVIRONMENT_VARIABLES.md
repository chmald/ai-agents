# Environment Variables Reference

This document details all environment variables used in the AI-Powered Business Ecosystem, indicating which are **required** for the application to start and which are **optional**.

## 🚨 **Minimum Required Variables (To Start Application)**

**NONE!** 

The application can start with **zero environment variables** and will run in **demo mode** with mock responses. However, for actual functionality with AI agents, you need Azure OpenAI credentials.

## ✅ **Required for Full AI Functionality**

These variables are required if you want the AI agents to actually call Azure OpenAI:

| Variable | Description | Example | Required For |
|----------|-------------|---------|--------------|
| `AZURE_OPENAI_API_KEY` | Your Azure OpenAI API key | `abc123def456...` | All AI agent functionality |
| `AZURE_OPENAI_ENDPOINT` | Your Azure OpenAI endpoint URL | `https://my-resource.openai.azure.com/` | All AI agent functionality |

**Without these**: Agents will run in **demo mode** and return mock responses like:
```
[DEMO MODE] Response to: Your request...
```

## 🔧 **Optional Azure OpenAI Variables**

These have sensible defaults and only need to be set if you want different values:

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Model deployment name in Azure | `gpt-4o-mini` | `gpt-4o`, `my-custom-deployment` |
| `AZURE_OPENAI_API_VERSION` | Azure OpenAI API version | `2024-02-15-preview` | `2023-12-01-preview` |

## 🌐 **External Service Integrations (All Optional)**

All external service integrations are **optional**. Without them, the system returns mock responses.

### GitLab Integration (Coding Agent)

| Variable | Description | Default | Mock Behavior |
|----------|-------------|---------|---------------|
| `GITLAB_TOKEN` | GitLab personal access token | None | Returns mock MR URLs |
| `GITLAB_URL` | GitLab API endpoint | `https://gitlab.com/api/v4` | Uses default GitLab.com |

**Without GitLab token**: Coding agent returns mock merge request like:
```json
{
  "id": 12345,
  "web_url": "https://gitlab.com/demo/demo/-/merge_requests/12345",
  "title": "Automated code changes",
  "state": "opened"
}
```

### Slack Integration (Marketing & BizDev Agents)

| Variable | Description | Default | Mock Behavior |
|----------|-------------|---------|---------------|
| `SLACK_BOT_TOKEN` | Slack bot OAuth token (starts with `xoxb-`) | None | Returns mock message timestamps |

**Without Slack token**: Agents return mock message confirmation:
```json
{
  "ok": true,
  "ts": "1234567890.123456",
  "channel": "#marketing",
  "message": {"text": "Your message"}
}
```

### Twitter/X Integration (Marketing Agent)

| Variable | Description | Default | Mock Behavior |
|----------|-------------|---------|---------------|
| `TWITTER_BEARER_TOKEN` | Twitter API v2 bearer token | None | Returns mock tweet IDs |
| `TWITTER_API_KEY` | Twitter API key | None | Not actively used |
| `TWITTER_API_SECRET` | Twitter API secret | None | Not actively used |
| `TWITTER_ACCESS_TOKEN` | Twitter access token | None | Not actively used |
| `TWITTER_ACCESS_TOKEN_SECRET` | Twitter access token secret | None | Not actively used |

**Note**: Only `TWITTER_BEARER_TOKEN` is typically needed for posting tweets.

**Without Twitter credentials**: Marketing agent returns mock tweet data.

### Salesforce Integration (BizDev Agent)

| Variable | Description | Default | Mock Behavior |
|----------|-------------|---------|---------------|
| `SALESFORCE_INSTANCE_URL` | Your Salesforce instance URL | None | Returns mock lead IDs |
| `SALESFORCE_ACCESS_TOKEN` | Salesforce OAuth access token | None | Returns mock lead IDs |

**Without Salesforce credentials**: BizDev agent returns mock lead creation:
```json
{
  "id": "00Q1234567890ABC",
  "success": true
}
```

## 🗄️ **Infrastructure Variables (Docker Compose)**

These are **automatically set** by Docker Compose and typically don't need manual configuration:

| Variable | Description | Default (Docker Compose) |
|----------|-------------|--------------------------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://ecosystem:password@postgres:5432/ecosystem` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379` |
| `CODING_AGENT_URL` | Internal URL for coding agent | `http://coding-agent:8081` |
| `MARKETING_AGENT_URL` | Internal URL for marketing agent | `http://marketing-agent:8082` |
| `SECURITY_AGENT_URL` | Internal URL for security agent | `http://security-agent:8083` |
| `BIZDEV_AGENT_URL` | Internal URL for bizdev agent | `http://bizdev-agent:8084` |

**Note**: When running with `docker compose`, these are set automatically by the compose file.

## 🛠️ **Application Configuration (Optional)**

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `ENV` | Environment type | `development` | `development`, `staging`, `production` |
| `DEBUG` | Enable debug mode | `false` | `true`, `false` |
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `PORT` | API Gateway port | `8000` | Any valid port number |

## 📋 **Quick Start Configurations**

### Minimal Setup (Demo Mode)
```bash
# No variables needed - everything runs in mock mode
# Just run: docker compose up -d
```

### Basic Setup (Azure OpenAI Only)
```bash
# Only 2 variables needed for real AI functionality
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
```

### Full Setup (All Features)
```bash
# Azure OpenAI
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# External Services
GITLAB_TOKEN=glpat-your-token
SLACK_BOT_TOKEN=xoxb-your-token
TWITTER_BEARER_TOKEN=your-bearer-token
SALESFORCE_INSTANCE_URL=https://your-instance.salesforce.com
SALESFORCE_ACCESS_TOKEN=your-access-token
```

## 🔍 **How to Check What's Configured**

After starting the application, check the health endpoint:

```bash
curl http://localhost:8000/health
```

This will show which agents are reachable and their status.

## 🎯 **Recommended Setups by Use Case**

### 1. **Local Development & Testing**
```bash
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
DEBUG=true
LOG_LEVEL=DEBUG
```

### 2. **Demo / Presentation Mode**
```bash
# No variables - runs entirely in mock mode
# Perfect for demos without spending API credits
```

### 3. **Coding Agent Only**
```bash
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
GITLAB_TOKEN=your-gitlab-token
```

### 4. **Marketing Agent Only**
```bash
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
SLACK_BOT_TOKEN=your-slack-token
TWITTER_BEARER_TOKEN=your-twitter-token
```

### 5. **Production Deployment**
```bash
# All credentials
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
GITLAB_TOKEN=your-gitlab-token
SLACK_BOT_TOKEN=your-slack-token
TWITTER_BEARER_TOKEN=your-twitter-token
SALESFORCE_INSTANCE_URL=https://your-instance.salesforce.com
SALESFORCE_ACCESS_TOKEN=your-salesforce-token

# Production settings
ENV=production
DEBUG=false
LOG_LEVEL=INFO
```

## 🔐 **Security Best Practices**

1. **Never commit `.env` file** to version control
2. **Use Azure Key Vault** in production for secrets
3. **Rotate credentials regularly** (especially API keys)
4. **Use environment-specific files**:
   - `.env.development`
   - `.env.staging`
   - `.env.production`

## 📝 **Setting Up Your `.env` File**

```bash
# Copy the example file
cp .env.example .env

# Edit with your credentials
nano .env  # or use your preferred editor

# Only fill in what you need
# Leave unused variables blank or commented out
```

## 🧪 **Testing Configuration**

### Test Azure OpenAI Connection
```bash
# If configured correctly, agents return AI-generated responses
curl -X POST http://localhost:8000/api/coding_agent/consume \
  -H "Content-Type: application/json" \
  -d '{"repo":"test/repo","branch":"main","requirements":"test"}'

# Look for actual AI response vs [DEMO MODE] prefix
```

### Test External Services
```bash
# Check GitLab
curl -X POST http://localhost:8000/api/coding_agent/consume \
  -H "Content-Type: application/json" \
  -d '{"repo":"your-org/your-repo","branch":"test","requirements":"test feature"}'

# Check Slack  
curl -X POST http://localhost:8000/api/marketing_agent/draft \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","body":"Test message"}'
```

## 🆘 **Troubleshooting**

### Application Won't Start
- **Check**: Docker is running
- **Check**: No port conflicts on 8000-8084
- **Solution**: Application should start even without any variables

### AI Agents Return Demo Responses
- **Check**: `AZURE_OPENAI_API_KEY` is set
- **Check**: `AZURE_OPENAI_ENDPOINT` is set
- **Check**: No typos in variable names
- **Solution**: Set both Azure OpenAI variables

### External Service Errors
- **Check**: Specific service token is set
- **Check**: Token has necessary permissions
- **Note**: Missing tokens trigger mock mode (not errors)

### Environment Variables Not Loading
- **Check**: `.env` file exists in project root
- **Check**: Variable names match exactly (case-sensitive)
- **Check**: No spaces around `=` sign
- **Check**: No quotes around values (unless needed)

## 📞 **Getting API Credentials**

### Azure OpenAI
1. Azure Portal → Create Azure OpenAI resource
2. Deploy a model (e.g., gpt-4o-mini)
3. Keys and Endpoint → Copy key and endpoint

### GitLab
1. GitLab → User Settings → Access Tokens
2. Scopes: `api`, `write_repository`
3. Copy generated token

### Slack
1. api.slack.com → Create New App
2. OAuth & Permissions → Bot Token Scopes
3. Install to Workspace → Copy Bot User OAuth Token

### Twitter/X
1. developer.twitter.com → Developer Portal
2. Create Project and App
3. Keys and Tokens → Generate Bearer Token

### Salesforce
1. Salesforce → Setup → Apps → App Manager
2. Create Connected App
3. OAuth Settings → Get credentials

---

**Summary**: Start with just Azure OpenAI credentials for AI functionality. Add external service tokens only when you need those specific features. Everything else has sensible defaults or runs in mock mode!
