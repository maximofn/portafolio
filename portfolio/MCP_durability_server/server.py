"""
MCP Durability Server

MPC server that implements durability for long-running agents using Resource links.
Allows long-running operations to survive server restarts and provides state tracking
outside of band.

Implemented pattern:
1. Tools return resource links immediately
2. Background processing continues asynchronously
3. Clients can poll or subscribe to resources for state updates

Usage:
    python server.py
"""

import asyncio
import json
import sqlite3
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from fastmcp.server.context import Context


class TaskStatus(Enum):
    """Long running task status."""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskResult:
    """Result data for a completed task."""
    task_id: str
    status: TaskStatus
    progress: float = 0.0
    total: Optional[float] = None
    message: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: float = 0.0
    updated_at: float = 0.0
    completed_at: Optional[float] = None


class DurableTaskManager:
    """Manages persistent task state and background execution."""
    
    def __init__(self, db_path: str = "mcp_tasks.db"):
        self.db_path = db_path
        self._background_tasks: Dict[str, asyncio.Task] = {}
        self._setup_database()
    
    def _setup_database(self) -> None:
        """Initializes SQLite database for task persistence."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                progress REAL DEFAULT 0.0,
                total REAL,
                message TEXT,
                result_data TEXT,
                error TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                completed_at REAL
            )
        """)
        conn.commit()
        conn.close()
    
    async def create_task(self, task_id: Optional[str] = None) -> str:
        """Creates a new task and returns its ID."""
        if not task_id:
            task_id = str(uuid.uuid4())
        
        current_time = time.time()
        task_result = TaskResult(
            task_id=task_id,
            status=TaskStatus.PENDING,
            created_at=current_time,
            updated_at=current_time
        )
        
        await self._save_task(task_result)
        return task_id
    
    async def start_background_task(
        self, 
        task_id: str, 
        task_function, 
        context: Optional[Context] = None
    ) -> None:
        """Starts a background task and tracks its execution."""
        async def wrapper():
            try:
                await self._update_task_status(task_id, TaskStatus.RUNNING)
                
                # Execute the real task
                if context:
                    result = await task_function(task_id, context, self)
                else:
                    result = await task_function(task_id, self)
                
                # Mark as completed with results
                await self._update_task_completion(task_id, result)
                
            except asyncio.CancelledError:
                await self._update_task_status(task_id, TaskStatus.CANCELLED)
                raise
            except Exception as e:
                await self._update_task_error(task_id, str(e))
            finally:
                # Clean up background task reference
                self._background_tasks.pop(task_id, None)
        
        # Start the task in the background
        task = asyncio.create_task(wrapper())
        self._background_tasks[task_id] = task
    
    async def _save_task(self, task_result: TaskResult) -> None:
        """Saves the task result to the database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO tasks 
            (task_id, status, progress, total, message, result_data, error, 
             created_at, updated_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_result.task_id,
            task_result.status.value,
            task_result.progress,
            task_result.total,
            task_result.message,
            json.dumps(task_result.result_data) if task_result.result_data else None,
            task_result.error,
            task_result.created_at,
            task_result.updated_at,
            task_result.completed_at
        ))
        conn.commit()
        conn.close()
    
    async def get_task(self, task_id: str) -> Optional[TaskResult]:
        """Retrieves the task result from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT task_id, status, progress, total, message, result_data, error,
                   created_at, updated_at, completed_at
            FROM tasks WHERE task_id = ?
        """, (task_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        result_data = None
        if row[5]:  # result_data
            try:
                result_data = json.loads(row[5])
            except json.JSONDecodeError:
                pass
        
        return TaskResult(
            task_id=row[0],
            status=TaskStatus(row[1]),
            progress=row[2],
            total=row[3],
            message=row[4],
            result_data=result_data,
            error=row[6],
            created_at=row[7],
            updated_at=row[8],
            completed_at=row[9]
        )
    
    async def update_task_progress(
        self, 
        task_id: str, 
        progress: float, 
        total: Optional[float] = None,
        message: Optional[str] = None
    ) -> None:
        """Updates the task progress."""
        task_result = await self.get_task(task_id)
        if not task_result:
            return
        
        task_result.progress = progress
        if total is not None:
            task_result.total = total
        if message is not None:
            task_result.message = message
        task_result.updated_at = time.time()
        
        await self._save_task(task_result)
    
    async def _update_task_status(self, task_id: str, status: TaskStatus) -> None:
        """Updates the task status."""
        task_result = await self.get_task(task_id)
        if not task_result:
            return
        
        task_result.status = status
        task_result.updated_at = time.time()
        await self._save_task(task_result)
    
    async def _update_task_completion(self, task_id: str, result_data: Any) -> None:
        """Marks the task as completed with results."""
        task_result = await self.get_task(task_id)
        if not task_result:
            return
        
        task_result.status = TaskStatus.COMPLETED
        task_result.progress = task_result.total or 100.0
        task_result.result_data = result_data if isinstance(result_data, dict) else {"result": result_data}
        task_result.completed_at = time.time()
        task_result.updated_at = time.time()
        
        await self._save_task(task_result)
    
    async def _update_task_error(self, task_id: str, error: str) -> None:
        """Marks the task as failed with error."""
        task_result = await self.get_task(task_id)
        if not task_result:
            return
        
        task_result.status = TaskStatus.FAILED
        task_result.error = error
        task_result.updated_at = time.time()
        
        await self._save_task(task_result)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancels a background task in execution."""
        if task_id in self._background_tasks:
            task = self._background_tasks[task_id]
            task.cancel()
            await self._update_task_status(task_id, TaskStatus.CANCELLED)
            return True
        return False
    
    async def list_tasks(self, status_filter: Optional[TaskStatus] = None) -> List[TaskResult]:
        """Lists all tasks, optionally filtered by status."""
        conn = sqlite3.connect(self.db_path)
        
        if status_filter:
            cursor = conn.execute("""
                SELECT task_id, status, progress, total, message, result_data, error,
                       created_at, updated_at, completed_at
                FROM tasks WHERE status = ? ORDER BY updated_at DESC
            """, (status_filter.value,))
        else:
            cursor = conn.execute("""
                SELECT task_id, status, progress, total, message, result_data, error,
                       created_at, updated_at, completed_at
                FROM tasks ORDER BY updated_at DESC
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        tasks = []
        for row in rows:
            result_data = None
            if row[5]:
                try:
                    result_data = json.loads(row[5])
                except json.JSONDecodeError:
                    pass
            
            tasks.append(TaskResult(
                task_id=row[0],
                status=TaskStatus(row[1]),
                progress=row[2],
                total=row[3],
                message=row[4],
                result_data=result_data,
                error=row[6],
                created_at=row[7],
                updated_at=row[8],
                completed_at=row[9]
            ))
        
        return tasks


# Create the MCP server with durability capabilities
server = FastMCP(
    name="MCP Durability Server",
    instructions="An MCP server that demonstrates durability for long-running agents"
)

# Initialize the task manager
task_manager = DurableTaskManager()


# Resources to track the state of tasks
@server.resource("task://status/{task_id}")
async def get_task_status(task_id: str) -> str:
    """Gets the current status of a task by ID."""
    task_result = await task_manager.get_task(task_id)
    if not task_result:
        return json.dumps({"error": "Task not found", "task_id": task_id})
    
    data = {
        "task_id": task_result.task_id,
        "status": task_result.status.value,
        "progress": task_result.progress,
        "total": task_result.total,
        "message": task_result.message,
        "result_data": task_result.result_data,
        "error": task_result.error,
        "created_at": task_result.created_at,
        "updated_at": task_result.updated_at,
        "completed_at": task_result.completed_at,
    }
    
    return json.dumps(data)


@server.resource("task://list")
async def list_all_tasks() -> str:
    """Lists all tasks with their current status."""
    tasks = await task_manager.list_tasks()
    data = {
        "tasks": [
            {
                "task_id": task.task_id,
                "status": task.status.value,
                "progress": task.progress,
                "total": task.total,
                "message": task.message,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "completed_at": task.completed_at,
                "has_result": task.result_data is not None,
                "has_error": task.error is not None
            } for task in tasks
        ],
        "total": len(tasks)
    }
    return json.dumps(data)


@server.resource("task://list/{status}")
async def list_tasks_by_status(status: str) -> str:
    """Lists tasks filtered by status."""
    try:
        status_enum = TaskStatus(status.lower())
        tasks = await task_manager.list_tasks(status_enum)
        data = {
            "tasks": [
                {
                    "task_id": task.task_id,
                    "status": task.status.value,
                    "progress": task.progress,
                    "total": task.total,
                    "message": task.message,
                    "created_at": task.created_at,
                    "updated_at": task.updated_at,
                    "completed_at": task.completed_at
                } for task in tasks
            ],
            "status_filter": status,
            "total": len(tasks)
        }
        return json.dumps(data)
    except ValueError:
        data = {
            "error": f"Invalid status: {status}",
            "valid_statuses": [s.value for s in TaskStatus]
        }
        return json.dumps(data)


# Tools to demonstrate durability functionality
@server.tool
async def start_data_migration(
    source_path: str,
    destination_path: str,
    ctx: Context,
    record_count: int = 1000
) -> str:
    """
    Starts a long-running data migration task.
    
    Args:
        source_path: Source path of the data
        destination_path: Destination path of the data  
        record_count: Number of records to migrate
        ctx: Contexto MCP
    
    Returns:
        Resource URI to track progress
    """
    await ctx.info(f"Starting migration of {record_count} records from {source_path} to {destination_path}")
    print(f"Starting migration of {record_count} records from {source_path} to {destination_path}")
    
    async def migration_task(task_id: str, context: Context, manager: DurableTaskManager):
        """Simulated data migration task."""
        batch_size = 100
        migrated = 0
        
        for batch_start in range(0, record_count, batch_size):
            # Simulate batch processing
            await asyncio.sleep(1)  # Simulate work
            
            batch_end = min(batch_start + batch_size, record_count)
            migrated = batch_end
            
            # Update progress
            progress_pct = (migrated / record_count) * 100
            message = f"Migrated {migrated}/{record_count} records"
            
            await manager.update_task_progress(task_id, progress_pct, 100.0, message)
            try:
                await context.report_progress(migrated, record_count, message)
            except Exception:
                pass
        
        try:
            await context.info(f"Data migration completed: {migrated} records")
        except Exception:
            pass
        
        return {
            "migrated_records": migrated,
            "total_records": record_count,
            "source_path": source_path,
            "destination_path": destination_path,
            "success": True,
            "completion_time": time.time()
        }
    
    # Create the task and start background processing
    task_id = await task_manager.create_task()
    await task_manager.start_background_task(task_id, migration_task, ctx)
    
    resource_link = f"task://status/{task_id}"
    await ctx.info(f"Data migration started. Track progress at: {resource_link}")
    
    return resource_link


@server.tool  
async def start_batch_processing(
    batch_size: int,
    total_items: int,
    ctx: Context,
    processing_delay: float = 10
) -> str:
    """
    Starts a batch processing task.
    
    Args:
        batch_size: Size of each batch
        total_items: Total number of items to process
        processing_delay: Delay per batch in seconds
        ctx: MCP context
    
    Returns:
        Resource URI to track progress
    """
    await ctx.info(f"Starting batch processing: {total_items} items in batches of {batch_size}")
    
    async def batch_task(task_id: str, context: Context, manager: DurableTaskManager):
        """Batch processing task."""
        processed = 0
        
        for i in range(0, total_items, batch_size):
            await asyncio.sleep(processing_delay)   # Simulate work
            batch_end = min(i + batch_size, total_items)
            processed = batch_end
            
            progress = (processed / total_items) * 100
            message = f"Processed {processed}/{total_items} items"
            
            await manager.update_task_progress(task_id, progress, 100.0, message)
            await context.report_progress(processed, total_items, message)
        
        await context.info(f"Batch processing completed: {processed} items")
        
        return {
            "processed": processed, 
            "total": total_items,
            "batch_size": batch_size,
            "processing_delay": processing_delay,
            "success": True
        }
    
    task_id = await task_manager.create_task()
    await task_manager.start_background_task(task_id, batch_task, ctx)
    
    resource_link = f"task://status/{task_id}"
    await ctx.info(f"Batch processing started. Track progress at: {resource_link}")
    
    return resource_link


@server.tool
async def start_ml_training(
    model_name: str,
    ctx: Context,
    dataset_size: int = 10000,
    epochs: int = 100
) -> str:
    """
    Simulates machine learning model training.
        
    Args:
        model_name: Name of the model to train
        dataset_size: Size of the dataset
        epochs: Number of training epochs
        ctx: MCP context
    
    Returns:
        Resource URI to track progress
    """
    await ctx.info(f"Starting training of model '{model_name}' with {dataset_size} samples by {epochs} epochs")
    
    async def training_task(task_id: str, context: Context, manager: DurableTaskManager):
        """Simulated ML training task."""
        for epoch in range(1, epochs + 1):
            # Simulate training of an epoch
            await asyncio.sleep(10)
            
            # Simulate training metrics
            loss = 1.0 - (epoch / epochs) * 0.8 + (epoch % 10) * 0.01
            accuracy = (epoch / epochs) * 0.95 + (epoch % 5) * 0.002
            
            progress = (epoch / epochs) * 100
            message = f"Epoch {epoch}/{epochs} - Loss: {loss:.4f}, Accuracy: {accuracy:.4f}"
            
            await manager.update_task_progress(task_id, progress, 100.0, message)
            await context.report_progress(epoch, epochs, message)
        
        await context.info(f"Model '{model_name}' training completed")
        
        return {
            "model_name": model_name,
            "dataset_size": dataset_size,
            "epochs_completed": epochs,
            "final_loss": loss,
            "final_accuracy": accuracy,
            "success": True,
            "training_time_seconds": epochs * 0.5
        }
    
    task_id = await task_manager.create_task()
    await task_manager.start_background_task(task_id, training_task, ctx)
    
    resource_link = f"task://status/{task_id}"
    await ctx.info(f"Training started. Track progress at: {resource_link}")
    
    return resource_link


@server.tool
async def cancel_task(task_id: str, ctx: Context) -> str:
    """
    Cancels an in-progress task.
    
    Args:
        task_id: ID of the task to cancel
        ctx: MCP context
    
    Returns:
        Status message of the cancellation
    """
    success = await task_manager.cancel_task(task_id)
    if success:
        await ctx.info(f"Task {task_id} cancelled successfully")
        return f"Task {task_id} cancelled. Status available at: task://status/{task_id}"
    else:
        await ctx.warning(f"Task {task_id} not found or cannot be cancelled")
        return f"Task {task_id} not found or cannot be cancelled"


@server.tool
async def get_server_stats(ctx: Context) -> Dict[str, Any]:
    """
    Gets durability server statistics.
    
    Args:
        ctx: MCP context
    
    Returns:
        Server statistics
    """
    all_tasks = await task_manager.list_tasks()
    
    stats = {
        "total_tasks": len(all_tasks),
        "running_tasks": len([t for t in all_tasks if t.status == TaskStatus.RUNNING]),
        "completed_tasks": len([t for t in all_tasks if t.status == TaskStatus.COMPLETED]),
        "failed_tasks": len([t for t in all_tasks if t.status == TaskStatus.FAILED]),
        "cancelled_tasks": len([t for t in all_tasks if t.status == TaskStatus.CANCELLED]),
        "pending_tasks": len([t for t in all_tasks if t.status == TaskStatus.PENDING]),
        "active_background_tasks": len(task_manager._background_tasks),
    }
    
    await ctx.info(f"Server statistics: {stats['total_tasks']} total tasks, {stats['running_tasks']} running")
    
    return stats


if __name__ == "__main__":
    print("Durability MCP server started")
    print("Available tools:")
    print("  - start_data_migration: Starts data migration")
    print("  - start_batch_processing: Starts batch processing")
    print("  - start_ml_training: Simulates ML training")
    print("  - cancel_task: Cancels a task")
    print("  - get_server_stats: Gets server statistics")
    print("\nResources available:")
    print("  - task://status/{task_id}: Specific task status")
    print("  - task://list: Lists all tasks")
    print("  - task://list/{status}: Lists tasks by status")
    
    server.run(transport="http", host="127.0.0.1", port=8080)