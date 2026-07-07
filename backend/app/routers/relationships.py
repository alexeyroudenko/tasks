from fastapi import APIRouter, Depends, HTTPException

from app.graph.edge import Edge
from app.graph.graph import Graph
from app.graph.task import Task
from app.routers.deps import get_graph
from app.schemas import RelationshipIn

router = APIRouter(
    prefix="/api/projects/{project_id}/relationships", tags=["relationships"]
)


def resolve(graph: Graph, payload: RelationshipIn) -> tuple[Task, str, Task]:
    from_id, type_, to_id = Task.invert(payload.from_id, payload.type, payload.to_id)

    from_task = Task.find(graph, from_id)
    to_task = Task.find(graph, to_id)
    if from_task is None or to_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return from_task, type_, to_task


@router.post("", status_code=201)
def create(payload: RelationshipIn, graph: Graph = Depends(get_graph)) -> dict:
    from_task, type_, to_task = resolve(graph, payload)

    edge = Edge(graph, from_node=from_task, type=type_, to_node=to_task)
    if not edge.save():
        raise HTTPException(status_code=422, detail=edge.validate())

    return {"from_id": from_task.id, "type": type_, "to_id": to_task.id}


@router.delete("", status_code=204)
def destroy(payload: RelationshipIn, graph: Graph = Depends(get_graph)) -> None:
    from_task, type_, to_task = resolve(graph, payload)

    edge = Edge.find(graph, Task, from_id=from_task.id, type=type_, to_id=to_task.id)
    if edge is None:
        raise HTTPException(status_code=404, detail="Relationship not found")

    edge.destroy()
