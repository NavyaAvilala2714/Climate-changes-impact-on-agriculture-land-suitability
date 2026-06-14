# Climate Land Suitability – Python Backend

FastAPI + SQLite backend for the Climate Change Land Suitability app. Replaces the Node/Express server.

## Setup

```bash
cd backend
pip install -r requirements.txt
```

## Run

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 5000
```

- API base: `http://127.0.0.1:5000`
- Docs: `http://127.0.0.1:5000/docs`

**With the frontend:** Start this backend first, then from the project root run `npm run dev:frontend`. The Vite dev server proxies `/api` to this backend.

## API (match frontend)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/regions` | List regions |
| GET | `/api/regions/{id}` | Get region by id |
| GET | `/api/scenarios` | List scenarios |
| GET | `/api/analysis/predict?regionId=&scenarioId=&timePeriod=` | Suitability prediction (returns prediction + region + scenario) |

Database is created and seeded automatically on first run (`climate.db` in this folder). To reseed (e.g. after adding new data), delete `climate.db` and restart the backend.
