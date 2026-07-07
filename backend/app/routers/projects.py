from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.graph.graph import Graph
from app.models import Project
from app.routers.deps import get_project
from app.schemas import ProjectIn, ProjectOut, ProjectPatch

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut])
def index(db: Session = Depends(get_db)) -> list[Project]:
    return list(db.scalars(select(Project).order_by(Project.created_at)))


@router.post("", response_model=ProjectOut, status_code=201)
def create(payload: ProjectIn, db: Session = Depends(get_db)) -> Project:
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()

    return project


@router.get("/{project_id}", response_model=ProjectOut)
def show(project: Project = Depends(get_project)) -> Project:
    return project


@router.patch("/{project_id}", response_model=ProjectOut)
def update(
    payload: ProjectPatch,
    project: Project = Depends(get_project),
    db: Session = Depends(get_db),
) -> Project:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    db.add(project)
    db.commit()

    return project


@router.delete("/{project_id}", status_code=204)
def destroy(
    project: Project = Depends(get_project), db: Session = Depends(get_db)
) -> None:
    Graph(str(project.id)).delete_all()

    db.delete(project)
    db.commit()
