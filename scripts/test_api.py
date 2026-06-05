import asyncio
import json
import urllib.request

import websockets


def test_rest():
    print("--- TESTING REST API ---")
    url = 'http://127.0.0.1:8080/v1/chat'
    data = json.dumps({'query': 'Sebutkan 1 tokoh ekonomi'}).encode('utf-8')
    headers = {'Content-Type': 'application/json', 'X-API-Key': 'master_key_123'}
    req = urllib.request.Request(url, data=data, headers=headers)

    try:
        res = urllib.request.urlopen(req)
        body = res.read().decode('utf-8')
        print(f"Status: {res.status}")
        print("Response:", body)
    except Exception as e:
        print(f"Error: {e}")

async def test_ws():
    print("\n--- TESTING WEBSOCKET ---")
    uri = "ws://127.0.0.1:8080/ws/v1/chat"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({"query": "Berapa 5 ditambah 5?"}))

        while True:
            try:
                response = await websocket.recv()
                data = json.loads(response)
                if 'status' not in data:
                    print("RAW WS Update:", data)
                    continue

                print(f"WS Update: {data['status'].upper()} -> {data.get('message', '')}")
                if data['status'] == 'done':
                    print("FINAL WS RESPONSE:", data.get('response'))
                    break
            except websockets.ConnectionClosed:
                print("Koneksi tertutup.")
                break

if __name__ == "__main__":
    asyncio.run(test_ws())
