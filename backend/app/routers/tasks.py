from fastapi import APIRouter, Depends, HTTPException

from app.graph.graph import Graph
from app.graph.renderer import Renderer
from app.graph.task import Task
from app.routers.deps import get_graph, serialize_task
from app.schemas import TaskIn, TaskPatch

router = APIRouter(prefix="/api/projects/{project_id}", tags=["tasks"])


def find_task(graph: Graph, task_id: str) -> Task:
    task = Task.find(graph, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.get("/tasks")
def index(graph: Graph = Depends(get_graph)) -> list[dict]:
    return [serialize_task(task) for task in graph.tasks()]


@router.post("/tasks", status_code=201)
def create(payload: TaskIn, graph: Graph = Depends(get_graph)) -> dict:
    task = Task(graph, **payload.model_dump())
    if not task.save():
        raise HTTPException(status_code=422, detail=task.validate())

    return serialize_task(task, relationships=True)


@router.get("/tasks/{task_id}")
def show(task_id: str, graph: Graph = Depends(get_graph)) -> dict:
    return serialize_task(find_task(graph, task_id), relationships=True)


@router.patch("/tasks/{task_id}")
def update(task_id: str, payload: TaskPatch, graph: Graph = Depends(get_graph)) -> dict:
    task = find_task(graph, task_id)
    if not task.update(**payload.model_dump(exclude_unset=True)):
        raise HTTPException(status_code=422, detail=task.validate())

    return serialize_task(task, relationships=True)


@router.delete("/tasks/{task_id}", status_code=204)
def destroy(task_id: str, graph: Graph = Depends(get_graph)) -> None:
    find_task(graph, task_id).destroy()


@router.get("/graph")
def graph_json(graph: Graph = Depends(get_graph)) -> dict:
    return Renderer(graph).to_dict()
