#!/bin/bash
set -e

NAMESPACE=${1:-"production"}
RELEASE_NAME=${2:-"ml-agents-universe"}
TAG=${3:-"latest"}

echo "Deploying $RELEASE_NAME to namespace $NAMESPACE with tag $TAG..."

helm upgrade --install $RELEASE_NAME ./deployment/helm/ml-agents-universe \
  --namespace $NAMESPACE \
  --create-namespace \
  --set gateway.tag=$TAG \
  --set agents.tag=$TAG \
  --wait \
  --timeout 5m

echo "Deployment completed successfully!"
