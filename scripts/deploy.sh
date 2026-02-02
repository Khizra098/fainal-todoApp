#!/bin/bash

# Deployment script for the Containerized Todo Application with AI Assistant

set -euo pipefail  # Exit on error, undefined vars, and pipe failures

# Default values
ENVIRONMENT="development"
NAMESPACE="todo-app"
DOCKER_REGISTRY=""
IMAGE_TAG="latest"
HELM_VALUES_FILE=""
SKIP_TESTS="false"
FORCE_DEPLOY="false"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Deploy the Containerized Todo Application"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Environment to deploy to (development|staging|production) [default: development]"
    echo "  -n, --namespace NS       Kubernetes namespace [default: todo-app]"
    echo "  -r, --registry REGISTRY  Docker registry URL"
    echo "  -t, --tag TAG           Image tag [default: latest]"
    echo "  -v, --values FILE       Helm values file"
    echo "  -s, --skip-tests        Skip pre-deployment tests"
    echo "  -f, --force             Force deployment even if tests fail"
    echo "  --dry-run               Dry run mode (don't actually deploy)"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --environment staging --registry myregistry.azurecr.io --tag v1.2.3"
    echo "  $0 -e production -v values-prod.yaml --skip-tests"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -r|--registry)
            DOCKER_REGISTRY="$2"
            shift 2
            ;;
        -t|--tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        -v|--values)
            HELM_VALUES_FILE="$2"
            shift 2
            ;;
        -s|--skip-tests)
            SKIP_TESTS="true"
            shift
            ;;
        -f|--force)
            FORCE_DEPLOY="true"
            shift
            ;;
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate environment
case $ENVIRONMENT in
    development|staging|production)
        ;;
    *)
        print_error "Invalid environment: $ENVIRONMENT. Must be development, staging, or production."
        exit 1
        ;;
esac

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."

    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install kubectl and configure access to your cluster."
        exit 1
    fi

    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        print_error "helm is not installed. Please install helm 3.x."
        exit 1
    fi

    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        print_warning "docker is not installed. Builds will be skipped."
    fi

    # Check kubectl connection
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster. Please configure kubectl."
        exit 1
    fi

    print_success "All prerequisites satisfied."
}

# Function to run pre-deployment tests
run_pre_deployment_tests() {
    if [ "$SKIP_TESTS" = "true" ]; then
        print_warning "Skipping pre-deployment tests as requested."
        return 0
    fi

    print_status "Running pre-deployment tests..."

    # Run unit tests
    if [ -d "backend" ]; then
        print_status "Running backend tests..."
        cd backend
        if command -v pytest &> /dev/null; then
            if ! pytest --cov=src --cov-report=term-missing; then
                print_error "Backend tests failed."
                if [ "$FORCE_DEPLOY" = "false" ]; then
                    exit 1
                else
                    print_warning "Proceeding with deployment despite test failures (forced)."
                fi
            else
                print_success "Backend tests passed."
            fi
        else
            print_warning "pytest not found, skipping backend tests."
        fi
        cd ..
    fi

    # Run any other tests
    print_success "Pre-deployment tests completed."
}

