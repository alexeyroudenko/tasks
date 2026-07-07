# Tasks

Graph-based project management: tasks and their relationships are modeled as a directed graph.

A Python + TypeScript port of [code-red](https://github.com/floriandejonckheere/code-red) by Florian Dejonckheere (MIT), originally built with Ruby on Rails and RedisGraph.

## What it does

A project consists of a single graph containing many tasks. A task can be an idea, goal, epic, feature, task or bug, with a status of to do, in progress, review or done. Tasks are linked with directed relationships: `blocked_by`, `child_of` or `related_to`. Inverse directions (`blocks`, `parent_of`) are resolved in code and shown in the UI.

The project is rendered as an interactive force-directed graph (D3), and tasks with deadlines appear on a monthly calendar.

## Architecture

- **PostgreSQL** stores administrative data: users and projects (SQLAlchemy + Alembic).
- **Neo4j** stores tasks as nodes and relationships as edges, one logical graph per project (nodes are scoped by a `graph` property carrying the project id).
- **FastAPI** backend exposes a REST API, including a D3-ready graph JSON endpoint.
- **React + Vite + TypeScript + TailwindCSS** frontend with a D3 graph view, task modal and calendar view.

The graph storage layer features a small chainable DSL that translates method calls into Cypher queries, ported from the original app:

```python
graph.match("n", "Task", id=from_id).to("r", "blocked_by").match("m", "Task").delete("r").execute()
# MATCH (n:Task {graph: '...', id: '...'}) -[r:blocked_by]-> (m:Task {graph: '...'}) DELETE r
```

## Setup

Start the databases (and optionally the apps) with Docker:

```bash
docker compose up -d postgres neo4j
```

Backend:

```bash
cd backend
python -m venv .venv
.venv/Scripts/pip install -r requirements-dev.txt   # or .venv/bin/pip on Unix
.venv/Scripts/alembic upgrade head
.venv/Scripts/python -m app.seeds                   # load sample data
.venv/Scripts/uvicorn app.main:app --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

The app is now available at http://localhost:5173 (the dev server proxies `/api` to the backend at port 8000).

Alternatively run everything in containers: `docker compose up -d`.

## API

- `GET/POST /api/projects`, `GET/PATCH/DELETE /api/projects/{id}`
- `GET/POST /api/projects/{id}/tasks`, `GET/PATCH/DELETE /api/projects/{id}/tasks/{task_id}`
- `GET /api/projects/{id}/graph` — D3 payload (`nodes`, `edges`, `groups`, `constraints`)
- `POST/DELETE /api/projects/{id}/relationships` — body `{from_id, type, to_id}`; inverse types are normalized automatically
- `GET /api/projects/{id}/calendar?year=&month=`
- `GET /api/users`

Interactive docs at http://localhost:8000/docs.

## Testing

```bash
cd backend && .venv/Scripts/python -m pytest tests   # DSL, graph models, renderer
cd frontend && npm test                              # vitest
```

CI (GitHub Actions) runs pytest, TypeScript typecheck, vitest and the production build on every push.

## Development workflow

The port was built subtask-by-subtask, one commit per [ROADMAP.md](ROADMAP.md) item, guided by the Cursor skills in [.cursor/skills/](.cursor/skills/).

## License

MIT, see [LICENSE.md](LICENSE.md). Based on [code-red](https://github.com/floriandejonckheere/code-red) by Florian Dejonckheere.
