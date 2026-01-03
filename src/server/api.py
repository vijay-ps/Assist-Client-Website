import os
import secrets
import logging
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WebServer")

app = FastAPI()

# Store connected clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

# State
PAIRING_CODE = None
AUTH_TOKENS = set()

class PairingRequest(BaseModel):
    code: str

def set_pairing_code(code: str):
    global PAIRING_CODE
    PAIRING_CODE = code
    logger.info(f"Pairing code set to: {code}")

@app.post("/verify")
async def verify_code(request: PairingRequest):
    if not PAIRING_CODE:
        raise HTTPException(status_code=500, detail="Server not ready")
    
    if request.code == PAIRING_CODE:
        token = secrets.token_hex(16)
        AUTH_TOKENS.add(token)
        return {"valid": True, "token": token}
    else:
        return {"valid": False}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    if token not in AUTH_TOKENS:
        await websocket.close(code=4003) # Forbidden
        return

    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, maybe handle ping/pong
            data = await websocket.receive_text()
            # We don't expect messages from client, but just in case
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Serve static files
# We assume the 'client' folder is in the project root
CLIENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "client"))

if os.path.exists(CLIENT_DIR):
    app.mount("/", StaticFiles(directory=CLIENT_DIR, html=True), name="client")
else:
    logger.error(f"Client directory not found at {CLIENT_DIR}")

    await manager.broadcast(message)

# Thread-safe communication
import asyncio
SERVER_LOOP = None

@app.on_event("startup")
async def startup_event():
    global SERVER_LOOP
    SERVER_LOOP = asyncio.get_running_loop()
    logger.info("Server loop captured.")

def send_message_sync(text: str, timestamp: str):
    """
    Thread-safe wrapper to call broadcast_response from a different thread.
    """
    global SERVER_LOOP
    if SERVER_LOOP and SERVER_LOOP.is_running():
        asyncio.run_coroutine_threadsafe(broadcast_response(text, timestamp), SERVER_LOOP)
    else:
        logger.warning("Server loop not running, cannot broadcast message.")

