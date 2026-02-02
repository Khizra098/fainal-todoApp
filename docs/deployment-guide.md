# Deployment Guide

This guide provides detailed instructions for deploying the Containerized Todo Application with AI Assistant to various environments.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [Configuration](#configuration)
5. [Deployment Methods](#deployment-methods)
6. [Post-Deployment Tasks](#post-deployment-tasks)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

## Overview

This application is designed for containerized deployment using Docker and orchestrated with Kubernetes. The deployment includes:

- Frontend service (Next.js)
- Backend API (FastAPI)
- PostgreSQL database
- AI assistant integration
- Verification and monitoring systems

## Prerequisites

### Infrastructure Requirements

- Kubernetes cluster (v1.20 or higher)
- kubectl configured to access the cluster
- Helm 3.x (for Helm deployments)
- Docker registry access (for image deployment)
- SSL certificate (for production deployments)

### Resource Requirements

- **CPU**: Minimum 2 cores, Recommended 4+ cores
- **Memory**: Minimum 4GB RAM, Recommended 8GB+ RAM
- **Storage**: Minimum 10GB, Recommended 50GB+ for production
- **Network**: Inbound access on port 443/80, outbound access to OpenAI API

### Required Accounts/Keys

- OpenAI API key for AI assistant functionality
- Database credentials (if using external database)
- Container registry credentials (if using private registry)

## Environment Setup

### 1. Prepare Kubernetes Cluster

```bash
# Verify kubectl connection
kubectl cluster-info

# Check available nodes
kubectl get nodes

# Verify sufficient resources
kubectl top nodes
```

### 2. Create Namespace

```bash
kubectl create namespace todo-app-prod
kubectl create namespace todo-app-staging
```

### 3. Set Up Storage Class (if needed)

```yaml
# storage-class.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs  # Adjust for your cloud provider
parameters:
  type: gp2
  fsType: ext4
```

```bash
kubectl apply -f storage-class.yaml
```

## Configuration

### 1. Create Secrets

#### Database Secrets

```bash
kubectl create secret generic postgres-secret \
  --from-literal=password=your_secure_password \
  --namespace=todo-app-prod
```

#### Application Secrets

```bash
kubectl create secret generic backend-secrets \
  --from-literal=SECRET_KEY=your_secure_secret_key \
  --from-literal=OPENAI_API_KEY=your_openai_api_key \
  --from-literal=DATABASE_URL=postgresql://todo_user:your_secure_password@postgresql-service:5432/todo_app \
  --namespace=todo-app-prod
```

#### SSL Certificate (for production)

```bash
kubectl create secret tls tls-secret \
  --cert=path/to/cert.pem \
  --key=path/to/key.pem \
  --namespace=todo-app-prod
```

### 2. Configure Environment-Specific Values

Create environment-specific configuration files:

#### Production Values (`values-prod.yaml`)

```yaml
# values-prod.yaml
global:
  environment: production
  domain: your-domain.com

backend:
  replicaCount: 3
  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "1Gi"
      cpu: "500m"
  service:
    type: ClusterIP
    port: 8000

frontend:
  replicaCount: 2
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "200m"
  service:
    type: ClusterIP
    port: 3000

database:
  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "1Gi"
      cpu: "500m"

ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: your-domain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: tls-secret
      hosts:
        - your-domain.com

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
```

#### Staging Values (`values-staging.yaml`)

```yaml
# values-staging.yaml
global:
  environment: staging
  domain: staging.your-domain.com

backend:
  replicaCount: 1
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "200m"

frontend:
  replicaCount: 1
  resources:
    requests:
      memory: "128Mi"
      cpu: "50m"
    limits:
      memory: "256Mi"
      cpu: "100m"

ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: staging.your-domain.com
      paths:
        - path: /
          pathType: Prefix
```

## Deployment Methods

### Method 1: Helm Deployment (Recommended)

#### 1. Add Helm Repository

```bash
# If using a custom chart repository
helm repo add your-repo https://your-chart-repo.com
helm repo update
```

#### 2. Deploy to Staging

```bash
helm install todo-app-staging k8s/helm/ \
  --values k8s/helm/values-staging.yaml \
  --namespace todo-app-staging \
  --create-namespace
```

#### 3. Deploy to Production

```bash
helm install todo-app-prod k8s/helm/ \
  --values k8s/helm/values-prod.yaml \
  --namespace todo-app-prod \
  --create-namespace
```

#### 4. Upgrade Deployment

```bash
# Upgrade with new values
helm upgrade todo-app-prod k8s/helm/ \
  --values k8s/helm/values-prod.yaml \
  --namespace todo-app-prod

# Rollback if needed
helm rollback todo-app-prod --namespace todo-app-prod
```

### Method 2: Kustomize Deployment

#### 1. Deploy Base Resources

```bash
kubectl apply -k k8s/base/
```

#### 2. Deploy Environment-Specific Overlays

```bash
# For production
kubectl apply -k k8s/overlays/production/

# For staging
kubectl apply -k k8s/overlays/staging/
```

### Method 3: Direct Kubernetes Manifests

```bash
# Apply all manifests in order
kubectl apply -f k8s/manifests/namespace.yaml
kubectl apply -f k8s/manifests/database/
kubectl apply -f k8s/manifests/backend/
kubectl apply -f k8s/manifests/frontend/
kubectl apply -f k8s/manifests/ingress.yaml
```

## Post-Deployment Tasks

### 1. Verify Deployment

```bash
# Check all pods are running
kubectl get pods --all-namespaces | grep todo-app

# Check services
kubectl get svc --all-namespaces | grep todo-app

# Check ingress
kubectl get ingress --all-namespaces | grep todo-app

# Check logs
kubectl logs -l app=backend -n todo-app-prod
kubectl logs -l app=frontend -n todo-app-prod
```

### 2. Run Health Checks

```bash
# Test health endpoints
kubectl port-forward -n todo-app-prod svc/backend-service 8000:8000 &
curl http://localhost:8000/health/health
curl http://localhost:8000/health/ready
```

### 3. Initialize Database (if needed)

```bash
# Run database migrations
kubectl exec -it deployment/backend-deployment -n todo-app-prod -- python manage.py migrate

# Seed initial data (if needed)
kubectl exec -it deployment/backend-deployment -n todo-app-prod -- python manage.py seed-data
```

### 4. Run Verification Tests

```bash
# Run feature verification
kubectl exec -it deployment/backend-deployment -n todo-app-prod -- python -c "
from src.services.verification_service import VerificationService
from src.database.database import SessionLocal

db = SessionLocal()
service = VerificationService(db)
stats = service.get_verification_statistics()
print(stats)
"
```

### 5. Set Up Monitoring

```bash
# Install Prometheus/Grafana if not already present
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace
```

## Monitoring and Maintenance

### 1. Application Monitoring

#### Check Resource Usage

```bash
# Monitor CPU/Memory usage
kubectl top pods -n todo-app-prod

# Monitor nodes
kubectl top nodes

# Check HPA status
kubectl get hpa -n todo-app-prod
```

#### Monitor Application Logs

```bash
# Tail logs continuously
kubectl logs -f deployment/backend-deployment -n todo-app-prod
kubectl logs -f deployment/frontend-deployment -n todo-app-prod

# Search for errors
kubectl logs deployment/backend-deployment -n todo-app-prod | grep ERROR
```

### 2. Performance Monitoring

#### Run Performance Tests

```bash
# Execute performance benchmarks
kubectl exec -it deployment/backend-deployment -n todo-app-prod -- python -c "
from src.api.v1.performance_routes import run_performance_benchmark
result = run_performance_benchmark('api-response-time', {'target_value': 200.0})
print(result)
"
```

### 3. Security Monitoring

#### Run Security Scans

```bash
# Execute security scans
kubectl exec -it deployment/backend-deployment -n todo-app-prod -- python -c "
from src.api.v1.security_routes import perform_security_scan_task
import uuid
from src.database.database import SessionLocal

db = SessionLocal()
scan_id = str(uuid.uuid4())
perform_security_scan_task(scan_id, 'dependency_vulnerability', [], db)
"
```

### 4. Regular Maintenance Tasks

#### Update Dependencies

```bash
# Create new deployment with updated image
kubectl set image deployment/backend-deployment backend-container=your-registry/backend:v1.2.3 -n todo-app-prod
kubectl set image deployment/frontend-deployment frontend-container=your-registry/frontend:v1.2.3 -n todo-app-prod
```

#### Backup Database

```bash
# Create database backup
kubectl exec -it deployment/postgresql-deployment -n todo-app-prod -- pg_dump -U todo_user -d todo_app > backup.sql
```

## Troubleshooting

### Common Issues

#### 1. Pods Stuck in Pending State

```bash
# Check events
kubectl describe pod <pod-name> -n todo-app-prod

# Check resource quotas
kubectl describe quota -n todo-app-prod

# Check node resources
kubectl describe nodes
```

#### 2. Application Not Responding

```bash
# Check service endpoints
kubectl get endpoints -n todo-app-prod

# Test internal connectivity
kubectl run test-pod --image=curlimages/curl -it --rm --restart=Never -- curl -v http://backend-service:8000/health/health

# Check firewall/network policies
kubectl get networkpolicy -n todo-app-prod
```

#### 3. Database Connection Issues

```bash
# Test database connectivity
kubectl run pg-client --image=postgres:13 -it --rm --restart=Never -- psql -h postgresql-service -U todo_user -d todo_app

# Check database secrets
kubectl get secret postgres-secret -n todo-app-prod -o yaml
```

#### 4. SSL/TLS Issues

```bash
# Check certificate validity
kubectl get secret tls-secret -n todo-app-prod -o yaml

# Test SSL connection
openssl s_client -connect your-domain.com:443
```

### Diagnostic Commands

```bash
# Comprehensive health check
kubectl get all -n todo-app-prod
kubectl get events -n todo-app-prod --sort-by='.lastTimestamp'
kubectl describe deployment backend-deployment -n todo-app-prod
kubectl describe service backend-service -n todo-app-prod
kubectl describe ingress todo-app-ingress -n todo-app-prod
```

### Rollback Procedures

```bash
# Check deployment history
kubectl rollout history deployment/backend-deployment -n todo-app-prod

# Rollback to previous version
kubectl rollout undo deployment/backend-deployment -n todo-app-prod

# Rollback to specific revision
kubectl rollout undo deployment/backend-deployment -n todo-app-prod --to-revision=2
```

## Best Practices

1. **Blue-Green Deployments**: Use for zero-downtime deployments
2. **Canary Releases**: Deploy to subset of users first
3. **Regular Backups**: Automate database backups
4. **Monitoring Alerts**: Set up alerts for critical metrics
5. **Security Updates**: Regularly update base images and dependencies
6. **Resource Optimization**: Monitor and optimize resource usage
7. **Documentation**: Keep deployment documentation updated

## Contact and Support

For deployment issues, contact:
- DevOps Team: devops@your-organization.com
- Platform Team: platform@your-organization.com

Emergency contact: [Phone number for critical issues]