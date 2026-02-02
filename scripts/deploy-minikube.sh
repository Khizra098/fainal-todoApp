#!/bin/bash

# Script to deploy the application to Minikube
# Usage: ./deploy-minikube.sh [env: dev|staging|prod]

ENV="${1:-dev}"

echo "Starting deployment to Minikube for environment: $ENV"

# Check if minikube is running
MINIKUBE_STATUS=$(minikube status --format='{{.Host}}')
if [ "$MINIKUBE_STATUS" != "Running" ]; then
    echo "Minikube is not running. Starting minikube..."
    minikube start
    if [ $? -ne 0 ]; then
        echo "Error: Failed to start minikube"
        exit 1
    fi
fi

# Enable ingress addon if not already enabled
minikube addons enable ingress
if [ $? -ne 0 ]; then
    echo "Warning: Could not enable ingress addon"
fi

# Set Docker environment to use minikube
eval $(minikube docker-env)

# Build Docker images
echo "Building Docker images for $ENV environment..."

echo "Building backend image..."
docker build -t todo-backend:$ENV -f docker/backend/Dockerfile .

if [ $? -ne 0 ]; then
    echo "Error: Failed to build backend image"
    exit 1
fi

echo "Building frontend image..."
docker build -t todo-frontend:$ENV -f docker/frontend/Dockerfile .

if [ $? -ne 0 ]; then
    echo "Error: Failed to build frontend image"
    exit 1
fi

# Create namespace if it doesn't exist
NAMESPACE="todo-app-$ENV"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Deploy using Kustomize
case $ENV in
    "dev")
        kubectl kustomize k8s/overlays/development | kubectl apply -f -
        ;;
    "staging")
        kubectl kustomize k8s/overlays/staging | kubectl apply -f -
        ;;
    "prod"|"production")
        kubectl kustomize k8s/overlays/production | kubectl apply -f -
        ;;
    *)
        echo "Invalid environment: $ENV. Use dev, staging, or prod"
        exit 1
        ;;
esac

if [ $? -ne 0 ]; then
    echo "Error: Failed to deploy application to $ENV environment"
    exit 1
fi

# Wait for deployments to be ready
echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=ready pod -l app=postgresql -n $NAMESPACE --timeout=120s
kubectl wait --for=condition=ready pod -l app=backend -n $NAMESPACE --timeout=120s
kubectl wait --for=condition=ready pod -l app=frontend -n $NAMESPACE --timeout=120s

if [ $? -ne 0 ]; then
    echo "Warning: Some pods are not ready after timeout"
fi

# Get the ingress IP and show deployment status
INGRESS_IP=$(minikube ip)
echo ""
echo "Deployment completed successfully!"
echo "Minikube IP: $INGRESS_IP"
echo "Application namespace: $NAMESPACE"
echo ""
echo "Services:"
kubectl get svc -n $NAMESPACE
echo ""
echo "Deployments:"
kubectl get deployments -n $NAMESPACE
echo ""
echo "Pods:"
kubectl get pods -n $NAMESPACE
echo ""

echo "Application should be accessible via the ingress configuration."
echo "Check: kubectl get ingress -n $NAMESPACE for exact URLs"