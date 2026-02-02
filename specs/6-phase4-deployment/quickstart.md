# Quickstart Guide: Phase 4 Deployment

## Prerequisites

- Docker and Docker Compose
- Kubernetes cluster (Minikube for local development)
- kubectl command-line tool
- GitHub account for CI/CD setup
- Access to container registry (Docker Hub, GitHub Container Registry, etc.)

## Local Development Setup

### 1. Start Minikube
```bash
minikube start
minikube addons enable ingress
```

### 2. Clone and Navigate to Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 3. Build and Deploy to Minikube
```bash
# Build Docker images
docker build -t todo-frontend:latest -f docker/frontend/Dockerfile .
docker build -t todo-backend:latest -f docker/backend/Dockerfile .
docker build -t todo-database:latest -f docker/database/Dockerfile .

# Tag and push images to local registry (if needed)
eval $(minikube docker-env)
docker tag todo-frontend:latest minikube/todo-frontend:latest
docker tag todo-backend:latest minikube/todo-backend:latest
docker tag todo-database:latest minikube/todo-database:latest

# Apply Kubernetes manifests
kubectl apply -k k8s/overlays/development/
```

### 4. Verify Deployment
```bash
# Check if all pods are running
kubectl get pods -n todo-app-dev

# Check services
kubectl get services -n todo-app-dev

# Access the application
minikube service frontend-service -n todo-app-dev --url
```

## Production Deployment

### 1. Configure Secrets
```bash
# Create secrets for database credentials
kubectl create secret generic postgres-secret \
  --from-literal=password=<password> \
  --namespace todo-app-prod

# Create secrets for API keys and other sensitive data
kubectl create secret generic app-config \
  --from-literal=OPENAI_API_KEY=<api-key> \
  --namespace todo-app-prod
```

### 2. Deploy to Production
```bash
# Apply production manifests
kubectl apply -k k8s/overlays/production/
```

### 3. Set Up CI/CD Pipeline
1. Create GitHub repository with the code
2. Configure secrets in GitHub repository:
   - `DOCKER_USERNAME`: Container registry username
   - `DOCKER_PASSWORD`: Container registry password/token
   - `KUBE_CONFIG_DATA`: Base64-encoded kubeconfig file
3. Workflows will automatically trigger on code changes

## Key Commands

### Container Operations
```bash
# Build all containers
make build-all

# Build specific container
make build-frontend
make build-backend
make build-database
```

### Kubernetes Operations
```bash
# Deploy to development
make deploy-dev

# Deploy to staging
make deploy-staging

# Deploy to production
make deploy-prod

# Check deployment status
make status

# View logs
make logs
```

### Verification Commands
```bash
# Check all resources
kubectl get all -n todo-app-dev

# Check ingress
kubectl get ingress -n todo-app-dev

# Check health of deployments
kubectl rollout status deployment/frontend-deployment -n todo-app-dev
kubectl rollout status deployment/backend-deployment -n todo-app-dev
```

## Troubleshooting

### Common Issues
1. **Images not found**: Ensure images are built and pushed to the registry
2. **Secrets missing**: Verify all required secrets are created in the target namespace
3. **Ingress not working**: Check if ingress controller is running and configured properly
4. **Database connection issues**: Verify database is running and credentials are correct

### Useful Commands
```bash
# Describe a pod to see detailed status
kubectl describe pod <pod-name> -n <namespace>

# View logs for a specific pod
kubectl logs <pod-name> -n <namespace>

# Exec into a container for debugging
kubectl exec -it <pod-name> -n <namespace> -- /bin/sh
```