import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ai.video_processor import session_manager

logger = logging.getLogger("websocket")
router = APIRouter(tags=["WebSocket"])

@router.websocket("/ws/monitor/{session_id}")
async def monitor_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()
    logger.info(f"WebSocket client connected for session {session_id}")

    processor = session_manager.get_processor(session_id)
    queue: asyncio.Queue = asyncio.Queue(maxsize=100)

    if processor:
        processor.register_telemetry_listener(queue)

    async def sender_task():
        """Reads messages from the queue and sends them over WebSocket."""
        try:
            while True:
                # If processor wasn't ready at connect, attempt lookup
                nonlocal processor
                if not processor:
                    processor = session_manager.get_processor(session_id)
                    if processor:
                        processor.register_telemetry_listener(queue)
                    await asyncio.sleep(0.5)
                    continue

                msg = await queue.get()
                await websocket.send_text(json.dumps(msg))
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.debug(f"Sender task error/close: {e}")

    async def receiver_task():
        """Handles incoming messages from the frontend."""
        try:
            while True:
                data_text = await websocket.receive_text()
                try:
                    data = json.loads(data_text)
                    action = data.get("action")
                    if action == "pause" and processor:
                        processor.pause()
                    elif action == "resume" and processor:
                        processor.resume()
                    elif action == "stop" and processor:
                        processor.stop()
                    elif action == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                except Exception as e:
                    logger.error(f"Error handling incoming ws message: {e}")
        except WebSocketDisconnect:
            logger.info(f"WebSocket client disconnected from session {session_id}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.debug(f"Receiver task error/close: {e}")

    sender = asyncio.create_task(sender_task())
    receiver = asyncio.create_task(receiver_task())

    try:
        # Wait until either sender or receiver terminates
        done, pending = await asyncio.wait(
            [sender, receiver],
            return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()
    finally:
        if processor:
            processor.unregister_telemetry_listener(queue)
        logger.info(f"Cleaned up WebSocket connection for session {session_id}")
