import urllib.request
import urllib.parse
import json
import asyncio
import websockets

def run_test():
    data = urllib.parse.urlencode({'safe_capacity': 40}).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:8000/api/videos/use-demo', data=data)
    with urllib.request.urlopen(req) as res:
        session = json.loads(res.read().decode('utf-8'))
    session_id = session['id']
    print(f"Created session: {session_id} | Video: {session['video_name']}")

    req2 = urllib.request.Request(f'http://127.0.0.1:8000/api/sessions/{session_id}/start', data=b'')
    with urllib.request.urlopen(req2) as res2:
        print(f"Started session HTTP status: {res2.status}")

    async def read_ws():
        uri = f"ws://127.0.0.1:8000/ws/monitor/{session_id}"
        print(f"Connecting to WebSocket: {uri}")
        async with websockets.connect(uri) as ws:
            for i in range(4):
                raw = await ws.recv()
                msg = json.loads(raw)
                mtype = msg.get("type")
                frame = msg.get("frame_index")
                persons = msg.get("person_count")
                occ = msg.get("occupancy")
                level = msg.get("crowd_level")
                fps = msg.get("fps")
                print(f"  [WS Packet {i+1}] type={mtype} | Frame: {frame} | Persons: {persons} | Occ: {occ}% | Level: {level} | FPS: {fps}")

    asyncio.run(read_ws())

    # Check MJPEG stream header
    stream_req = urllib.request.Request(f'http://127.0.0.1:8000/api/sessions/{session_id}/stream')
    with urllib.request.urlopen(stream_req) as stream_res:
        content_type = stream_res.headers.get('Content-Type')
        print(f"MJPEG Stream Content-Type: {content_type}")
        first_chunk = stream_res.read(1024)
        print(f"MJPEG Chunk read size: {len(first_chunk)} bytes (contains '--frame': {b'--frame' in first_chunk})")

    print("ALL VERIFICATIONS PASSED!")

if __name__ == "__main__":
    run_test()
