from datetime import datetime, timezone
from typing import Literal
import asyncio, random, os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="SMARTCASE API", version="1.0.0", description="IoT smart luggage backend")
ALLOWED_ORIGINS = [x.strip() for x in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

# Demo mode is enabled by default. Set DEMO_MODE=false and DEVICE_API_KEY in production.
DEMO_MODE = True
DEVICE_API_KEY = "change-this-device-key"
state = {
    "device_id": "SC-001", "online": True, "mode": "demo", "battery": 86,
    "latitude": 31.3260, "longitude": 75.5762, "speed": 0.0,
    "motion": "Stationary", "last_seen": datetime.now(timezone.utc).isoformat(),
    "gps_fix": True, "rssi": -54, "motor": "stopped"
}
inventory = [
    {"id": "RFID-A102", "name": "Laptop sleeve", "tag": "A102", "present": True, "category": "Electronics", "last_seen": datetime.now(timezone.utc).isoformat()},
    {"id": "RFID-B204", "name": "Travel pouch", "tag": "B204", "present": True, "category": "Accessories", "last_seen": datetime.now(timezone.utc).isoformat()},
    {"id": "RFID-C309", "name": "Camera case", "tag": "C309", "present": False, "category": "Electronics", "last_seen": None},
]
alerts = [{"id": 1, "level": "warning", "message": "Camera case has not been scanned", "time": datetime.now(timezone.utc).isoformat()}]
clients: set[WebSocket] = set()

class Telemetry(BaseModel):
    device_id: str = "SC-001"
    battery: int = Field(ge=0, le=100)
    latitude: float | None = None
    longitude: float | None = None
    speed: float = 0
    gps_fix: bool = False
    rssi: int | None = None
    motion: str = "Unknown"

class RFIDScan(BaseModel):
    tag: str
    name: str | None = None

class MotorCommand(BaseModel):
    direction: Literal["forward", "backward", "left", "right", "stop"]
    speed: int = Field(default=120, ge=0, le=255)

async def broadcast():
    payload = {"type": "state", "state": state, "inventory": inventory, "alerts": alerts[:10]}
    dead = []
    for ws in clients:
        try: await ws.send_json(payload)
        except Exception: dead.append(ws)
    for ws in dead: clients.discard(ws)

@app.get("/")
def root(): return {"name": "SMARTCASE API", "docs": "/docs", "demo_mode": DEMO_MODE}

@app.get("/api/status")
def get_status(): return {"state": state, "inventory": inventory, "alerts": alerts[:10], "demo_mode": DEMO_MODE}

@app.get("/api/health")
def health(): return {"ok": True, "time": datetime.now(timezone.utc).isoformat()}

@app.post("/api/device/telemetry")
async def device_telemetry(data: Telemetry, x_device_key: str | None = Header(default=None)):
    if x_device_key != DEVICE_API_KEY: raise HTTPException(401, "Invalid device API key")
    state.update(data.model_dump(exclude_none=True))
    state["online"] = True; state["mode"] = "hardware"; state["last_seen"] = datetime.now(timezone.utc).isoformat()
    await broadcast()
    return {"ok": True}

@app.post("/api/device/rfid")
async def device_rfid(data: RFIDScan, x_device_key: str | None = Header(default=None)):
    if x_device_key != DEVICE_API_KEY: raise HTTPException(401, "Invalid device API key")
    tag = data.tag.upper()
    item = next((x for x in inventory if x["tag"].upper() == tag), None)
    if item:
        item["present"] = True; item["last_seen"] = datetime.now(timezone.utc).isoformat()
    else:
        inventory.append({"id": f"RFID-{tag}", "name": data.name or f"Unknown item {tag}", "tag": tag, "present": True, "category": "Uncategorised", "last_seen": datetime.now(timezone.utc).isoformat()})
    await broadcast()
    return {"ok": True, "item": item or inventory[-1]}

@app.post("/api/command")
async def command(data: MotorCommand):
    # Demo only: never energise motors from an internet-facing endpoint without physical safeguards.
    state["motor"] = data.direction if data.direction == "stop" else "command_pending"
    await broadcast()
    return {"ok": True, "accepted": data.direction, "note": "Demo command recorded. Hardware actuation is disabled until the local safety controller is configured."}

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept(); clients.add(ws)
    try:
        await ws.send_json({"type": "state", "state": state, "inventory": inventory, "alerts": alerts[:10]})
        while True: await ws.receive_text()
    except WebSocketDisconnect: clients.discard(ws)

@app.on_event("startup")
async def demo_loop():
    async def run():
        while True:
            if DEMO_MODE:
                state["battery"] = max(10, min(100, state["battery"] + random.choice([-1, 0, 0, 0, 1])))
                state["last_seen"] = datetime.now(timezone.utc).isoformat()
                await broadcast()
            await asyncio.sleep(4)
    asyncio.create_task(run())
