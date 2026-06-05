#!/bin/bash
set -e

NAMESPACE=${1:-"production"}
RELEASE_NAME=${2:-"ml-agents-universe"}
REVISION=${3:-""}

if [ -z "$REVISION" ]; then
    echo "Rolling back to previous revision..."
    helm rollback $RELEASE_NAME --namespace $NAMESPACE --wait
else
    echo "Rolling back to revision $REVISION..."
    helm rollback $RELEASE_NAME $REVISION --namespace $NAMESPACE --wait
fi

echo "Rollback successful!"
