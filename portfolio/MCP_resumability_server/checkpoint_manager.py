#!/usr/bin/env python3
"""
Checkpoint and resumability system for MCP streaming tasks.
Allows saving the state of long tasks and resuming them from where they were interrupted.
"""

import json
import pickle
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class TaskStatus(Enum):
    """Task states."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskCheckpoint:
    """Represents a checkpoint of a task."""
    task_id: str
    session_id: str
    task_name: str
    parameters: Dict[str, Any]
    current_step: int
    total_steps: int
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    data: Dict[str, Any]  # Estado específico de la tarea
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        data = asdict(self)
        data['status'] = data['status'].value
        data['created_at'] = data['created_at'].isoformat()
        data['updated_at'] = data['updated_at'].isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskCheckpoint':
        """Create from dictionary."""
        data['status'] = TaskStatus(data['status'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


class CheckpointManager:
    """Checkpoint manager for streaming tasks."""
    
    def __init__(self, storage_dir: str = "checkpoints"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.checkpoints_file = self.storage_dir / "checkpoints.json"
        self.data_dir = self.storage_dir / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self._checkpoints: Dict[str, TaskCheckpoint] = {}
        self._load_checkpoints()
    
    def _load_checkpoints(self):
        """Load checkpoints from disk."""
        if self.checkpoints_file.exists():
            try:
                with open(self.checkpoints_file, 'r') as f:
                    data = json.load(f)
                    self._checkpoints = {
                        task_id: TaskCheckpoint.from_dict(checkpoint_data)
                        for task_id, checkpoint_data in data.items()
                    }
            except Exception as e:
                print(f"❌ Error loading checkpoints: {e}")
                self._checkpoints = {}
    
    def _save_checkpoints(self):
        """Save checkpoints to disk."""
        try:
            data = {
                task_id: checkpoint.to_dict()
                for task_id, checkpoint in self._checkpoints.items()
            }
            with open(self.checkpoints_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving checkpoints: {e}")
    
    def generate_task_id(self, session_id: str, task_name: str, parameters: Dict[str, Any]) -> str:
        """Generate unique ID for a task."""
        # Create hash based on session, task and parameters
        data = f"{session_id}-{task_name}-{json.dumps(parameters, sort_keys=True)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def create_checkpoint(
        self,
        session_id: str,
        task_name: str,
        parameters: Dict[str, Any],
        total_steps: int,
        initial_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create new checkpoint."""
        task_id = self.generate_task_id(session_id, task_name, parameters)
        
        checkpoint = TaskCheckpoint(
            task_id=task_id,
            session_id=session_id,
            task_name=task_name,
            parameters=parameters,
            current_step=0,
            total_steps=total_steps,
            status=TaskStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            data=initial_data or {}
        )
        
        self._checkpoints[task_id] = checkpoint
        self._save_checkpoints()
        
        return task_id
    
    def update_checkpoint(
        self,
        task_id: str,
        current_step: int,
        status: TaskStatus,
        data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Update existing checkpoint."""
        if task_id not in self._checkpoints:
            return False
        
        checkpoint = self._checkpoints[task_id]
        checkpoint.current_step = current_step
        checkpoint.status = status
        checkpoint.updated_at = datetime.now(timezone.utc)
        
        if data is not None:
            checkpoint.data.update(data)
        
        if error_message is not None:
            checkpoint.error_message = error_message
        
        self._save_checkpoints()
        return True
    
    def get_checkpoint(self, task_id: str) -> Optional[TaskCheckpoint]:
        """Get checkpoint by ID."""
        return self._checkpoints.get(task_id)
    
    def find_resumable_task(
        self,
        session_id: str,
        task_name: str,
        parameters: Dict[str, Any]
    ) -> Optional[TaskCheckpoint]:
        """Find resumable task with the same parameters."""
        task_id = self.generate_task_id(session_id, task_name, parameters)
        checkpoint = self._checkpoints.get(task_id)
        
        if checkpoint and checkpoint.status in [TaskStatus.PAUSED, TaskStatus.RUNNING]:
            return checkpoint
        
        return None
    
    def get_session_checkpoints(self, session_id: str) -> List[TaskCheckpoint]:
        """Get all checkpoints of a session."""
        return [
            checkpoint for checkpoint in self._checkpoints.values()
            if checkpoint.session_id == session_id
        ]
    
    def save_task_data(self, task_id: str, data: Any) -> bool:
        """Save specific task data."""
        try:
            data_file = self.data_dir / f"{task_id}.pkl"
            with open(data_file, 'wb') as f:
                pickle.dump(data, f)
            return True
        except Exception as e:
            print(f"❌ Error saving task data {task_id}: {e}")
            return False
    
    def load_task_data(self, task_id: str) -> Any:
        """Load specific task data."""
        try:
            data_file = self.data_dir / f"{task_id}.pkl"
            if data_file.exists():
                with open(data_file, 'rb') as f:
                    return pickle.load(f)
            return None
        except Exception as e:
            print(f"❌ Error loading task data {task_id}: {e}")
            return None
    
    def delete_checkpoint(self, task_id: str) -> bool:
        """Delete checkpoint and associated data."""
        try:
            # Delete checkpoint
            if task_id in self._checkpoints:
                del self._checkpoints[task_id]
                self._save_checkpoints()
            
            # Delete data
            data_file = self.data_dir / f"{task_id}.pkl"
            if data_file.exists():
                data_file.unlink()
            
            return True
        except Exception as e:
            print(f"❌ Error deleting checkpoint {task_id}: {e}")
            return False
    
    def cleanup_old_checkpoints(self, max_age_days: int = 7) -> int:
        """Clean up old checkpoints."""
        cutoff_date = datetime.now(timezone.utc).replace(
            day=datetime.now(timezone.utc).day - max_age_days
        )
        
        to_delete = []
        for task_id, checkpoint in self._checkpoints.items():
            if (checkpoint.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
                and checkpoint.updated_at < cutoff_date):
                to_delete.append(task_id)
        
        for task_id in to_delete:
            self.delete_checkpoint(task_id)
        
        return len(to_delete)
    
    def get_stats(self) -> Dict[str, int]:
        """Get checkpoint statistics."""
        stats = {status.value: 0 for status in TaskStatus}
        
        for checkpoint in self._checkpoints.values():
            stats[checkpoint.status.value] += 1
        
        return stats


# Singleton global for checkpoint manager
checkpoint_manager = CheckpointManager()