# Function to build and push Docker images
build_and_push_images() {
    if [ -z "$DOCKER_REGISTRY" ]; then
        print_warning "No registry specified, skipping image build and push."
        return 0
    fi

    if [ -z "$IMAGE_TAG" ]; then
        print_error "Image tag is required when pushing to registry."
        exit 1
    fi

    print_status "Building and pushing Docker images..."

    # Build and push backend image
    if [ -f "backend/Dockerfile" ]; then
        BACKEND_IMAGE="${DOCKER_REGISTRY}/todo-backend:${IMAGE_TAG}"
        print_status "Building backend image: $BACKEND_IMAGE"

        if [ "$DRY_RUN" != "true" ]; then
            docker build -t "$BACKEND_IMAGE" backend/
            docker push "$BACKEND_IMAGE"
            print_success "Backend image built and pushed: $BACKEND_IMAGE"
        else
            print_status "[DRY RUN] Would build and push backend image: $BACKEND_IMAGE"
        fi
    fi

    # Build and push frontend image
    if [ -f "frontend/Dockerfile" ]; then
        FRONTEND_IMAGE="${DOCKER_REGISTRY}/todo-frontend:${IMAGE_TAG}"
        print_status "Building frontend image: $FRONTEND_IMAGE"

        if [ "$DRY_RUN" != "true" ]; then
            docker build -t "$FRONTEND_IMAGE" frontend/
            docker push "$FRONTEND_IMAGE"
            print_success "Frontend image built and pushed: $FRONTEND_IMAGE"
        else
            print_status "[DRY RUN] Would build and push frontend image: $FRONTEND_IMAGE"
        fi
    fi

    print_success "Docker images built and pushed."
}

# Function to prepare deployment configuration
prepare_deployment_config() {
    print_status "Preparing deployment configuration..."

    # Create namespace if it doesn't exist
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        print_status "Creating namespace: $NAMESPACE"
        if [ "$DRY_RUN" != "true" ]; then
            kubectl create namespace "$NAMESPACE"
        else
            print_status "[DRY RUN] Would create namespace: $NAMESPACE"
        fi
    fi

    # Set up default values file if not provided
    if [ -z "$HELM_VALUES_FILE" ]; then
        case $ENVIRONMENT in
            production)
                HELM_VALUES_FILE="k8s/helm/values-prod.yaml"
                ;;
            staging)
                HELM_VALUES_FILE="k8s/helm/values-staging.yaml"
                ;;
            *)
                HELM_VALUES_FILE="k8s/helm/values-dev.yaml"
                ;;
        esac
    fi

    if [ ! -f "$HELM_VALUES_FILE" ]; then
        print_warning "Values file $HELM_VALUES_FILE not found. Using defaults."
        HELM_VALUES_FILE=""  # Empty means use Helm defaults
    else
        print_status "Using values file: $HELM_VALUES_FILE"
    fi

    print_success "Deployment configuration prepared."
}

# Function to deploy using Helm
deploy_with_helm() {
    print_status "Deploying application using Helm..."

    HELM_RELEASE_NAME="todo-${ENVIRONMENT}"

    # Set up Helm parameters
    HELM_PARAMS="--namespace $NAMESPACE --create-namespace --timeout 10m"

    if [ -n "$HELM_VALUES_FILE" ]; then
        HELM_PARAMS="$HELM_PARAMS --values $HELM_VALUES_FILE"
    fi

    if [ "$DRY_RUN" = "true" ]; then
        HELM_PARAMS="$HELM_PARAMS --dry-run"
    fi

    # Add image tags to parameters if specified
    if [ -n "$DOCKER_REGISTRY" ] && [ -n "$IMAGE_TAG" ]; then
        HELM_PARAMS="$HELM_PARAMS --set backend.image.repository=${DOCKER_REGISTRY}/todo-backend --set backend.image.tag=${IMAGE_TAG}"
        HELM_PARAMS="$HELM_PARAMS --set frontend.image.repository=${DOCKER_REGISTRY}/todo-frontend --set frontend.image.tag=${IMAGE_TAG}"
    fi

    # Install or upgrade the release
    if helm status "$HELM_RELEASE_NAME" --namespace "$NAMESPACE" &> /dev/null; then
        print_status "Upgrading existing release: $HELM_RELEASE_NAME"
        if [ "$DRY_RUN" != "true" ]; then
            helm upgrade "$HELM_RELEASE_NAME" k8s/helm/ $HELM_PARAMS
        else
            print_status "[DRY RUN] Would upgrade release: $HELM_RELEASE_NAME"
            echo "Command would be: helm upgrade $HELM_RELEASE_NAME k8s/helm/ $HELM_PARAMS"
        fi
    else
        print_status "Installing new release: $HELM_RELEASE_NAME"
        if [ "$DRY_RUN" != "true" ]; then
            helm install "$HELM_RELEASE_NAME" k8s/helm/ $HELM_PARAMS
        else
            print_status "[DRY RUN] Would install release: $HELM_RELEASE_NAME"
            echo "Command would be: helm install $HELM_RELEASE_NAME k8s/helm/ $HELM_PARAMS"
        fi
    fi

    print_success "Helm deployment completed."
}

