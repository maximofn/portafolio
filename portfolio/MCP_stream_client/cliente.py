#!/usr/bin/env python3
"""
MCP client for streaming and partial results.
Shows how to receive and handle partial results from the server.
"""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

@dataclass
class ProgressUpdate:
    """Represents a progress update."""
    progress: float
    total: float
    message: str
    percentage: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass  
class TaskResult:
    """Represents the result of a task."""
    task_name: str
    result: Dict[str, Any]
    progress_updates: List[ProgressUpdate]
    duration: float
    success: bool
    error_message: Optional[str] = None


class StreamingProgressHandler:
    """Handles streaming progress in a visual way."""
    
    def __init__(self, task_name: str):
        self.task_name = task_name
        self.progress_updates: List[ProgressUpdate] = []
        self.start_time = time.time()
        
    async def __call__(self, progress: float, total: float, message: str):
        """Callback called when there are progress updates."""
        percentage = (progress / total) * 100 if total > 0 else 0
        
        update = ProgressUpdate(
            progress=progress,
            total=total,
            message=message,
            percentage=percentage
        )
        self.progress_updates.append(update)
        
        # Display progress visually
        self._display_progress(update)
    
    def _display_progress(self, update: ProgressUpdate):
        """Display progress visually."""
        bar_length = 30
        filled_length = int(bar_length * update.percentage / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        elapsed = time.time() - self.start_time

        print(f"\t📊 {self.task_name}: |{bar}| {update.percentage:.1f}% "
              f"({update.progress:.0f}/{update.total:.0f}) - "
              f"{update.message} [{elapsed:.1f}s]")
        
        if update.progress >= update.total:
            print()  # New line when complete


class MCPStreamingClient:
    """MCP client with streaming capabilities."""
    
    def __init__(self, server_url: str = "http://localhost:8000/mcp/"):
        self.server_url = server_url
        self.transport = None
        self.client = None
        
    async def __aenter__(self):
        """Initialize connection to the server."""
            
        self.transport = StreamableHttpTransport(
            url=self.server_url,
            sse_read_timeout=60.0  # Timeout for streaming
        )
        
        self.client = Client(transport=self.transport)
        await self.client.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close connection."""
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def test_connection(self) -> bool:
        """Test connection to the server."""
        try:
            if not self.client:
                print(f"❌ Client not initialized")
                return False
                
            result = await self.client.ping()
            print(f"✅ Connection established with the server")
            return True
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    async def call_streaming_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        progress_callback: Optional[Callable] = None
    ) -> TaskResult:
        """Call a tool with progress handling."""
        start_time = time.time()
        
        try:
            if not self.client:
                raise Exception("Client not initialized")
                
            print(f"Executing {tool_name} tool:")
            
            result = await self.client.call_tool(
                tool_name,
                parameters,
                progress_handler=progress_callback
            )
            
            duration = time.time() - start_time
            
            # FastMCP returns a CallToolResult object with content attribute
            result_data = result.content if hasattr(result, 'content') else result
            
            # If result_data is a list of TextContent, extract the text
            if isinstance(result_data, list) and len(result_data) > 0:
                # Handle list of TextContent objects
                if hasattr(result_data[0], 'text'):
                    result_data = result_data[0].text
            
            # If result_data is string, try to parse it as JSON
            if isinstance(result_data, str):
                try:
                    result_data = json.loads(result_data)
                except json.JSONDecodeError:
                    result_data = {"output": result_data}
            
            return TaskResult(
                task_name=tool_name,
                result=result_data,
                progress_updates=getattr(progress_callback, 'progress_updates', []),
                duration=duration,
                success=True
            )
            
        except Exception as e:
            duration = time.time() - start_time
            
            return TaskResult(
                task_name=tool_name,
                result={},
                progress_updates=getattr(progress_callback, 'progress_updates', []),
                duration=duration,
                success=False,
                error_message=str(e)
            )
    
    async def list_available_tools(self) -> List[str]:
        """List available tools on the server."""
        try:
            if not self.client:
                print(f"❌ Client not initialized")
                return []
                
            tools = await self.client.list_tools()
            # FastMCP returns a list of tools directly
            if isinstance(tools, list):
                return [tool.name for tool in tools]
            # If it has attribute tools
            elif hasattr(tools, 'tools'):
                return [tool.name for tool in tools.tools]
            else:
                return []
        except Exception as e:
            print(f"❌ Error listing tools: {e}")
            return []


async def demo_long_running_task(client: MCPStreamingClient) -> TaskResult:
    """Demo of long running task with progress."""
    print("\n" + "="*60)
    print("📋 DEMO: Long Running Task with Progress")
    print("="*60)
    
    progress_handler = StreamingProgressHandler("Long Running Task")
    
    result = await client.call_streaming_tool(
        "long_running_task",
        {"name": "Data Processing", "steps": 8},
        progress_callback=progress_handler
    )
    
    if result.success:
        print(f"✅ Task completed in {result.duration:.2f}s")
        print(f"📊 Progress updates received: {len(result.progress_updates)}")
        # Safe handling of the result
        status = result.result.get('status', 'N/A') if isinstance(result.result, dict) else 'N/A'
        print(f"📋 Result: {status}")
    else:
        print(f"❌ Task failed: {result.error_message}")
    
    return result


async def demo_data_processing(client: MCPStreamingClient) -> TaskResult:
    """Demo of data processing."""
    print("\n" + "="*60)
    print("💾 DEMO: Data Processing")
    print("="*60)
    
    progress_handler = StreamingProgressHandler("Procesamiento")
    
    result = await client.call_streaming_tool(
        "streaming_data_processor",
        {"data_size": 50},
        progress_callback=progress_handler
    )
    
    if result.success:
        print(f"✅ Processing completed in {result.duration:.2f}s")
        # Safe handling of the result
        total = result.result.get('total_processed', 0) if isinstance(result.result, dict) else 0
        print(f"📊 Processed elements: {total}")
    else:
        print(f"❌ Processing failed: {result.error_message}")
    
    return result


async def demo_file_upload(client: MCPStreamingClient) -> TaskResult:
    """Demo of file upload."""
    print("\n" + "="*60)
    print("📤 DEMO: File Upload")
    print("="*60)
    
    progress_handler = StreamingProgressHandler("File Upload")
    
    result = await client.call_streaming_tool(
        "file_upload_simulation",
        {"file_count": 3},
        progress_callback=progress_handler
    )
    
    if result.success:
        print(f"✅ Upload completed in {result.duration:.2f}s")
        # Safe handling of the result
        count = result.result.get('uploaded_count', 0) if isinstance(result.result, dict) else 0
        print(f"📁 Uploaded files: {count}")
    else:
        print(f"❌ Upload failed: {result.error_message}")
    
    return result


async def demo_realtime_monitoring(client: MCPStreamingClient) -> TaskResult:
    """Demo of real-time monitoring."""
    print("\n" + "="*60)
    print("📡 DEMO: Real-time Monitoring")
    print("="*60)
    
    progress_handler = StreamingProgressHandler("Monitoring")
    
    result = await client.call_streaming_tool(
        "realtime_monitoring",
        {"duration_seconds": 20},
        progress_callback=progress_handler
    )
    
    if result.success:
        print(f"✅ Monitoring completed in {result.duration:.2f}s")
        # Safe handling of the result
        if isinstance(result.result, dict):
            print(f"📊 Average CPU: {result.result.get('avg_cpu', 0)}%")
            print(f"💾 Average memory: {result.result.get('avg_memory', 0)}%")
        else:
            print(f"📊 Result: {result.result}")
    else:
        print(f"❌ Monitoring failed: {result.error_message}")
    
    return result


def print_summary(results: List[TaskResult]):
    """Print summary of all tasks."""
    print("\n" + "="*100)
    print("📈 EXECUTION SUMMARY")
    print("="*100)
    
    for result in results:
        status = "\t✅ SUCCESS" if result.success else "\t❌ FAILURE"
        print(f"{status} {result.task_name}: {result.duration:.2f}s "
              f"({len(result.progress_updates)} updates)")
    
    total_time = sum(r.duration for r in results)
    successful = len([r for r in results if r.success])
    
    print(f"\n📊 Total: {successful}/{len(results)} successful tasks")
    print(f"⏱️  Total time: {total_time:.2f}s")


async def run_streaming_demo():
    """Run complete streaming client demo."""
    print("MCP Streaming Client")
    print("="*100)
    
    try:
        async with MCPStreamingClient() as client:
            # Test connection
            if not await client.test_connection():
                print("❌ Could not connect to the server. Make sure it's running.")
                return
            
            # List tools
            tools = await client.list_available_tools()
            print("🔧 Available tools:")
            for tool in tools:
                print(f"\t * {tool}")
            
            # Run demos
            results = []
            
            # Demo 1: Long running task
            result1 = await demo_long_running_task(client)
            results.append(result1)
            
            await asyncio.sleep(1)  # Pause between demos
            
            # Demo 2: Data processing  
            result2 = await demo_data_processing(client)
            results.append(result2)
            
            await asyncio.sleep(1)
            
            # Demo 3: File upload
            result3 = await demo_file_upload(client)
            results.append(result3)
            
            await asyncio.sleep(1)
            
            # Demo 4: Real-time monitoring
            result4 = await demo_realtime_monitoring(client)
            results.append(result4)
            
            # Final summary
            print_summary(results)
            
    except Exception as e:
        print(f"❌ Error in the demo: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(run_streaming_demo())
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by the user")
    except Exception as e:
        print(f"❌ Error running demo: {e}")