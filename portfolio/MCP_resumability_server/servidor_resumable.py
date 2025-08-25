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


# @mcp.tool
# async def large_file_download(
#     file_url: str = "https://example.com/large_file.zip",
#     file_size_mb: int = 1000,
#     chunk_size_mb: int = 50,
#     client_id: str = None,  # Add persistent client_id
#     context: Context = None
# ) -> Dict[str, Any]:
#     """
#     Simulate large file download with resumability.
    
#     Args:
#         file_url: URL of the file to download
#         file_size_mb: Size of the file in MB
#         chunk_size_mb: Size of the chunk in MB
#         client_id: Persistent client id for resumability
#     """
#     if not context:
#         return {"error": "Requires context for resumability"}
    
#     # Use persistent client id if available, otherwise use session_id
#     persistent_id = client_id if client_id else context.session_id
#     if not persistent_id:
#         return {"error": "Requires client_id or session_id for resumability"}
    
#     task_name = "large_file_download"
#     parameters = {
#         "file_url": file_url,
#         "file_size_mb": file_size_mb,
#         "chunk_size_mb": chunk_size_mb
#     }
    
#     total_chunks = (file_size_mb + chunk_size_mb - 1) // chunk_size_mb
    
#     # Search for existing download - include interrupted tasks
#     task_id = checkpoint_manager.generate_task_id(persistent_id, task_name, parameters)
#     existing_checkpoint = checkpoint_manager.get_checkpoint(task_id)
    
#     if existing_checkpoint and existing_checkpoint.current_step > 0:
#         # Resume download from where it left off
#         await context.info(f"🔄 Reanudando descarga desde chunk {existing_checkpoint.current_step}/{total_chunks}")
#         start_chunk = existing_checkpoint.current_step
#         downloaded_chunks = checkpoint_manager.load_task_data(task_id) or []
        
#         checkpoint_manager.update_checkpoint(
#             task_id, start_chunk, TaskStatus.RUNNING
#         )
#     else:
#         # New download
#         await context.info(f"🆕 Iniciando descarga: {file_url} ({file_size_mb} MB)")
#         if not existing_checkpoint:
#             task_id = checkpoint_manager.create_checkpoint(
#                 persistent_id, task_name, parameters, total_chunks
#             )
#         start_chunk = 0
#         downloaded_chunks = []
        
#         checkpoint_manager.update_checkpoint(
#             task_id, 0, TaskStatus.RUNNING
#         )
    
#     try:
#         # Download chunks
#         for chunk_num in range(start_chunk, total_chunks):
#             # Simulate chunk download
#             await asyncio.sleep(0.8)  # Simulate download time
            
#             chunk_start = chunk_num * chunk_size_mb
#             chunk_end = min(chunk_start + chunk_size_mb, file_size_mb)
#             actual_chunk_size = chunk_end - chunk_start
            
#             chunk_info = {
#                 "chunk_num": chunk_num,
#                 "start_byte": chunk_start * 1024 * 1024,
#                 "end_byte": chunk_end * 1024 * 1024 - 1,
#                 "size_mb": actual_chunk_size,
#                 "downloaded_at": f"step_{chunk_num}"
#             }
#             downloaded_chunks.append(chunk_info)
            
#             # Checkpoint for each chunk
#             checkpoint_manager.update_checkpoint(
#                 task_id,
#                 chunk_num + 1,
#                 TaskStatus.RUNNING,
#                 {"last_chunk": chunk_info}
#             )
            
#             checkpoint_manager.save_task_data(task_id, downloaded_chunks)
            
#             # Progress
#             progress_mb = sum(c["size_mb"] for c in downloaded_chunks)
#             await context.report_progress(
#                 progress=chunk_num + 1,
#                 total=total_chunks,
#                 message=f"Downloaded {progress_mb:.1f}/{file_size_mb} MB (chunk {chunk_num + 1}/{total_chunks})"
#             )
            
#             await context.debug(f"Chunk {chunk_num + 1} downloaded: {actual_chunk_size} MB")
        
#         # Completed
#         checkpoint_manager.update_checkpoint(
#             task_id, total_chunks, TaskStatus.COMPLETED
#         )
        
#         total_downloaded = sum(c["size_mb"] for c in downloaded_chunks)
#         await context.info(f"✅ Download completed: {total_downloaded} MB")
        
#         return {
#             "task_id": task_id,
#             "file_url": file_url,
#             "total_chunks": len(downloaded_chunks),
#             "total_size_mb": total_downloaded,
#             "chunks": downloaded_chunks[-3:],  # Last 3 chunks
#             "status": "completed"
#         }
        
