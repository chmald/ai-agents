# 🌐 AI‑Powered Business Ecosystem  
**A multi‑tenant, agent‑based platform that automates coding, security, marketing, and business‑development.**  

> The project is split into micro‑services that can be run locally, in Kubernetes, or in a SaaS‑style "multi‑tenant" deployment.  
> Each agent is a thin wrapper around an LLM (GPT‑4o‑mini or Llama‑2‑70B).  
> The stack is intentionally container‑native so that you can ship a single `docker‑compose.yaml` to a new customer, or build a Helm chart for a managed Kubernetes deployment.  

---

## Table of Contents  

| Section | What it contains |
|---------|------------------|
| [`repo/`](#repo) | Project layout |
| [`docker‑compose.yaml`](#docker-composeyaml) | Local dev stack |
| [`agents/`](#agents) | Code for each agent |
| [`services/`](#services) | Non‑agent services (licensing, metrics, auth) |
| [`actions/`](#actions) | Thin wrappers around external APIs (GitLab, Twitter, Salesforce, Slack) |
| [`llm/`](#llm) | LLM client abstraction |
| [`docs/`](#docs) | Architecture, deployment guides, and docs |
| [`README.md`](#readme) | This file (the one you're reading) |

---

## 📁 Repo Layout  

```
ai‑ecosystem/
├── README.md
├── docker‑compose.yaml
├── api/
│   ├── main.py            # FastAPI gateway
│   ├── requirements.txt
│   └── Dockerfile
├── agents/
│   ├── coding_agent/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── actions.py
│   │   └── Dockerfile
│   ├── security_agent/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── actions.py
│   │   └── Dockerfile
│   ├── marketing_agent/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── actions.py
│   │   └── Dockerfile
│   └── bizdev_agent/
│       ├── __init__.py
│       ├── agent.py
│       ├── actions.py
│       └── Dockerfile
├── services/
│   ├── licensing/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── metrics/
│       └── (Prometheus scrape config, Grafana dashboards)
├── llm/
│   ├── openai_client.py
│   ├── local_client.py
│   └── Dockerfile
├── actions/
│   ├── gitlab.py
│   ├── twitter.py
│   ├── slack.py
│   ├── crm.py
│   └── Dockerfile
├── docs/
│   ├── architecture.md
│   ├── deployment.md
│   └── developer.md
└── .github/
    └── workflows/
        └── ci.yml
```

> **Tip:** Each agent lives in its own folder, so you can build it independently (`docker build -t myorg/coding-agent agents/coding_agent`).  

---

## ⚙️ Local Development

### Prerequisites  

| Tool | Version | Install |
|------|---------|---------|
| Docker | ≥ 24.0 | `brew install docker` |
| Docker‑Compose | v2.20+ | `brew install docker-compose` |
| Git | ≥ 2.30 | `brew install git` |

> If you prefer Kubernetes, the repo contains a Helm chart in `deploy/helm/`.

### 1️⃣ Spin up the full stack

```bash
# From the project root
docker compose up -d
```

> *What it starts:*  
> - API Gateway (FastAPI) – port **8000**  
> - Redis & Kafka – used by the Celery orchestrator  
> - Keycloak – OIDC for multi‑tenant auth (port **8080**)  
> - PostgreSQL – stores tenants, usage logs, agent registry  
> - Licensing Service – records token usage  
> - All four agents, each on a separate container

### 2️⃣ Configure Keycloak

```bash
# Add a test realm
docker compose exec keycloak bash -c "kcadm.sh create realms -s realm=demo"

# Create a client
docker compose exec keycloak bash -c "kcadm.sh create clients -r demo -s clientId=ecosystem -s 'public-client'=true -s 'standard-flow-enabled'=true"
```

> After this you'll get a client secret that you can store in an `.env` file and pass to the API Gateway.

### 3️⃣ Create a test tenant

```bash
# API call (replace TOKEN with a JWT from Keycloak)
curl -X POST http://localhost:8000/api/tenants \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name":"demo‑client"}'
```

### 4️⃣ Test the **Coding Agent**

```bash
# Create a PR via GitLab or manually trigger the agent
curl -X POST http://localhost:8000/api/coding_agent/consume \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"repo":"gitlab.com/demo/demo", "branch":"feature/codify"}'
```

> The agent will create an MR with the updated code.

### 5️⃣ Test the **Marketing Agent**

```bash
curl -X POST http://localhost:8000/api/marketing_agent/draft \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title":"New product launch","body":"We are excited to launch..."}'
```

> A tweet will be posted and a Slack message will be sent to `#marketing`.

### 6️⃣ View Metrics

Prometheus automatically scrapes the `/metrics` endpoint on every container.  
Grafana dashboards are in `services/metrics/grafana`.  
Open Grafana: `http://localhost:3000` (user: `admin`, pass: `admin`).

---

## 🔧 Agent Development

### Common patterns  

| File | Purpose |
|------|---------|
| `agent.py` | StateGraph implementation – nodes, edges, LLM calls |
| `actions.py` | Helper functions to talk to external APIs (GitLab, Twitter, Salesforce, Slack).  Each function returns a plain value – keep it stateless. |
| `Dockerfile` | Simple multi‑stage build that installs only the agent's dependencies. |

#### Example: `marketing_agent/agent.py`

```python
from langgraph.graph import StateGraph, START, END
from langchain.schema import HumanMessage
from ..llm.openai_client import llm
from .actions import post_tweet, send_message

class MarketingAgent(StateGraph):
    def __init__(self):
        super().__init__()

        async def generate(state):
            content = state["content"]
            prompt = (
                f"Write a 280‑char tweet from a brand voice. "
                f"Title: {content['title']}. "
                f"Body: {content['body']}"
            )
            response = await llm.agenerate([HumanMessage(content=prompt)])
            return {"tweet": response[0].content.strip()}

        async def publish(state):
            tweet = state["tweet"]
            tweet_id = await post_tweet(tweet)
            await send_message("#marketing", f"✅ Tweet posted: {tweet[:100]}…")
            return {"tweet_id": tweet_id}

        self.add_node("generate", generate)
        self.add_node("publish", publish)
        self.add_edge(START, "generate")
        self.add_edge("generate", "publish")
        self.add_edge("publish", END)

    async def __call__(self, content: dict):
        return await self.run({"content": content})["publish"]
```

> **Tip:** Keep all prompts small (≤ 300 tokens) to stay under the rate‑limit.

### Running a single agent locally

```bash
cd agents/marketing_agent
docker build -t myorg/marketing-agent .
docker run -p 8081:8081 myorg/marketing-agent
```

> The agent now exposes a simple HTTP endpoint (`POST /generate`) that you can hit directly.

---

## 🔒 Security & Compliance

| Layer | Best practice |
|-------|---------------|
| **Auth** | Keycloak with OIDC; JWT scopes per tenant |
| **Data isolation** | Separate DB schema per tenant (PostgreSQL `search_path`) |
| **Secrets** | Vault or AWS Secrets Manager; mount as env vars |
| **Network** | TLS everywhere; Traefik ingress with Let's Encrypt |
| **Audit** | Log every request (API, Celery, agent) with tenant ID |
| **LLM** | If you run an on‑prem LLM, ensure the server is not exposed publicly |
| **GDPR** | Add an opt‑in endpoint for marketing; anonymise lead data |

---

## 📦 Packaging for Customers

| Option | How |
|--------|-----|
| **Docker‑Compose bundle** | Ship `docker‑compose.yaml` + `Dockerfile`s.  Customer pulls, edits credentials, runs `docker compose up -d`. |
| **Helm chart** | `deploy/helm/ai-ecosystem/` – values.yaml lets them set the number of agents, GPU limits, Stripe keys, etc. |
| **SaaS** | Deploy the entire stack to a managed cluster, expose a `tenant‑portal` for users to create tenants, and auto‑spin GPU nodes on demand. |

---

## 📚 Documentation

* `docs/architecture.md` – Full architecture diagram and component description.  
* `docs/deployment.md` – K8s/Helm deployment instructions, scaling, autoscaling.  
* `docs/developer.md` – How to add a new agent, update the LLM, write actions.  

All docs are written in Markdown so you can render them with any static site generator (MkDocs, Hugo, etc.).

---

## 🤝 Contributing

1. Fork the repo.  
2. Create a feature branch.  
3. Add tests (`pytest` for agent logic).  
4. Update the `docs/` folder if you add a new feature.  
5. Open a PR.  

---

## 📞 Get In Touch

* **Email** – dev@ai‑ecosystem.com  
* **Slack** – Join our workspace: `https://ai-ecosystem.slack.com/`  
* **Discord** – `discord.gg/ai-ecosystem`  

Happy building! 🚀
