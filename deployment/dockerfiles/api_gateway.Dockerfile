# Image khusus API Gateway
FROM ghcr.io/ml-agents/base:latest

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start Uvicorn
CMD ["uvicorn", "api.gateway:app", "--host", "0.0.0.0", "--port", "8000"]
