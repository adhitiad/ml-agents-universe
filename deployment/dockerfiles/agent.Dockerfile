# Image dinamis untuk Agent Workers
FROM ghcr.io/ml-agents/base:latest

# Nama domain yang di-inject saat build (misal: nlp, finance, dll)
ARG DOMAIN_NAME
ENV AGENT_DOMAIN=$DOMAIN_NAME

EXPOSE 8000

# Karena worker bisa bertindak terisolasi (misal event-driven atau grpc)
# Di simulasi ini kita jalankan mereka dummy idle atau uvicorn spesifik modul
CMD ["python", "-c", "import time; print(f'Agent {os.environ.get(\"AGENT_DOMAIN\")} started'); time.sleep(99999)"]
