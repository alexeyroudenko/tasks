from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import calendar, projects, relationships, tasks, users

app = FastAPI(title="Tasks", description="Graph-based project management")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(relationships.router)
app.include_router(calendar.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
