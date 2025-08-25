#!/usr/bin/env python3
"""
Server MCP with resumability and checkpoints.
Demo how to implement tasks that can be paused and resumed.
"""

import asyncio
import uvicorn
import random
from typing import Dict, List, Optional, Any
from fastmcp import FastMCP, Context
from fastmcp.server.http import create_streamable_http_app
from checkpoint_manager import checkpoint_manager, TaskStatus, TaskCheckpoint


# Create instance of the MCP server
mcp = FastMCP(
    name="Resumable Server",
    instructions="MCP server with resumability and checkpoints for long tasks"
)


@mcp.tool
async def resumable_data_processing(
    dataset_name: str = "default_dataset",
    total_records: int = 100,
    batch_size: int = 10,
    client_id: str = None,  # Add persistent client_id
    context: Context = None
) -> Dict[str, Any]:
    """
    Resumable data processing with automatic checkpoints.
    
    Args:
        dataset_name: Name of the dataset to process
        total_records: Total records to process
        batch_size: Size of the batch per iteration
        client_id: Persistent client id for resumability
    """
    if not context:
        return {"error": "Requires context for resumability"}
    
    # Use persistent client id if available, otherwise use session_id
    persistent_id = client_id if client_id else context.session_id
    if not persistent_id:
        return {"error": "Requires client_id or session_id for resumability"}
    
    task_name = "resumable_data_processing"
    parameters = {
        "dataset_name": dataset_name,
        "total_records": total_records,
        "batch_size": batch_size
    }
    
    # Search for existing task to resume - include interrupted tasks
    task_id = checkpoint_manager.generate_task_id(persistent_id, task_name, parameters)
    existing_checkpoint = checkpoint_manager.get_checkpoint(task_id)
    
    if existing_checkpoint and existing_checkpoint.current_step > 0:
        # Resume from checkpoint
        await context.info(f"🔄 Resuming processing from record {existing_checkpoint.current_step}")
        start_record = existing_checkpoint.current_step
        processed_data = checkpoint_manager.load_task_data(task_id) or []
        
        # Mark as running
        checkpoint_manager.update_checkpoint(
            task_id, start_record, TaskStatus.RUNNING
        )
    else:
        # New task
        await context.info(f"🆕 Starting new processing of {total_records} records")
        if not existing_checkpoint:
            task_id = checkpoint_manager.create_checkpoint(
                persistent_id, task_name, parameters, total_records
            )
        start_record = 0
        processed_data = []
        
        # Mark as running
        checkpoint_manager.update_checkpoint(
            task_id, 0, TaskStatus.RUNNING
        )
    
    try:
        # Process in batches
        for record_num in range(start_record, total_records, batch_size):
            batch_end = min(record_num + batch_size, total_records)
            
            # Simulate batch processing
            await asyncio.sleep(1)  # Simulate work
            
            # Process batch
            batch_results = []
            for i in range(record_num, batch_end):
                # Simulate record processing
                result = {
                    "record_id": f"{dataset_name}_{i:06d}",
                    "processed_at": f"step_{i}",
                    "value": random.randint(1, 1000)
                }
                batch_results.append(result)
            
            processed_data.extend(batch_results)
            
            # Save checkpoint for each batch
            checkpoint_manager.update_checkpoint(
                task_id,
                batch_end,
                TaskStatus.RUNNING,
                {"last_batch": batch_results}
            )
            
            # Save processed data
            checkpoint_manager.save_task_data(task_id, processed_data)
            
            # Report progress
            await context.report_progress(
                progress=batch_end,
                total=total_records,
                message=f"Processed {batch_end}/{total_records} records"
            )
            
            await context.debug(f"Batch {record_num}-{batch_end-1} completed")
        
        # Mark as completed
        checkpoint_manager.update_checkpoint(
            task_id, total_records, TaskStatus.COMPLETED
        )
        
        await context.info(f"✅ Processing completed: {len(processed_data)} records")
        
        return {
            "task_id": task_id,
            "dataset_name": dataset_name,
            "total_processed": len(processed_data),
            "records": processed_data[:5],  # Show first 5
            "status": "completed"
        }
        
    except Exception as e:
        # Mark as failed
        checkpoint_manager.update_checkpoint(
            task_id, record_num, TaskStatus.FAILED, error_message=str(e)
        )
        
        await context.error(f"❌ Error in processing: {e}")
        raise