# Function to verify deployment
verify_deployment() {
    print_status "Verifying deployment..."

    if [ "$DRY_RUN" = "true" ]; then
        print_status "[DRY RUN] Would verify deployment."
        return 0
    fi

    # Wait for deployments to be ready
    print_status "Waiting for deployments to be ready..."

    # Check backend deployment
    if kubectl get deployment backend-deployment --namespace "$NAMESPACE" &> /dev/null; then
        kubectl rollout status deployment/backend-deployment --namespace "$NAMESPACE" --timeout=5m
        print_success "Backend deployment is ready."
    else
        print_warning "Backend deployment not found in namespace $NAMESPACE"
    fi

    # Check frontend deployment
    if kubectl get deployment frontend-deployment --namespace "$NAMESPACE" &> /dev/null; then
        kubectl rollout status deployment/frontend-deployment --namespace "$NAMESPACE" --timeout=5m
        print_success "Frontend deployment is ready."
    else
        print_warning "Frontend deployment not found in namespace $NAMESPACE"
    fi

    # Check services
    print_status "Checking services..."
    kubectl get svc --namespace "$NAMESPACE"

    # Check pods
    print_status "Checking pods..."
    kubectl get pods --namespace "$NAMESPACE"

    print_success "Deployment verification completed."
}

# Function to run post-deployment tests
run_post_deployment_tests() {
    if [ "$DRY_RUN" = "true" ]; then
        print_status "[DRY RUN] Would run post-deployment tests."
        return 0
    fi

    print_status "Running post-deployment tests..."

    # Run health checks
    print_status "Checking application health..."

    # Get the service external IP or use port forwarding for testing
    if kubectl get service frontend-service --namespace "$NAMESPACE" &> /dev/null; then
        print_status "Frontend service is available."
    fi

    if kubectl get service backend-service --namespace "$NAMESPACE" &> /dev/null; then
        print_status "Backend service is available."

        # Try to access health endpoint if possible
        POD_NAME=$(kubectl get pods --namespace "$NAMESPACE" -l app=backend -o jsonpath="{.items[0].metadata.name}" 2>/dev/null || echo "")
        if [ -n "$POD_NAME" ]; then
            print_status "Testing backend health endpoint..."
            kubectl port-forward --namespace "$NAMESPACE" "pod/$POD_NAME" 8000:8000 &
            PORT_FORWARD_PID=$!

            # Give port forward time to start
            sleep 5

            # Test health endpoint
            if curl -f http://localhost:8000/health/health &> /dev/null; then
                print_success "Backend health check passed."
            else
                print_warning "Backend health check failed or endpoint not accessible."
            fi

            # Kill port forward
            kill $PORT_FORWARD_PID 2>/dev/null || true
        fi
    fi

    print_success "Post-deployment tests completed."
}

# Main deployment process
main() {
    print_status "Starting deployment to $ENVIRONMENT environment in namespace $NAMESPACE..."

    check_prerequisites
    run_pre_deployment_tests
    build_and_push_images
    prepare_deployment_config
    deploy_with_helm
    verify_deployment
    run_post_deployment_tests

    print_success "Deployment to $ENVIRONMENT completed successfully!"
    echo ""
    print_status "Next steps:"
    echo "  - Check application status: kubectl get all -n $NAMESPACE"
    echo "  - View application logs: kubectl logs -l app=backend -n $NAMESPACE"
    echo "  - Access application: kubectl get ingress -n $NAMESPACE"
}

# Run the main function
main "$@"