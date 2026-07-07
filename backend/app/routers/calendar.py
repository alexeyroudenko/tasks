from datetime import date

from fastapi import APIRouter, Depends

from app.graph.graph import Graph
from app.routers.deps import get_graph, serialize_task

router = APIRouter(prefix="/api/projects/{project_id}/calendar", tags=["calendar"])


@router.get("")
def show(year: int, month: int, graph: Graph = Depends(get_graph)) -> dict:
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

    tasks = []
    for task in graph.tasks():
        if not task.deadline:
            continue
        deadline = date.fromisoformat(str(task.deadline))
        if start <= deadline < end:
            tasks.append(serialize_task(task))

    tasks.sort(key=lambda t: t["deadline"])

    return {"year": year, "month": month, "tasks": tasks}
