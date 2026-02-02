#!/bin/bash

# Script to restore PostgreSQL database in Kubernetes
# Usage: ./restore-postgres.sh [backup-file] [namespace] [deployment-name]

BACKUP_FILE="$1"
NAMESPACE="${2:-todo-app-prod}"
DEPLOYMENT_NAME="${3:-postgresql-deployment}"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup-file> [namespace] [deployment-name]"
    echo "Example: $0 /path/to/backup.sql todo-app-prod postgresql-deployment"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file $BACKUP_FILE does not exist"
    exit 1
fi

echo "Starting PostgreSQL restore from: $BACKUP_FILE to namespace: $NAMESPACE"

# Get the pod name for the PostgreSQL deployment
POD_NAME=$(kubectl get pods -n $NAMESPACE -l app=postgresql -o jsonpath='{.items[0].metadata.name}')

if [ -z "$POD_NAME" ]; then
    echo "Error: Could not find PostgreSQL pod in namespace $NAMESPACE"
    exit 1
fi

echo "Found PostgreSQL pod: $POD_NAME"

# Check if the backup file is compressed
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo "Decompressing backup file..."
    gunzip -c "$BACKUP_FILE" | kubectl exec -n $NAMESPACE $POD_NAME -i -- psql -U todo_user -d todo_app
else
    # Restore the database from the backup file
    cat "$BACKUP_FILE" | kubectl exec -n $NAMESPACE $POD_NAME -i -- psql -U todo_user -d todo_app
fi

if [ $? -eq 0 ]; then
    echo "Restore completed successfully"
else
    echo "Error: Restore failed"
    exit 1
fi

echo "Restore process completed."