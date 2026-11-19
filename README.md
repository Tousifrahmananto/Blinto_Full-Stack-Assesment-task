# Doomsday Ready

A full-stack MCU rewatch planner and watch-party quote tool. Add movies and prerequisites, build a rewatch plan, and calculate the seat bundles your group needs.

## Run with Docker

With Docker running, start the app from the repository root:

~~~sh
docker compose up --build
~~~

Open http://127.0.0.1:4173. Set the DOOMSDAY_PORT environment variable before starting Compose if that port is in use. Nginx serves the built React site and forwards /api requests to FastAPI. The backend stores SQLite in the sqlite-data named volume, so records survive normal restarts and docker compose down. Run docker compose down to stop the app.

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

Open http://localhost:5173 for the app or http://127.0.0.1:8000/docs for the API. A fresh database starts empty. Add movies in Movies and cinemas in Booking, then use Rewatch Plan or request a booking quote. Vite forwards local /api requests to FastAPI.

From backend, run `.\.venv\Scripts\python.exe -m pytest`. From frontend, run `npm run build`.

## Try the app

1. In **Movies**, add Iron Man (2008, 126 minutes) and The Avengers (2012, 143 minutes). Set Iron Man as a prerequisite of The Avengers.
2. In **Rewatch Plan**, select The Avengers. The plan lists Iron Man and shows 126 minutes remaining. Mark Iron Man watched in **Movies**, then generate the plan again to see the remaining time drop to zero.
3. In **Booking**, add a cinema with bundle sizes 1, 3, 4. Quote six seats. The result is two 3-seat bundles.

## Project structure

~~~mermaid
flowchart LR
    Browser["Browser<br/>HTML page + React views"]
    API["FastAPI<br/>Controllers"]
    Services["Python services<br/>Rewatch and booking algorithms"]
    Database[("SQLite")]
    Browser <-->|"HTTP / JSON"| API
    API <--> Services
    Services <--> Database
~~~

The browser starts with frontend/index.html, which supplies the document and the root element. React renders the screens inside that element from JSX in frontend/src. CSS controls the appearance. FastAPI controllers handle requests, and the Python services apply the rules and talk to SQLite.

## Data model

~~~mermaid
erDiagram
    MOVIES ||--o{ MOVIE_PREREQUISITES : "movie"
    MOVIES ||--o{ MOVIE_PREREQUISITES : "required movie"
    CINEMAS ||--o{ CINEMA_BUNDLE_SIZES : "offers"

    MOVIES {
        int id PK
        string title UK
        int release_year
        int runtime_minutes
        bool watched
    }
    MOVIE_PREREQUISITES {
        int movie_id PK, FK
        int prerequisite_id PK, FK
    }
    CINEMAS {
        int id PK
        string name UK
    }
    CINEMA_BUNDLE_SIZES {
        int cinema_id PK, FK
        int size PK
    }
~~~

Each prerequisite row links a movie to another movie that must be watched first. The pair of IDs is unique. Each cinema has one row per offered bundle size. Rewatch plans and booking quotes are calculated on request from these records.

## Movie API

Use the interactive docs to create or edit movies and request a rewatch order.

| Method and path | Behavior |
| --- | --- |
| GET /api/movies | List movies with direct prerequisite IDs. |
| POST /api/movies | Create a movie and return it with HTTP 201. |
| PATCH /api/movies/{id} | Update supplied fields. Send an empty prerequisite_ids array to clear prerequisites. |
| GET /api/movies/{id}/rewatch-order | Return all prerequisite movies in viewing order, their watched count and unwatched runtime. |

Titles are trimmed and compared case-sensitively. Release years are four-digit integers and runtimes range from 1 to 300 minutes. Prerequisites must be existing movies. Repeated prerequisite IDs collapse to a single link. A cycle returns HTTP 409 with code CIRCULAR_DEPENDENCY and leaves the database unchanged.

The service follows prerequisite links using iterative depth-first search. Each movie is appended after its prerequisites. A movie already on the active path signals a cycle, while a completed movie has already been counted. The traversal takes O(V + E) time for the reachable graph. Its stack can hold O(V + E) entries because a shared prerequisite can be queued by multiple movies. SQLite serializes the validation and write so concurrent requests cannot jointly introduce a cycle.

## Cinema and booking API

| Method and path | Behavior |
| --- | --- |
| GET /api/cinemas | List cinemas and their bundle sizes. |
| POST /api/cinemas | Create a cinema from a name and bundle_sizes array. |
| GET /api/cinemas/{id}/booking?groupSize=6 | Quote a minimum-bundle combination that exactly fits the group. |

Cinema names are trimmed and compared case-sensitively. Each cinema offers 1–10 distinct integer sizes in the range 1–500. Group size ranges from 1 to 10,000. Bundle sizes can be reused in a quote. An impossible fit returns HTTP 200 with possible=false, bundle_count=null, and an empty bundles array.

The quote algorithm computes the best count for each seat total and records the bundle used to reach it. It checks larger sizes first and keeps the first choice when counts tie. For group size G and K bundle sizes, the dynamic programming takes O(G × K) time and O(G) space.

## AI assistance

I wrote the final implementations of both core algorithms myself. These are the movie prerequisite traversal and the minimum-bundle booking calculation. I used Codex to study earlier drafts and for help with planning, the React and FastAPI code, testing, deployment checks, and documentation.
