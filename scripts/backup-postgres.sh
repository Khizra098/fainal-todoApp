#!/bin/bash

# Script to backup PostgreSQL database in Kubernetes
# Usage: ./backup-postgres.sh [namespace] [deployment-name]

NAMESPACE="${1:-todo-app-prod}"
DEPLOYMENT_NAME="${2:-postgresql-deployment}"
BACKUP_DIR="/tmp/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="postgresql_backup_$DATE.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

echo "Starting PostgreSQL backup for deployment: $DEPLOYMENT_NAME in namespace: $NAMESPACE"

# Get the pod name for the PostgreSQL deployment
POD_NAME=$(kubectl get pods -n $NAMESPACE -l app=postgresql -o jsonpath='{.items[0].metadata.name}')

if [ -z "$POD_NAME" ]; then
    echo "Error: Could not find PostgreSQL pod in namespace $NAMESPACE"
    exit 1
fi

echo "Found PostgreSQL pod: $POD_NAME"

# Execute pg_dump inside the pod with correct user
kubectl exec -n $NAMESPACE $POD_NAME -- pg_dump -U todo_user -d todo_app > $BACKUP_DIR/$BACKUP_NAME

if [ $? -eq 0 ]; then
    echo "Backup completed successfully: $BACKUP_DIR/$BACKUP_NAME"
    echo "Backup size: $(du -h $BACKUP_DIR/$BACKUP_NAME | cut -f1)"
else
    echo "Error: Backup failed"
    exit 1
fi

# Optional: Compress the backup
gzip $BACKUP_DIR/$BACKUP_NAME
echo "Backup compressed: $BACKUP_DIR/${BACKUP_NAME}.gz"

echo "Backup process completed."