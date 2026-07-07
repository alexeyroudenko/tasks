# Roadmap

Port of [code-red](https://github.com/floriandejonckheere/code-red) (Ruby on Rails + RedisGraph) to Python (FastAPI) + TypeScript (React), with Neo4j and PostgreSQL.

Each subtask is implemented and committed separately.

- [x] 0. Repository bootstrap: git init, GitHub repo, README, LICENSE
- [x] 1. Cursor skills (`.cursor/skills/`) and this roadmap
- [x] 2. Scaffolding: docker-compose (postgres, neo4j), `backend/` (FastAPI), `frontend/` (Vite + React + TS + Tailwind)
- [x] 3. Relational layer: SQLAlchemy models `User`, `Project` (UUID PK), Alembic migrations
- [x] 4. Graph layer: Cypher DSL query builder, `Node`, `Edge`, `Task` models on Neo4j
- [x] 5. REST API: projects CRUD, tasks CRUD, relationships add/remove, D3 graph JSON endpoint, calendar endpoint
- [ ] 6. Frontend: Tailwind layout, task list/modal with form, D3 force graph, calendar view
- [ ] 7. Seeds and tests: sample data seeder, pytest for the DSL and graph models, vitest for frontend
- [ ] 8. Final: GitHub Actions CI, complete README
