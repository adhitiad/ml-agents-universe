"""OpenTelemetry Tracing Wrapper."""

# Di skenario nyata, bagian ini akan menginisiasi provider OpenTelemetry:
# from opentelemetry import trace
# from opentelemetry.sdk.trace import TracerProvider
# dll.


class DistributedTracer:
    """Wrapper ringan untuk mengelola Span dan Trace."""

    @staticmethod
    def start_span(name: str, attributes: dict | None = None):
        """Memulai jejak pelacakan (Mock OpenTelemetry Span)."""

        # mock implementation
        class MockSpan:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

            def set_attribute(self, key, value):
                pass

        return MockSpan()
