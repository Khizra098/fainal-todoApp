# Containerized Todo Application with AI Assistant

This is a comprehensive containerized Todo application featuring AI-powered assistance, verification capabilities, and production-ready deployment configuration.

## Features

- **AI-Powered Assistant**: Integrated AI assistant to help users manage tasks and provide guidance
- **Feature Verification**: Built-in system to verify features against original specifications
- **Issue Tracking**: Comprehensive issue tracking and management system
- **Performance Monitoring**: Built-in performance benchmarking and monitoring
- **Security Scanning**: Automated security assessment and vulnerability scanning
- **Deployment Configuration**: Flexible deployment configuration management
- **Full CRUD Operations**: Complete task management capabilities

## Architecture

The application follows a microservices architecture with:

- **Frontend**: Next.js application for user interface
- **Backend**: FastAPI application for business logic and API endpoints
- **Database**: PostgreSQL for data persistence
- **AI Integration**: OpenAI integration with MCP tools for AI assistant functionality
- **Containerization**: Docker containers for all services
- **Orchestration**: Kubernetes for deployment and scaling

## Prerequisites

- Docker and Docker Compose
- Kubernetes cluster (Minikube for local development)
- kubectl command-line tool
- Python 3.11+
- Node.js 18+

## Local Development Setup

### Using Docker Compose (Development)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Create a `.env` file in the backend directory with:
   ```env
   DATABASE_URL=postgresql://todo_user:password@localhost:5432/todo_app
   OPENAI_API_KEY=your_openai_api_key_here
   SECRET_KEY=your_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

3. Start the services:
   ```bash
   docker-compose up --build
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

### Using Minikube (Kubernetes Development)

1. Start Minikube:
   ```bash
   minikube start
   minikube addons enable ingress
   ```

2. Deploy to Minikube:
   ```bash
   chmod +x scripts/deploy-minikube.sh
   ./scripts/deploy-minikube.sh dev
   ```

3. Access the application via Minikube:
   ```bash
   minikube tunnel  # In a separate terminal
   ```

   The application will be accessible through the ingress configuration.

## API Endpoints

### Verification Endpoints
- `GET /api/v1/verification/features` - Retrieve all features with verification status
- `GET /api/v1/verification/features/{feature_id}` - Get detailed verification information for a specific feature
- `POST /api/v1/verification/features/{feature_id}/verify` - Initiate verification process for a specific feature

### Issue Tracking Endpoints
- `GET /api/v1/issues` - Retrieve list of issues with filtering options
- `POST /api/v1/issues` - Create a new issue
- `PUT /api/v1/issues/{issue_id}` - Update an existing issue
- `GET /api/v1/issues/{issue_id}` - Get detailed information for a specific issue

### Performance Endpoints
- `GET /api/v1/performance/benchmarks` - Retrieve performance benchmark results
- `GET /api/v1/performance/current-metrics` - Get current system performance metrics
- `POST /api/v1/performance/run-benchmark/{test_name}` - Run a performance benchmark test

### Security Endpoints
- `GET /api/v1/security/scans` - Retrieve security scan results
- `POST /api/v1/security/scans/run` - Run a security scan
- `GET /api/v1/security/vulnerability-summary` - Get vulnerability summary

### Deployment Configuration Endpoints
- `GET /api/v1/deployment/config` - Retrieve current deployment configuration
- `PUT /api/v1/deployment/config` - Update deployment configuration
- `GET /api/v1/deployment/environments` - Get available deployment environments

### Health Check Endpoints
- `GET /health/health` - Basic health check
- `GET /health/ready` - Readiness check
- `GET /health/live` - Liveness check

## Environment Variables

### Backend
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for AI functionality
- `SECRET_KEY`: Secret key for JWT tokens
- `ALGORITHM`: Algorithm for JWT tokens (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)
- `ENVIRONMENT`: Environment type (development/staging/production)
- `LOG_LEVEL`: Logging level (default: INFO)

### Frontend
- `NEXT_PUBLIC_API_URL`: Backend API URL

## Testing

### Backend Tests
Run the backend tests:
```bash
cd backend
pytest
```

To run tests with coverage:
```bash
cd backend
pytest --cov=src --cov-report=html
```

### Frontend Tests
Run the frontend tests:
```bash
cd frontend
npm test
```

## Production Deployment

### Kubernetes Deployment

1. Set up your Kubernetes cluster with the required namespaces:
   ```bash
   kubectl apply -f k8s/base/namespace.yaml
   ```

2. Deploy secrets (update with your actual secrets):
   ```bash
   kubectl apply -f k8s/base/postgresql/secrets.yaml -n todo-app-prod
   kubectl apply -f k8s/base/backend/secrets.yaml -n todo-app-prod
   ```

3. Deploy using Kustomize:
   ```bash
   kubectl kustomize k8s/overlays/production | kubectl apply -f -
   ```

### Helm Deployment

1. Add the required secrets to your values file or create them separately:
   ```bash
   kubectl create secret generic postgres-secret --from-literal=password=your_password -n todo-app-prod
   ```

2. Install the Helm chart:
   ```bash
   helm install todo-app k8s/helm/ -f k8s/helm/values.yaml
   ```

## Security Best Practices

1. **Secrets Management**: All sensitive information is stored in Kubernetes Secrets
2. **Network Policies**: Traffic between services is restricted to necessary communications
3. **Resource Limits**: CPU and memory limits prevent resource exhaustion
4. **Health Checks**: Liveness and readiness probes ensure service availability
5. **Multi-stage Builds**: Docker images are optimized and minimize attack surface
6. **Rate Limiting**: API endpoints have rate limiting to prevent abuse
7. **Authentication**: JWT-based authentication for all protected endpoints
8. **Input Validation**: Comprehensive input validation and sanitization

## Monitoring and Observability

The deployment includes:
- Health check endpoints for Kubernetes probes
- Proper logging configuration with structured JSON logs
- Resource limits and requests for monitoring resource usage
- Horizontal Pod Autoscaling for backend services
- Centralized logging and monitoring capabilities

## Troubleshooting

### Common Issues
- **Services not starting**: Check logs with `kubectl logs <pod-name> -n <namespace>`
- **Database connection issues**: Verify secrets and database deployment status
- **Ingress not working**: Ensure ingress controller is running and configured
- **Image pull errors**: Verify image tags and registry access
- **AI assistant not responding**: Check OpenAI API key and network connectivity

### Useful Commands
```bash
# Check all resources in the namespace
kubectl get all -n todo-app-prod

# Check ingress status
kubectl get ingress -n todo-app-prod

# Check deployment rollout status
kubectl rollout status deployment/backend-deployment -n todo-app-prod

# Get detailed pod information
kubectl describe pod <pod-name> -n <namespace>

# Check application logs
kubectl logs deployment/backend-deployment -n todo-app-prod
```

## Development Guidelines

1. Always use the feature branch workflow
2. Update the Docker images when making code changes
3. Test changes in development environment before promoting to staging/production
4. Update the Helm chart values when changing configurations
5. Follow the Twelve-Factor App methodology for configuration management
6. Write comprehensive tests for all new functionality
7. Follow security best practices for all code changes

## License

This project is licensed under the MIT License - see the LICENSE file for details.