#     except Exception as e:
#         checkpoint_manager.update_checkpoint(
#             task_id, chunk_num, TaskStatus.FAILED, error_message=str(e)
#         )
#         await context.error(f"❌ Error in download: {e}")
#         raise


# @mcp.tool
# async def machine_learning_training(
#     model_name: str = "neural_network",
#     total_epochs: int = 100,
#     batch_size: int = 32,
#     client_id: str = None,  # Add persistent client_id
#     context: Context = None
# ) -> Dict[str, Any]:
#     """
#     Simulate machine learning training with resumability and checkpoints.
    
#     Args:
#         model_name: Name of the model to train
#         total_epochs: Total epochs of training
#         batch_size: Size of the batch
#         client_id: Persistent client id for resumability
#     """
#     if not context:
#         return {"error": "Requires context for resumability"}
    
#     # Use persistent client id if available, otherwise use session_id
#     persistent_id = client_id if client_id else context.session_id
#     if not persistent_id:
#         return {"error": "Requires client_id or session_id for resumability"}
    
#     task_name = "machine_learning_training"
#     parameters = {
#         "model_name": model_name,
#         "total_epochs": total_epochs,
#         "batch_size": batch_size
#     }
    
#     # Search for existing training - include interrupted tasks
#     task_id = checkpoint_manager.generate_task_id(persistent_id, task_name, parameters)
#     existing_checkpoint = checkpoint_manager.get_checkpoint(task_id)
    
#     if existing_checkpoint and existing_checkpoint.current_step > 0:
#         # Resume training from where it left off
#         await context.info(f"🔄 Resume training from epoch {existing_checkpoint.current_step}")
#         start_epoch = existing_checkpoint.current_step
#         training_history = checkpoint_manager.load_task_data(task_id) or []
        
#         checkpoint_manager.update_checkpoint(
#             task_id, start_epoch, TaskStatus.RUNNING
#         )
#     else:
#         # New training
#         await context.info(f"🆕 Starting training: {model_name} ({total_epochs} epochs)")
#         if not existing_checkpoint:
#             task_id = checkpoint_manager.create_checkpoint(
#                 persistent_id, task_name, parameters, total_epochs,
#                 {"model_config": {"name": model_name, "batch_size": batch_size}}
#             )
#         start_epoch = 0
#         training_history = []
        
#         checkpoint_manager.update_checkpoint(
#             task_id, 0, TaskStatus.RUNNING
#         )
    
#     try:
#         # Train epochs
#         for epoch in range(start_epoch, total_epochs):
#             # Simulate epoch training
#             await asyncio.sleep(0.5)
            
#             # Simulated metrics
#             loss = max(0.1, 2.0 * (1 - epoch / total_epochs) + random.uniform(-0.1, 0.1))
#             accuracy = min(0.99, epoch / total_epochs * 0.9 + random.uniform(-0.05, 0.05))
            
#             epoch_result = {
#                 "epoch": epoch + 1,
#                 "loss": round(loss, 4),
#                 "accuracy": round(accuracy, 4),
#                 "learning_rate": 0.001 * (0.95 ** (epoch // 10))
#             }
#             training_history.append(epoch_result)
            
#             # Checkpoint for each epoch
#             checkpoint_manager.update_checkpoint(
#                 task_id,
#                 epoch + 1,
#                 TaskStatus.RUNNING,
#                 {"last_epoch": epoch_result}
#             )
            
#             checkpoint_manager.save_task_data(task_id, training_history)
            
#             # Progress
#             await context.report_progress(
#                 progress=epoch + 1,
#                 total=total_epochs,
#                 message=f"Epoch {epoch + 1}/{total_epochs} - Loss: {loss:.4f}, Acc: {accuracy:.4f}"
#             )
            
#             await context.debug(f"Epoch {epoch + 1} completed")
        
#         # Completed
#         checkpoint_manager.update_checkpoint(
#             task_id, total_epochs, TaskStatus.COMPLETED
#         )
        
#         final_accuracy = training_history[-1]["accuracy"] if training_history else 0
#         await context.info(f"✅ Training completed - Final accuracy: {final_accuracy:.4f}")
        
#         return {
#             "task_id": task_id,
#             "model_name": model_name,
#             "total_epochs": len(training_history),
#             "final_accuracy": final_accuracy,
#             "final_loss": training_history[-1]["loss"] if training_history else 0,
#             "history": training_history[-5:],  # Last 5 epochs
#             "status": "completed"
#         }
        
#     except Exception as e:
#         checkpoint_manager.update_checkpoint(
#             task_id, epoch, TaskStatus.FAILED, error_message=str(e)
#         )
#         await context.error(f"❌ Error in training: {e}")
#         raise


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