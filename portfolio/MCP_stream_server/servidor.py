#!/usr/bin/env python3
"""
MCP server for streaming and partial results.
Shows how to send real-time progress updates to the client.
"""

import asyncio
import uvicorn
from typing import Dict, List, Any
from fastmcp import FastMCP, Context
from fastmcp.server.http import create_streamable_http_app


# Create MCP server instance
mcp = FastMCP(
    name="Streaming Server",
    instructions="Streaming Server with real-time progress updates"
)


@mcp.tool
async def long_running_task(
    name: str = "Task", 
    steps: int = 10,
    context: Context = None
) -> Dict[str, Any]:
    """
    Long running task with real-time progress updates.
    
    Args:
        name: Task name
        steps: Number of steps to execute
    """
    if context:
        await context.info(f"🚀 Initializing {name} with {steps} steps...")
    
    results = []
    
    for i in range(steps):
        # Simulate work
        await asyncio.sleep(1)
        
        # Create partial result
        partial_result = f"Step {i + 1}: Processed {name}"
        results.append(partial_result)
        
        # Report progress
        if context:
            await context.report_progress(
                progress=i + 1,
                total=steps,
                message=f"Step {i + 1}/{steps} - {partial_result}"
            )
            
            await context.debug(f"✅ {partial_result}")
    
    if context:
        await context.info(f"🎉 {name} completed successfully!")
    
    return {
        "task_name": name,
        "steps_completed": steps,
        "results": results,
        "status": "completed"
    }


@mcp.tool
async def streaming_data_processor(
    data_size: int = 100,
    context: Context = None
) -> Dict[str, Any]:
    """
    Processes data sending real-time progress updates.
    
    Args:
        data_size: Number of data items to process
    """
    if context:
        await context.info(f"📊 Procesando {data_size} elementos de datos...")
    
    processed = []
    batch_size = max(1, data_size // 10)  # Process in batches
    
    for i in range(0, data_size, batch_size):
        batch_end = min(i + batch_size, data_size)
        
        # Simulate batch processing
        await asyncio.sleep(0.5)
        
        # Process batch
        batch_results = [f"item_{j}" for j in range(i, batch_end)]
        processed.extend(batch_results)
        
        # Report progress
        if context:
            progress = len(processed)
            await context.report_progress(
                progress=progress,
                total=data_size,
                message=f"Processed {progress}/{data_size} items"
            )
            
            await context.debug(f"Batch processed: {i}-{batch_end-1}")
    
    if context:
        await context.info(f"✅ Processing completed: {len(processed)} items")
    
    return {
        "total_processed": len(processed),
        "processed_items": processed[:10],  # Show first 10 items
        "status": "completed"
    }


@mcp.tool
async def file_upload_simulation(
    file_count: int = 5,
    context: Context = None
) -> Dict[str, Any]:
    """
    Simulates file upload with progress updates.
    
    Args:
        file_count: Number of files to upload
    """
    if context:
        await context.info(f"📤 Starting upload of {file_count} files...")
    
    uploaded_files = []
    
    for i in range(file_count):
        file_name = f"file_{i+1}.dat"
        
        if context:
            await context.info(f"Uploading {file_name}...")
        
        # Simulate upload by chunks
        chunks = 10
        for chunk in range(chunks):
            await asyncio.sleep(0.2)  # Simulate upload time
            
            if context:
                await context.report_progress(
                    progress=(i * chunks) + chunk + 1,
                    total=file_count * chunks,
                    message=f"Uploading {file_name} - chunk {chunk+1}/{chunks}"
                )
        
        uploaded_files.append({
            "name": file_name,
            "size": f"{(i+1) * 1024} KB",
            "status": "uploaded"
        })
        
        if context:
            await context.debug(f"✅ {file_name} uploaded successfully")
    
    if context:
        await context.info(f"🎉 Upload completed: {len(uploaded_files)} files")
    
    return {
        "uploaded_count": len(uploaded_files),
        "files": uploaded_files,
        "total_size": sum(int(f["size"].split()[0]) for f in uploaded_files),
        "status": "completed"
    }


@mcp.tool
async def realtime_monitoring(
    duration_seconds: int = 30,
    context: Context = None
) -> Dict[str, Any]:
    """
    Real-time monitoring with periodic updates.
    
    Args:
        duration_seconds: Monitoring duration in seconds
    """
    if context:
        await context.info(f"📡 Starting monitoring for {duration_seconds} seconds...")
    
    metrics = []
    interval = 2  # Update every 2 seconds
    total_intervals = duration_seconds // interval
    
    for i in range(total_intervals):
        # Simulate metrics
        import random
        cpu_usage = random.randint(20, 80)
        memory_usage = random.randint(40, 90)
        network_io = random.randint(100, 1000)
        
        metric = {
            "timestamp": i * interval,
            "cpu": cpu_usage,
            "memory": memory_usage,
            "network_io": network_io
        }
        metrics.append(metric)
        
        if context:
            await context.report_progress(
                progress=i + 1,
                total=total_intervals,
                message=f"Monitoring active - CPU: {cpu_usage}%, MEM: {memory_usage}%, NET: {network_io}KB/s"
            )
            
            await context.debug(f"Metrics collected: interval {i+1}")
        
        await asyncio.sleep(interval)
    
    if context:
        await context.info(f"📊 Monitoring completed: {len(metrics)} data points")
    
    avg_cpu = sum(m["cpu"] for m in metrics) / len(metrics)
    avg_memory = sum(m["memory"] for m in metrics) / len(metrics)
    
    return {
        "duration": duration_seconds,
        "data_points": len(metrics),
        "avg_cpu": round(avg_cpu, 2),
        "avg_memory": round(avg_memory, 2),
        "metrics": metrics,
        "status": "completed"
    }


async def run_streaming_server(host: str = "127.0.0.1", port: int = 8000):
    """Run the streaming server."""
    print(f"🚀 Starting MCP streaming server on {host}:{port}")
    
    # Create Starlette application with streaming support
    app = create_streamable_http_app(
        server=mcp,
        streamable_http_path="/mcp/",
        stateless_http=False,  # Keep session state
        debug=True
    )
    
    # Configure uvicorn
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="info",
        access_log=False
    )
    
    # Run server
    server = uvicorn.Server(config)
    print(f"✅ Server ready at http://{host}:{port}/mcp/")
    print("📡 Available tools:")
    print("  - long_running_task: Long running task with progress")
    print("  - streaming_data_processor: Data processing")
    print("  - file_upload_simulation: File upload simulation")
    print("  - realtime_monitoring: Real-time monitoring")
    
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(run_streaming_server())
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
    except Exception as e:
        print(f"❌ Error running server: {e}")