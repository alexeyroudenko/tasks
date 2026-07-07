import uuid

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.graph.graph import Graph
from app.graph.task import Task
from app.models import Project


def get_project(project_id: uuid.UUID, db: Session = Depends(get_db)) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


def get_graph(project: Project = Depends(get_project)) -> Graph:
    return Graph(str(project.id))


def serialize_task(task: Task, relationships: bool = False) -> dict:
    data = {name: getattr(task, name) for name in task.attributes}

    if relationships:
        data["relationships"] = {
            name: [{"id": t.id, "title": t.title} for t in task.related(name)]
            for name in ("blocks", "blocked_by", "parent_of", "child_of", "related_to")
        }

    return data
