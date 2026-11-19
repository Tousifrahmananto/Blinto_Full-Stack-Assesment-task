# Doomsday Ready

A full-stack MCU rewatch planner and watch-party quote tool. The current milestone lists movies from a local SQLite database.

## Run locally

Requires Python 3.11 and Node 24 LTS (tested versions).

In PowerShell, from the repository root, start the backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

From the root in another terminal, start the frontend:

```powershell
cd frontend
npm ci
npm run dev
```

Open http://localhost:5173 for the app or http://127.0.0.1:8000/docs for the API. A fresh database starts with an empty movie list. Vite forwards local /api requests to FastAPI.

From backend, run `.\.venv\Scripts\python.exe -m pytest`. From frontend, run `npm run build`.

## AI assistance

Codex helped review the assessment, plan the architecture, scaffold the project and verify the movie list setup.
