# Doomsday Ready

A full-stack MCU rewatch planner and watch-party quote tool. The current milestone includes a movie list in React and movie management, rewatch planning, and cinema booking quotes in the API.

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

## Cinema and booking API

| Method and path | Behavior |
| --- | --- |
| GET /api/cinemas | List cinemas and their bundle sizes. |
| POST /api/cinemas | Create a cinema from a name and bundle_sizes array. |
| GET /api/cinemas/{id}/booking?groupSize=6 | Quote a minimum-bundle combination that exactly fits the group. |

Cinema names are trimmed and compared case-sensitively. Each cinema offers 1–10 distinct integer sizes in the range 1–500. Group size ranges from 1 to 10,000. Bundle sizes can be reused in a quote. An impossible fit returns HTTP 200 with possible=false, bundle_count=null, and an empty bundles array.

The quote algorithm computes the best count for each seat total and records the bundle used to reach it. It checks larger sizes first and keeps the first choice when counts tie. For group size G and K bundle sizes, the dynamic programming takes O(G × K) time and O(G) space.
