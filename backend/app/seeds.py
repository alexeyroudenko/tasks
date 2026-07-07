"""Load sample data into PostgreSQL and Neo4j.

Usage: python -m app.seeds
"""

from sqlalchemy import select

from app.database import SessionLocal
from app.graph.edge import Edge
from app.graph.graph import Graph
from app.graph.task import Task
from app.models import Project, User


def create_task(graph: Graph, type: str, title: str, description: str, **attrs) -> Task:
    task = Task(graph, type=type, title=title, description=description, **attrs)
    task.save()

    return task


def relate(graph: Graph, from_task: Task, type: str, to_task: Task) -> None:
    Edge(graph, from_node=from_task, type=type, to_node=to_task).save()


def seed_tasks(graph: Graph) -> None:
    idea = create_task(
        graph, "idea", "Graph project management",
        "Use a directed graph to visualize and manage interdependent tasks.",
    )

    # Task management epic
    manage = create_task(
        graph, "epic", "Task management",
        "Creating, modifying and deleting tasks.",
    )
    create = create_task(
        graph, "feature", "Create a task",
        "A task has a title, description, deadline, status, type and assignee.",
    )
    view = create_task(
        graph, "feature", "View a task",
        "A modal displays all properties of the task.",
    )
    modify = create_task(
        graph, "feature", "Modify a task",
        "All task properties can be edited.",
        status="in_progress",
    )
    delete = create_task(
        graph, "feature", "Delete a task",
        "A confirmation is required before deletion.",
    )
    model = create_task(
        graph, "task", "Design the data model",
        "Decide which data lives in PostgreSQL and which in the graph store.",
        status="done",
    )
    store = create_task(
        graph, "task", "Implement graph storage",
        "Persist tasks as nodes and relationships as edges in Neo4j.",
        status="review",
    )
    quotes = create_task(
        graph, "bug", "Quotes break saving",
        "Titles containing single quotes fail to persist.",
        status="done",
    )

    relate(graph, manage, "child_of", idea)
    relate(graph, create, "child_of", manage)
    relate(graph, view, "child_of", manage)
    relate(graph, modify, "child_of", manage)
    relate(graph, delete, "child_of", manage)
    relate(graph, model, "child_of", create)
    relate(graph, store, "child_of", create)
    relate(graph, quotes, "related_to", modify)

    # Relationships epic
    relationships = create_task(
        graph, "epic", "Relationship management",
        "Linking tasks together with typed, directed relationships.",
    )
    link = create_task(
        graph, "feature", "Link two tasks",
        "Supported types: blocks/blocked by, parent of/child of, related to.",
    )
    unlink = create_task(
        graph, "feature", "Unlink two tasks",
        "Relationships can be removed from the task modal.",
    )

    relate(graph, relationships, "child_of", idea)
    relate(graph, relationships, "blocked_by", manage)
    relate(graph, link, "child_of", relationships)
    relate(graph, unlink, "child_of", relationships)

    # Views epic
    views = create_task(
        graph, "epic", "Views",
        "Displaying tasks and their relationships on screen.",
    )
    graph_view = create_task(
        graph, "feature", "Graph view",
        "Render the project as an interactive force-directed graph.",
    )
    calendar_view = create_task(
        graph, "feature", "Calendar view",
        "Show tasks with deadlines on a monthly calendar.",
    )

    relate(graph, views, "child_of", idea)
    relate(graph, graph_view, "child_of", views)
    relate(graph, calendar_view, "child_of", views)


def run() -> None:
    db = SessionLocal()
    try:
        print("== Creating users ==")
        users = list(db.scalars(select(User)))
        if not users:
            users = [
                User(email="alice@example.com", name="Alice"),
                User(email="bob@example.com", name="Bob"),
            ]
            db.add_all(users)
            db.commit()

        print("== Creating projects ==")
        projects = list(db.scalars(select(Project)))
        if not projects:
            projects = [
                Project(name="Code Red", description="Port of the original demo project", user_id=users[0].id),
            ]
            db.add_all(projects)
            db.commit()

        print("== Creating tasks ==")
        for project in projects:
            graph = Graph(str(project.id))
            if graph.tasks():
                print(f"   {project.name}: already seeded, skipping")
                continue
            seed_tasks(graph)
            print(f"   {project.name}: seeded {len(graph.tasks())} tasks")
    finally:
        db.close()


if __name__ == "__main__":
    run()
