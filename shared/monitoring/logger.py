"""Structured JSON Logger dengan PII Masking."""

import json
import logging
import re
from contextvars import ContextVar
from datetime import datetime


# Menyimpan Trace/Correlation ID untuk request saat ini
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="SYSTEM")

# Simple Regex Masking untuk PII (Email & Telp)
PII_PATTERNS = [
    (re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"), "***@***.***"),
    (re.compile(r"\b\d{10,12}\b"), "XXX-XXXX-XXXX"),
]


class StructuredJsonFormatter(logging.Formatter):
    """Format logs into JSON."""

    def format(self, record):
        message = record.getMessage()
        # Scrub PII
        for pattern, mask in PII_PATTERNS:
            message = pattern.sub(mask, message)

        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "correlation_id": correlation_id_var.get(),
            "logger_name": record.name,
            "message": message,
        }
        # Tambahkan extra fields jika ada
        if hasattr(record, "extra_info"):
            log_obj["extra_info"] = record.extra_info

        return json.dumps(log_obj)


def get_logger(name: str) -> logging.Logger:
    """Mengembalikan logger yang terkonfigurasi untuk output JSON."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredJsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
