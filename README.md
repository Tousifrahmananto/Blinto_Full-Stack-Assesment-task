# Doomsday Ready

A full-stack MCU rewatch planner and watch-party quote tool. The current milestone includes a movie list in React and movie management and rewatch planning in the API.

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

## Movie API

Use the interactive docs to create or edit movies and request a rewatch order.

| Method and path | Behavior |
| --- | --- |
| GET /api/movies | List movies with direct prerequisite IDs. |
| POST /api/movies | Create a movie and return it with HTTP 201. |
| PATCH /api/movies/{id} | Update supplied fields. Send an empty prerequisite_ids array to clear prerequisites. |
| GET /api/movies/{id}/rewatch-order | Return all prerequisite movies in viewing order, their watched count and unwatched runtime. |

Titles are trimmed and compared case-sensitively. Release years are four-digit integers and runtimes range from 1 to 300 minutes. Prerequisites must be existing movies. Repeated prerequisite IDs collapse to a single link. A cycle returns HTTP 409 with code CIRCULAR_DEPENDENCY and leaves the database unchanged.

The service follows prerequisite links using iterative depth-first search. Each movie is appended after its prerequisites. A movie already on the active path signals a cycle, while a completed movie has already been counted. The traversal takes O(V + E) time for the reachable graph and O(V) extra space. SQLite serializes the validation and write so concurrent requests cannot jointly introduce a cycle.
