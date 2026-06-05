"""Skrip Asynchronous Load Testing (Pengganti Locust untuk testing lokal)."""

import asyncio
import time

import httpx


# Target API gateway
BASE_URL = "http://127.0.0.1:8000"
HEADERS = {"X-API-Key": "dev_universe_key"}
TOTAL_REQUESTS = 200
CONCURRENCY = 20

async def fetch(client: httpx.AsyncClient, endpoint: str):
    start = time.time()
    try:
        res = await client.get(f"{BASE_URL}{endpoint}", headers=HEADERS)
        status = res.status_code
    except Exception:
        status = 500
    latency = time.time() - start
    return status, latency

async def worker(queue: asyncio.Queue, results: list):
    async with httpx.AsyncClient() as client:
        while True:
            endpoint = await queue.get()
            status, latency = await fetch(client, endpoint)
            results.append((status, latency))
            queue.task_done()

async def main():
    print(f"Memulai Load Test: {TOTAL_REQUESTS} requests, {CONCURRENCY} concurrency.")
    queue = asyncio.Queue()
    results = []

    # Isi queue dengan target
    for _ in range(TOTAL_REQUESTS):
        # Asumsikan endpoint /health tidak di-rate-limit ketat, atau kita bisa tes /health
        queue.put_nowait("/health")

    workers = [asyncio.create_task(worker(queue, results)) for _ in range(CONCURRENCY)]

    start_time = time.time()
    await queue.join()

    for w in workers:
        w.cancel()

    total_time = time.time() - start_time

    # Statistik
    latencies = sorted([r[1] for r in results])
    successes = sum(1 for r in results if r[0] == 200)

    print("\n--- Hasil Load Test ---")
    print(f"Total Time: {total_time:.2f} s")
    print(f"RPS: {TOTAL_REQUESTS / total_time:.2f} req/s")
    print(f"Success Rate: {(successes / TOTAL_REQUESTS) * 100:.1f}%")
    if latencies:
        print(f"P50 Latency: {latencies[int(len(latencies)*0.5)]*1000:.2f} ms")
        print(f"P95 Latency: {latencies[int(len(latencies)*0.95)]*1000:.2f} ms")

if __name__ == "__main__":
    # Karena kita belum punya server Uvicorn yang berjalan dalam test env ini,
    # skrip ini dirancang untuk dijalankan saat API live.
    print("Load tester script ready. (Jalankan Uvicorn terlebih dahulu sebelum eksekusi)")
    asyncio.run(main())
