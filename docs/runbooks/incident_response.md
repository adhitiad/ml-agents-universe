# Incident Response Runbook

## 1. HighErrorRateAlert
**Gejala**: Agen spesifik membuang banyak *HTTP 500* atau kegagalan *parsing*.
**Aksi**:
1. Cek logs Elasticsearch/Kibana dengan `correlation_id`.
2. Periksa apakah LLM provider sedang *down* (rate limit tercapai).
3. Matikan / matikan agen via *Circuit Breaker* jika eksternal API terganggu.

## 2. HighLatencyAlert
**Gejala**: Endpoint `/predict` mengambil waktu > 2 detik (p95).
**Aksi**:
1. Cek beban memori `system_memory_usage_bytes`.
2. Jika HPA (Horizontal Pod Autoscaler) tidak bekerja, tingkatkan replika secara manual: `kubectl scale deployment <agent> --replicas=3`.

## 3. DataQualityAlert
**Gejala**: Peringatan dari *data pipeline*.
**Aksi**:
1. Periksa `data/schemas/` apabila skema berubah dan *scraper* tidak relevan.
2. Evaluasi aturan regex pada PII masking atau parsing teks.
