"""Prometheus Metrics Collector."""

from prometheus_client import Counter, Gauge, Histogram


# --- Agent Metrics ---
inference_latency = Histogram(
    "inference_latency_seconds", "Latency of agent inference", ["domain"]
)
request_count = Counter(
    "request_count_total", "Total requests received by agent", ["domain", "status"]
)
error_rate = Counter(
    "error_rate_total", "Total errors encountered", ["domain", "error_type"]
)
token_usage = Counter("token_usage_total", "Total LLM tokens consumed", ["domain"])
tool_call_count = Counter(
    "tool_call_count_total", "Total tool calls executed", ["domain", "tool_name"]
)

# --- Data Metrics ---
pipeline_duration = Histogram(
    "pipeline_duration_seconds",
    "Time taken for data pipeline execution",
    ["domain", "stage"],
)
data_quality_score = Gauge(
    "data_quality_score", "Data quality score from 0.0 to 1.0", ["domain"]
)

# --- System Metrics ---
system_memory_usage = Gauge(
    "system_memory_usage_bytes", "Current memory usage of the process"
)
active_connections = Gauge(
    "active_connections_total",
    "Number of active WebSocket or HTTP streaming connections",
)


class MetricsCollector:
    """Wrapper untuk mempermudah pencatatan metrics."""

    @staticmethod
    def record_request(domain: str, status: str = "success"):
        request_count.labels(domain=domain, status=status).inc()

    @staticmethod
    def record_error(domain: str, error_type: str):
        error_rate.labels(domain=domain, error_type=error_type).inc()
