# SMARTCASE Backend

## Run
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Open http://localhost:8000/docs.

Demo mode is enabled in this starter. Before real deployment, move secrets to environment variables, add persistent storage/authentication, and configure a local motor safety controller. The `/api/device/telemetry` and `/api/device/rfid` endpoints require `X-Device-Key: change-this-device-key`.
