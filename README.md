# Football Video Analytics Platforms

Production-ready AI-powered football match analysis system.

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Architecture
- **Video Ingestion** → Frame extraction via OpenCV
- **Detection** → YOLOv8 player/ball detection
- **Tracking** → DeepSORT persistent ID tracking
- **Event Detection** → Heuristic pass/shot/possession inference
- **Analytics Engine** → Aggregated match statistics
- **API Layer** → FastAPI REST + WebSocket
- **Dashboard** → React + Tailwind + Recharts
