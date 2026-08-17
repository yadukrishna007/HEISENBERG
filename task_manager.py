"""
Task Manager for Heisenberg V2 Architecture
Tracks multi-step task state (CREATED, IN_PROGRESS, PAUSED, COMPLETED, FAILED)
separately from Planner, enabling task pause, resume, and crash recovery.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional

MEMORY_DIR = os.path.join(os.path.dirname(__file__), "memory")
TASKS_FILE = os.path.join(MEMORY_DIR, "tasks.json")

class TaskStatus:
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Task:
    def __init__(self, task_id: str, description: str, steps: Optional[List[str]] = None, status: str = TaskStatus.CREATED):
        self.id = task_id
        self.description = description
        self.steps = steps or []
        self.completed_steps: List[Dict[str, Any]] = []
        self.status = status
        self.created_at = time.time()
        self.updated_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "steps": self.steps,
            "completed_steps": self.completed_steps,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        task = cls(
            task_id=data["id"],
            description=data["description"],
            steps=data.get("steps", []),
            status=data.get("status", TaskStatus.CREATED)
        )
        task.completed_steps = data.get("completed_steps", [])
        task.created_at = data.get("created_at", time.time())
        task.updated_at = data.get("updated_at", time.time())
        return task


class TaskManager:
    """Gatekeeper for task execution state and persistence."""
    
    def __init__(self, storage_file: str = TASKS_FILE):
        self.storage_file = storage_file
        self.tasks: Dict[str, Task] = {}
        self._ensure_storage_directory()
        self.load_tasks()

    def _ensure_storage_directory(self):
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def load_tasks(self):
        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.tasks = {task_id: Task.from_dict(tdata) for task_id, tdata in data.items()}
        except Exception:
            self.tasks = {}

    def save_tasks(self):
        try:
            data = {task_id: task.to_dict() for task_id, task in self.tasks.items()}
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[TaskManager Error] Failed to save tasks: {e}")

    def create_task(self, description: str, steps: Optional[List[str]] = None) -> Task:
        task_id = f"task_{int(time.time() * 1000)}"
        task = Task(task_id=task_id, description=description, steps=steps)
        self.tasks[task_id] = task
        self.save_tasks()
        return task

    def record_step(self, task_id: str, step_description: str, result_data: Any = None, success: bool = True):
        task = self.tasks.get(task_id)
        if not task:
            return
        task.completed_steps.append({
            "step": step_description,
            "result": result_data,
            "success": success,
            "timestamp": time.time()
        })
        task.status = TaskStatus.IN_PROGRESS
        task.updated_at = time.time()
        self.save_tasks()

    def pause_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if task:
            task.status = TaskStatus.PAUSED
            task.updated_at = time.time()
            self.save_tasks()
            return True
        return False

    def resume_task(self, task_id: str) -> Optional[Task]:
        task = self.tasks.get(task_id)
        if task:
            task.status = TaskStatus.IN_PROGRESS
            task.updated_at = time.time()
            self.save_tasks()
            return task
        return None

    def complete_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if task:
            task.status = TaskStatus.COMPLETED
            task.updated_at = time.time()
            self.save_tasks()
            return True
        return False

    def fail_task(self, task_id: str, error_message: str) -> bool:
        task = self.tasks.get(task_id)
        if task:
            task.status = TaskStatus.FAILED
            task.completed_steps.append({
                "error": error_message,
                "timestamp": time.time()
            })
            task.updated_at = time.time()
            self.save_tasks()
            return True
        return False

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def get_active_tasks(self) -> List[Task]:
        return [t for t in self.tasks.values() if t.status in (TaskStatus.CREATED, TaskStatus.IN_PROGRESS, TaskStatus.PAUSED)]

    def get_interrupted_tasks(self) -> List[Task]:
        """Returns tasks that were left IN_PROGRESS or PAUSED across application restarts."""
        return [t for t in self.tasks.values() if t.status in (TaskStatus.IN_PROGRESS, TaskStatus.PAUSED)]


# Global singleton instance
task_manager = TaskManager()

