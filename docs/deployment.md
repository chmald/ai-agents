# Deployment Guide

## Prerequisites

Before deploying the AI-Powered Business Ecosystem, ensure you have:

- **Docker & Docker Compose** v2.20+
- **Kubernetes** v1.25+ (for production deployment)
- **Helm** v3.10+ (for Kubernetes deployment)
- **External API Keys** (OpenAI, GitLab, Twitter, Salesforce, Slack)

## Local Development Deployment

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/your-org/ai-ecosystem.git
cd ai-ecosystem

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 2. Required API Keys

Configure the following in your `.env` file:

```bash
# Required
OPENAI_API_KEY=your-openai-api-key

# Optional but recommended
GITLAB_TOKEN=your-gitlab-token
TWITTER_BEARER_TOKEN=your-twitter-token
SLACK_BOT_TOKEN=your-slack-token
SALESFORCE_ACCESS_TOKEN=your-salesforce-token
```

### 3. Start the Stack

```bash
# Start all services
docker compose up -d

# Check service status
docker compose ps

# View logs
docker compose logs -f api-gateway
```

### 4. Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| API Gateway | http://localhost:8000 | JWT token required |
| API Documentation | http://localhost:8000/docs | - |
| Keycloak Admin | http://localhost:8080 | admin/admin |
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | - |
| Traefik Dashboard | http://localhost:8090 | - |

## Production Deployment

### Docker Compose Production

For small to medium deployments:

```bash
# Production compose file
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

For large-scale production deployments:

```bash
# Install using Helm
helm repo add ai-ecosystem ./deploy/helm
helm install ai-ecosystem ai-ecosystem/ai-ecosystem \
  --set global.domain=your-domain.com \
  --set global.tls.enabled=true \
  --set agents.replicas=3
```

#### Kubernetes Configuration

```yaml
# values.yaml
global:
  domain: your-domain.com
  tls:
    enabled: true
    issuer: letsencrypt-prod

api:
  replicas: 2
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 1000m
      memory: 2Gi

agents:
  replicas: 2
  resources:
    requests:
      cpu: 1000m
      memory: 2Gi
    limits:
      cpu: 2000m
      memory: 4Gi

database:
  type: postgresql
  replicas: 3
  storage: 100Gi

redis:
  cluster:
    enabled: true
    nodes: 3

monitoring:
  prometheus:
    enabled: true
    storage: 50Gi
  grafana:
    enabled: true
    ingress:
      enabled: true
```

### Cloud Deployment Options

#### AWS EKS

```bash
# Create EKS cluster
eksctl create cluster --name ai-ecosystem --region us-west-2

# Deploy using Helm
helm install ai-ecosystem ./deploy/helm/ai-ecosystem \
  --set cloud.provider=aws \
  --set database.type=rds \
  --set storage.type=efs
```

#### Google GKE

```bash
# Create GKE cluster
gcloud container clusters create ai-ecosystem \
  --machine-type=n1-standard-4 \
  --num-nodes=3

# Deploy using Helm
helm install ai-ecosystem ./deploy/helm/ai-ecosystem \
  --set cloud.provider=gcp \
  --set database.type=cloud-sql
```

#### Azure AKS

```bash
# Create AKS cluster
az aks create --resource-group ai-ecosystem \
  --name ai-ecosystem \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3

# Deploy using Helm
helm install ai-ecosystem ./deploy/helm/ai-ecosystem \
  --set cloud.provider=azure \
  --set database.type=azure-postgresql
```

## Scaling Configuration

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Vertical Pod Autoscaler

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: agents-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: coding-agent
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: coding-agent
      maxAllowed:
        cpu: 4
        memory: 8Gi
      minAllowed:
        cpu: 100m
        memory: 128Mi
```

## Database Setup

### PostgreSQL Configuration

```sql
-- Initialize database schema
CREATE DATABASE ecosystem;
CREATE USER ecosystem WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ecosystem TO ecosystem;

-- Create tenant isolation schema
CREATE SCHEMA tenant_demo;
GRANT ALL ON SCHEMA tenant_demo TO ecosystem;
```

### Redis Configuration

```yaml
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
appendonly yes
appendfsync everysec
```

## Security Configuration

### TLS/SSL Setup

```yaml
# ingress-tls.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-ecosystem-ingress
  annotations:
    kubernetes.io/ingress.class: traefik
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.your-domain.com
    secretName: api-tls
  rules:
  - host: api.your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-gateway
            port:
              number: 8000
```

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ai-ecosystem-network-policy
spec:
  podSelector:
    matchLabels:
      app: ai-ecosystem
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: traefik
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
```

## Monitoring Setup

### Prometheus Configuration

```yaml
# monitoring.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'ai-ecosystem'
      kubernetes_sd_configs:
      - role: pod
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
```

### Alerting Rules

```yaml
groups:
- name: ai-ecosystem-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: High error rate detected
      
  - alert: HighMemoryUsage
    expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: Container memory usage is above 90%
```

## Backup and Disaster Recovery

### Database Backups

```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
pg_dump -h postgres -U ecosystem ecosystem > "$BACKUP_DIR/backup_$DATE.sql"

# Cleanup old backups (keep 7 days)
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

### Disaster Recovery Plan

1. **RTO (Recovery Time Objective)**: 30 minutes
2. **RPO (Recovery Point Objective)**: 1 hour
3. **Backup Frequency**: Every 6 hours
4. **Backup Retention**: 30 days
5. **Multi-region Deployment**: Primary/Secondary setup

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Agent not responding | Check health endpoints, restart if needed |
| Database connection failed | Verify credentials and network connectivity |
| High memory usage | Scale up resources or optimize queries |
| API rate limits | Implement request queuing and throttling |

### Debugging Commands

```bash
# Check pod status
kubectl get pods -n ai-ecosystem

# View logs
kubectl logs -f deployment/api-gateway -n ai-ecosystem

# Execute commands in pod
kubectl exec -it deployment/api-gateway -- /bin/bash

# Port forward for local access
kubectl port-forward service/api-gateway 8000:8000 -n ai-ecosystem
```