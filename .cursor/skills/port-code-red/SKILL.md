---
name: port-code-red
description: Domain knowledge for porting the code-red graph task manager (Ruby on Rails + RedisGraph) to FastAPI + React/TypeScript with Neo4j and PostgreSQL. Use when implementing any ROADMAP.md subtask in this repository, or when questions arise about the original app's data model, Cypher DSL, endpoints, or seed data.
---

# Porting code-red to Python + TypeScript

Original: https://github.com/floriandejonckheere/code-red (MIT, archived). Rewrite behavior in idiomatic Python/TypeScript — do not transliterate Ruby.

## Target layout

- `backend/` — FastAPI app: `app/models/` (SQLAlchemy), `app/graph/` (Cypher DSL + graph models), `app/routers/`, `app/seeds.py`, `tests/`
- `frontend/` — Vite + React + TS + Tailwind: `src/components/`, `src/api/`
- `docker-compose.yml` — postgres, neo4j, backend, frontend

## Data model

Relational (PostgreSQL, UUID PKs):

- `User`: email (not null, indexed), name (not null), timestamps
- `Project`: name (not null), description, icon (default `clipboard-list`), user_id (FK users, nullable, ON DELETE SET NULL), timestamps

Graph (Neo4j; one logical graph per project, nodes carry `project_id` property since Neo4j has no per-graph namespacing like RedisGraph keys):

- `Task` node: id (UUID), title (required), description (rich text HTML), deadline (date), status (`todo|in_progress|review|done`, default `todo`), type (`idea|goal|epic|feature|task|bug`, default `task`), user_id (optional assignee), created_at, updated_at
- Edge types: `related_to`, `blocked_by`, `child_of`. Inverse pseudo-relationships resolved in code, not stored: `blocks` = inverse of `blocked_by`, `parent_of` = inverse of `child_of`. `Task.invert()` swaps from/to and replaces the inverse name with the stored type before persisting or querying.

## Cypher DSL

Chainable query builder mirroring the original `app/graph/dsl.rb`:

- `match(name, label=None, **attrs)` / `merge(...)` — add `(name:Label {k: 'v'})` to the clause; sets "target" for a following `to()`
- `to(name, label=None)` — appends `-[name:label]->` to the current target clause
- `return_(*names, **aliases)` — aliases render as `expr AS alias`
- `delete(*names)`, `set(**attrs)` — set applies attrs to all collected names
- `to_cypher()` — join non-empty clauses in order MATCH, MERGE, RETURN, DELETE, SET; within MATCH/MERGE, elements are comma-separated except around `-[...]->` arrows (space-separated)
- `execute()` — run via neo4j driver session, return list of dicts keyed by names/aliases

Example: `graph.match("n", "Task", id=x).to("r", "blocked_by").match("m", "Task").delete("r")` → `MATCH (n:Task {id: 'x'}) -[r:blocked_by]-> (m:Task) DELETE r`.

Escape single quotes in values. Node save = `MERGE` on id + `SET` all attributes (upsert; create and update share one code path). Timestamps set in code before save.

## API endpoints (FastAPI)

- `GET/POST /api/projects`, `GET/PATCH/DELETE /api/projects/{id}`
- `GET/POST /api/projects/{id}/tasks`, `GET/PATCH/DELETE .../tasks/{task_id}`
- `GET /api/projects/{id}/graph` — D3 payload: `{nodes, edges, groups, constraints}`; nodes = `{id, label, icon, color, type, status}`, edges = `{source, target, label}` using node indices, groups = children of feature tasks, constraints = y-axis ordering between consecutive type groups (gap 150)
- `POST/DELETE /api/projects/{id}/relationships` — body `{from_id, type, to_id}`, apply `Task.invert` first
- `GET /api/projects/{id}/calendar?year=&month=` — tasks with deadlines in that month
- `GET /api/users`

## Frontend notes

- Graph view: D3 force simulation (original used cola.js; d3-force is fine), rectangular nodes with title, type icon and status color, directed edges with arrowheads and rotated labels, zoom/pan, click node opens task modal
- Task modal: title, rich text description, deadline, status, type, assignee selects; relationships list with add/remove (six directions: blocks, blocked by, parent of, child of, related to)
- Colors by status: todo gray, in_progress blue, review yellow, done green. Colors by type: idea purple, goal red, epic pink, feature blue, task gray, bug red.

## Seeds

Port `db/seeds/development/`: 2 users, 1 project per user, ~20 tasks forming a tree (idea → epics → features → tasks/bugs) with `child_of`, `blocked_by`, `related_to` edges. Skip seeding if the project already has tasks.
