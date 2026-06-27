from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid

app = FastAPI(
    title="Task Management API",
    description="A modern, high-performance CRUD API built with FastAPI.",
    version="1.0.0"
)

# Pydantic models for request & response body validation
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="The title of the task", examples=["Buy groceries"])
    description: Optional[str] = Field(None, max_length=500, description="Detailed explanation of the task", examples=["Milk, eggs, and bread"])
    completed: bool = Field(default=False, description="Status of task completion")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    completed: Optional[bool] = None

class Task(TaskBase):
    id: str = Field(..., description="Unique task identifier (UUID)")

# In-memory storage acting as our database
tasks_db = {}

@app.get("/", tags=["Health"])
async def root():
    return {"message": "Welcome to the Task Management API. Go to /docs for interactive API documentation."}

@app.get("/tasks", response_model=List[Task], tags=["Tasks"])
async def get_tasks():
    """Retrieve all tasks."""
    return list(tasks_db.values())

@app.get("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def get_task(task_id: str):
    """Retrieve a single task by its unique ID."""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Task with ID '{task_id}' not found"
        )
    return tasks_db[task_id]

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
async def create_task(task: TaskCreate):
    """Create a new task."""
    task_id = str(uuid.uuid4())
    new_task = Task(id=task_id, **task.model_dump())
    tasks_db[task_id] = new_task
    return new_task

@app.put("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def update_task(task_id: str, task_update: TaskUpdate):
    """Update an existing task by its ID."""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Task with ID '{task_id}' not found"
        )
    
    current_task = tasks_db[task_id]
    updated_data = task_update.model_dump(exclude_unset=True)
    
    # Update fields
    for field, value in updated_data.items():
        setattr(current_task, field, value)
        
    tasks_db[task_id] = current_task
    return current_task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
async def delete_task(task_id: str):
    """Delete a task by its ID."""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Task with ID '{task_id}' not found"
        )
    del tasks_db[task_id]
    return None
