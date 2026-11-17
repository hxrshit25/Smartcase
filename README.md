# SMARTCASE V2 — Intelligent Luggage Management

Responsive React + TypeScript PWA, FastAPI backend, demo telemetry, and an Arduino UNO integration scaffold based on the hardware details currently reported:

- Arduino UNO
- RC522 RFID reader + keychain tags
- HM-10 BLE module (BLE central/scanning capability **not yet verified**)
- Beacon reported as “nRF5122” (exact model needs confirmation; possibly nRF51822)
- NEO-6M V2 GPS
- L298N motor driver + Johnson 100 RPM motors
- Battery described as “3+2” (cell arrangement, voltage and capacity unknown)

## What works now
- Responsive dashboard / mobile-friendly PWA shell
- FastAPI status, telemetry, RFID and command endpoints
- Demo mode with clearly labelled illustrative GPS values
- Inventory, map, device health, BLE signal display and movement-control UI
- WebSocket status updates

## Important hardware boundary
The Arduino UNO has no built-in Wi-Fi. The reported parts list does not yet identify a Wi-Fi gateway. Therefore this package **does not claim live remote hardware connectivity**. For remote dashboard data, confirm/add a suitable gateway (for example an ESP8266/ESP32 configured as a bridge) or another network interface. HM-10 modules commonly operate as BLE UART peripherals; do not assume this particular module can scan/act as a BLE central until its firmware/AT commands are verified. The beacon model also needs confirmation.

Motor commands in this project are intentionally non-actuating demo commands. Do not connect these web commands directly to motors. Before movement is enabled, implement local fail-safe control, physical emergency stop, obstacle detection, loss-of-beacon stop, speed limits, battery/current checks and a safe test procedure.

## Run locally
### Backend (Terminal 1)
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
API docs: http://localhost:8000/docs

### Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173.

For a separately hosted frontend, create `frontend/.env` using:
```env
VITE_API_URL=https://YOUR-BACKEND-HOST
```
The backend must be deployed separately; a static Vercel frontend cannot run FastAPI itself. Configure the backend CORS allowed origin to your deployed frontend domain before production.

## Build frontend
```bash
cd frontend
npm run build
```
Output: `frontend/dist/` (deploy this folder as a Vite static site).

## Arduino scaffold
Open `firmware/smartcase_uno_scaffold.ino` in Arduino IDE. Install `MFRC522` and `TinyGPSPlus` libraries. This is a **serial diagnostic scaffold**, not a complete hardware firmware. It reads RC522 tags and NEO-6M GPS and prints JSON-like telemetry to USB Serial. Pin assignments are provisional and must be checked against the actual wiring before powering the circuit. HM-10 BLE scanning and L298N motor control are deliberately not enabled pending verified wiring, module role/firmware, beacon details and safety design.

## API endpoints
- `GET /api/health`
- `GET /api/status`
- `POST /api/device/telemetry` (requires `X-Device-Key`)
- `POST /api/device/rfid` (requires `X-Device-Key`)
- `POST /api/command` (records demo command only)
- `WS /ws`

## Before real deployment
The starter backend uses in-memory demo data and a development device key. Add persistent storage, proper authentication, secret management, HTTPS, rate limiting and device authorization before public use. Never expose device secrets in frontend code.
