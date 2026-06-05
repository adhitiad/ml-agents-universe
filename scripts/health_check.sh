#!/bin/bash
set -e

NAMESPACE=${1:-"production"}
URL=${2:-"http://api.ml-agents.local/health"}

echo "Verifying health of Gateway at $URL in $NAMESPACE..."

MAX_RETRIES=10
RETRY_COUNT=0
HEALTHY=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    HTTP_STATUS=$(curl -o /dev/null -s -w "%{http_code}\n" $URL || true)
    if [ "$HTTP_STATUS" == "200" ]; then
        HEALTHY=true
        break
    fi
    echo "Attempt $((RETRY_COUNT+1)): Gateway not ready (Status: $HTTP_STATUS). Retrying in 10s..."
    sleep 10
    RETRY_COUNT=$((RETRY_COUNT+1))
done

if [ "$HEALTHY" = true ]; then
    echo "Health check passed!"
    exit 0
else
    echo "Health check failed after $MAX_RETRIES attempts."
    exit 1
fi