@mcp.tool
async def pause_task(
    task_id: str,
    context: Context = None
) -> Dict[str, str]:
    """
    Pause a task in execution.
    
    Args:
        task_id: ID of the task to pause
    """
    checkpoint = checkpoint_manager.get_checkpoint(task_id)
    if not checkpoint:
        return {"error": f"Task {task_id} not found"}
    
    if checkpoint.status != TaskStatus.RUNNING:
        return {"error": f"Task {task_id} is not running"}
    
    success = checkpoint_manager.update_checkpoint(
        task_id, checkpoint.current_step, TaskStatus.PAUSED
    )
    
    if success:
        if context:
            await context.info(f"⏸️ Task {task_id} paused")
        return {"message": f"Task {task_id} paused correctly"}
    else:
        return {"error": f"Could not pause task {task_id}"}


@mcp.tool
async def list_session_tasks(
    client_id: str = None,  # Add persistent client_id
    context: Context = None
) -> Dict[str, Any]:
    """
    List all tasks of the current session or the specified client.
    
    Args:
        client_id: Persistent client id (optional)
    """
    if not context:
        return {"error": "Requires context"}
    
    # Use persistent client id if available, otherwise use session_id
    persistent_id = client_id if client_id else context.session_id
    if not persistent_id:
        return {"error": "Requires client_id or session_id"}
    
    checkpoints = checkpoint_manager.get_session_checkpoints(persistent_id)
    
    tasks = []
    for checkpoint in checkpoints:
        task_info = {
            "task_id": checkpoint.task_id,
            "task_name": checkpoint.task_name,
            "status": checkpoint.status.value,
            "progress": f"{checkpoint.current_step}/{checkpoint.total_steps}",
            "progress_percent": round((checkpoint.current_step / checkpoint.total_steps) * 100, 1) if checkpoint.total_steps > 0 else 0,
            "created_at": checkpoint.created_at.isoformat(),
            "updated_at": checkpoint.updated_at.isoformat()
        }
        tasks.append(task_info)
    
    return {
        "session_id": context.session_id,
        "persistent_id": persistent_id,
        "total_tasks": len(tasks),
        "tasks": tasks
    }


@mcp.tool
async def get_checkpoint_stats(context: Context = None) -> Dict[str, Any]:
    """
    Get global checkpoint statistics.
    """
    stats = checkpoint_manager.get_stats()
    
    return {
        "checkpoint_stats": stats,
        "total_checkpoints": sum(stats.values())
    }


@mcp.tool
async def get_session_info(context: Context = None) -> Dict[str, Any]:
    """
    Get information about the current session.
    """
    if not context:
        return {"error": "No context available"}
    
    return {
        "session_id": context.session_id,
        "request_id": context.request_id,
        "client_id": context.client_id
    }


async def run_resumable_server(host: str = "127.0.0.1", port: int = 8001):
    """Run server with resumability capabilities."""
    print(f"🚀 Starting MCP server with resumability at {host}:{port}")
    
    # Create application
    app = create_streamable_http_app(
        server=mcp,
        streamable_http_path="/mcp/",
        stateless_http=False,  # IMPORTANT: stateful for sessions
        debug=True
    )
    
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="info",
        access_log=False
    )
    
    server = uvicorn.Server(config)
    print(f"✅ Resumable server ready at http://{host}:{port}/mcp/")
    print("🔧 Tools with resumability:")
    print("  - resumable_data_processing: Processing with checkpoints")
    # print("  - large_file_download: Download resumable")
    # print("  - machine_learning_training: ML training resumable")
    print("  - pause_task: Pause tasks")
    print("  - list_session_tasks: List session tasks")
    print("  - get_checkpoint_stats: Checkpoint statistics")
    print("  - get_session_info: Current session information")
    
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(run_resumable_server())
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
    except Exception as e:
        print(f"❌ Error running server: {e}")