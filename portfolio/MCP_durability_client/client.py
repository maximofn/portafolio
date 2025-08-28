"""
Durability MCP client

Client that demonstrates how to interact with an MCP server that implements durability.

Shows how to:
1. Start long-running tasks
2. Monitor progress using resource polling
3. Subscribe to status updates (simulated)
4. Handle persistent tasks that survive server restarts


Usage:
    python client.py
"""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

import argparse


class DurabilityClient:
    """Client that demonstrates durability patterns with MCP."""
    
    def __init__(self, server_command: List[str]):
        """
        Initializes the durability client.
        
        Args:
            server_command: Command to execute the MCP server
        """
        self.server_command = server_command
        self._polling_tasks: Dict[str, asyncio.Task] = {}
    
    async def connect(self) -> Client:
        """Creates and connects the client to the server."""
        transport = StreamableHttpTransport(
            url="http://127.0.0.1:8080/mcp"
        )
        client = Client(transport)
        return client
    
    async def start_data_migration(
        self, 
        client: Client,
        source_path: str = "/data/source",
        destination_path: str = "/data/destination", 
        record_count: int = 1000
    ) -> str:
        """
        Starts a data migration task and returns the resource link.
        
        Args:
            client: MCP connected client
            source_path: Source path
            destination_path: Destination path
            record_count: Number of records to migrate
            
        Returns:
            Resource URI to track progress
        """
        print(f"🚀 Starting data migration: {record_count} records")
        print(f"   Source: {source_path}")
        print(f"   Destination: {destination_path}")
        
        result = await client.call_tool(
            "start_data_migration",
            {
                "source_path": source_path,
                "destination_path": destination_path,
                "record_count": record_count
            }
        )
        
        resource_uri = result.content[0].text
        print(f"✅ Task started. Resource URI: {resource_uri}")
        return resource_uri
    
    async def start_batch_processing(
        self,
        client: Client,
        batch_size: int = 50,
        total_items: int = 500,
        processing_delay: float = 0.3
    ) -> str:
        """
        Starts batch processing.
        
        Args:
            client: MCP connected client
            batch_size: Batch size
            total_items: Total items
            processing_delay: Processing delay
            
        Returns:
            Resource URI to track progress
        """
        print(f"🔄 Starting batch processing:")
        print(f"   Total items: {total_items}")
        print(f"   Batch size: {batch_size}")
        print(f"   Processing delay: {processing_delay}s")
        
        result = await client.call_tool(
            "start_batch_processing",
            {
                "batch_size": batch_size,
                "total_items": total_items,
                "processing_delay": processing_delay
            }
        )
        
        resource_uri = result.content[0].text
        print(f"✅ Batch processing started. Resource URI: {resource_uri}")
        return resource_uri
    
    async def start_ml_training(
        self,
        client: Client,
        model_name: str = "clasificador-texto",
        dataset_size: int = 5000,
        epochs: int = 50
    ) -> str:
        """
        Starts ML model training.
        
        Args:
            client: MCP connected client
            model_name: Model name
            dataset_size: Dataset size
            epochs: Number of epochs
            
        Returns:
            Resource URI to track progress
        """
        print(f"🤖 Starting ML training:")
        print(f"   Model: {model_name}")
        print(f"   Dataset size: {dataset_size} samples")
        print(f"   Epochs: {epochs}")
        
        result = await client.call_tool(
            "start_ml_training",
            {
                "model_name": model_name,
                "dataset_size": dataset_size,
                "epochs": epochs
            }
        )
        
        resource_uri = result.content[0].text
        print(f"✅ ML training started. Resource URI: {resource_uri}")
        return resource_uri
    
    async def get_task_status(self, client: Client, resource_uri: str) -> Dict[str, Any]:
        """
        Gets the current status of a task.
        
        Args:
            client: MCP connected client
            resource_uri: Resource URI of the task
            
        Returns:
            Current status of the task
        """
        try:
            result = await client.read_resource(resource_uri)
            
            # result should be a list of ReadResourceContents  
            if isinstance(result, list) and len(result) > 0:
                content_block = result[0]
                
                # The content is in the 'text' attribute
                if hasattr(content_block, 'text') and content_block.text:
                    return json.loads(content_block.text)
                else:
                    return {"error": f"No text found in the resource. Type: {type(content_block)}, text={getattr(content_block, 'text', None)}"}
            else:
                return {"error": "Empty resource"}
                
        except Exception as e:
            return {"error": f"Error reading resource: {str(e)}"}
    
    async def poll_task_until_complete(
        self, 
        client: Client, 
        resource_uri: str,
        poll_interval: float = 1.0,
        max_duration: float = 10.0
    ) -> Dict[str, Any]:
        """
        Polls a task until it completes or fails.
        
        Args:
            client: MCP connected client
            resource_uri: Resource URI of the task
            poll_interval: Interval between polls in seconds
            max_duration: Maximum duration of polling
            
        Returns:
            Final status of the task
        """
        task_id = resource_uri.split("/")[-1]
        print(f"📊 Monitoring task {task_id}...")
        
        start_time = time.time()
        last_progress = -1
        
        while time.time() - start_time < max_duration:
            status = await self.get_task_status(client, resource_uri)
            
            if "error" in status and status["error"] is not None:
                print(f"Error getting status: {status['error']}")
                return status
            
            current_status = status.get("status", "unknown")
            progress = status.get("progress", 0)
            message = status.get("message", "")
            
            # Show updates only if the progress changed
            if progress != last_progress:
                progress_bar = self._create_progress_bar(progress)
                print(f"   {progress_bar} {progress:5.1f}% | {current_status.upper()} | {message}")
                last_progress = progress
            
            # Check if the task is complete
            if current_status in ["completed", "failed", "cancelled"]:
                print(f"Task {current_status}: {task_id}")
                
                if current_status == "completed" and status.get("result_data"):
                    print("Results:")
                    self._print_results(status["result_data"])
                elif current_status == "failed" and status.get("error"):
                    print(f"Error: {status['error']}")
                
                return status
            
            await asyncio.sleep(poll_interval)
        
        print(f"Timeout for task {task_id}")
        return await self.get_task_status(client, resource_uri)
    
    def _create_progress_bar(self, progress: float, width: int = 20) -> str:
        """Creates a visual progress bar."""
        filled = int(width * progress / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def _print_results(self, result_data: Dict[str, Any], indent: int = 4) -> None:
        """Prints the results in a formatted way."""
        spaces = " " * indent
        for key, value in result_data.items():
            if isinstance(value, dict):
                print(f"{spaces}{key}:")
                self._print_results(value, indent + 2)
            elif isinstance(value, list):
                print(f"{spaces}{key}: {len(value)} items")
            else:
                print(f"{spaces}{key}: {value}")
    
    async def list_all_tasks(self, client: Client) -> Dict[str, Any]:
        """Lists all tasks on the server."""
        try:
            result = await client.read_resource("task://list")
            
            # result should be a list of ReadResourceContents  
            if isinstance(result, list) and len(result) > 0:
                content_block = result[0]
                # The content is in the 'text' attribute
                if hasattr(content_block, 'text') and content_block.text:
                    return json.loads(content_block.text)
                else:
                    return {"error": f"No text found in the resource. Type: {type(content_block)}"}
            else:
                return {"error": "Empty resource"}
                
        except Exception as e:
            return {"error": f"Error reading task list: {str(e)}"}
    
    async def list_tasks_by_status(self, client: Client, status: str) -> Dict[str, Any]:
        """Lists tasks filtered by status."""
        try:
            result = await client.read_resource(f"task://list/{status}")
            
            # result should be a list of ReadResourceContents  
            if isinstance(result, list) and len(result) > 0:
                content_block = result[0]
                # The content is in the 'text' attribute
                if hasattr(content_block, 'text') and content_block.text:
                    return json.loads(content_block.text)
                else:
                    return {"error": f"No text found in the resource. Type: {type(content_block)}"}
            else:
                return {"error": "Empty resource"}
                
        except Exception as e:
            return {"error": f"Error reading task list: {str(e)}"}
    
    async def print_task_list(self, client: Client) -> None:
        """Prints a formatted list of all tasks."""
        print("Task list:")
        
        task_list = await self.list_all_tasks(client)
        
        if "error" in task_list:
            print(f"   {task_list['error']}")
            return
        
        tasks = task_list.get("tasks", [])
        if not tasks:
            print("   No tasks")
            return
        
        for task in tasks:
            task_id = task["task_id"]
            status = task["status"].upper()
            progress = task.get("progress", 0)
            message = task.get("message", "")
            
            print(f"   ID: {task_id} | {status:9} | {progress:5.1f}% | {message}")
    
    async def select_task(self, client: Client) -> Optional[str]:
        """
        Shows a numbered list of tasks and allows the user to select one.
        
        Args:
            client: MCP connected client
            
        Returns:
            The ID of the selected task, or None if no task was selected
        """
        print("📋 Available tasks:")
        
        task_list = await self.list_all_tasks(client)
        
        if "error" in task_list:
            print(f"   ❌ {task_list['error']}")
            return None
        
        tasks = task_list.get("tasks", [])
        if not tasks:
            print("   No tasks available")
            return None
        
        # Show tasks with numbers
        for i, task in enumerate(tasks, 1):
            task_id = task["task_id"]
            status = task["status"].upper()
            progress = task.get("progress", 0)
            message = task.get("message", "")
            
            print(f"   {i}. ID: {task_id} | {status:9} | {progress:5.1f}% | {message}")
        
        # Ask user to select
        try:
            choice = input(f"\nSelect a task (1-{len(tasks)}) or press Enter to cancel: ").strip()
            
            if not choice:
                print("Selection cancelled")
                return None
                
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(tasks):
                selected_task = tasks[choice_num - 1]
                selected_id = selected_task["task_id"]
                print(f"✅ Selected task: {selected_id}")
                return selected_id
            else:
                print(f"❌ Invalid selection. Please choose between 1 and {len(tasks)}")
                return None
                
        except ValueError:
            print("❌ Invalid input. Please enter a number")
            return None
        except Exception as e:
            print(f"❌ Error selecting task: {str(e)}")
            return None
    
    async def cancel_task(self, client: Client, task_id: str) -> str:
        """Cancels a specific task."""
        try:
            result = await client.call_tool("cancel_task", {"task_id": task_id})
            response = result.content[0].text
            print(f"🚫 {response}")
            return response
        except Exception as e:
            error_msg = f"Error canceling task: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    async def get_server_stats(self, client: Client) -> Dict[str, Any]:
        """Gets server statistics."""
        try:
            result = await client.call_tool("get_server_stats", {})
            
            # result.content is a list of ContentBlock
            if hasattr(result, 'content') and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return json.loads(content.text)
                else:
                    # If not text, it may be the object directly
                    return content if isinstance(content, dict) else {"error": f"Unexpected format: {type(content)}"}
            else:
                return {"error": "Empty response from get_server_stats"}
                
        except Exception as e:
            return {"error": f"Error getting server statistics: {str(e)}"}
    
    async def print_server_stats(self, client: Client) -> None:
        """Prints server statistics."""
        print("📊 Server statistics:")
        
        stats = await self.get_server_stats(client)
        
        if "error" in stats:
            print(f"   ❌ {stats['error']}")
            return
        
        print(f"   Total tasks: {stats.get('total_tasks', 0)}")
        print(f"   Running: {stats.get('running_tasks', 0)}")
        print(f"   Completed: {stats.get('completed_tasks', 0)}")
        print(f"   Failed: {stats.get('failed_tasks', 0)}")
        print(f"   Cancelled: {stats.get('cancelled_tasks', 0)}")
        print(f"   Pending: {stats.get('pending_tasks', 0)}")
        print(f"   Active background tasks: {stats.get('active_background_tasks', 0)}")


async def interactive_demo(server_path: Optional[str] = None):
    """Interactive demo to explore the system."""
    print("🚀 Interactive Demo of the MCP Durability System")
    print("=" * 55)
    
    client_manager = DurabilityClient([])
    
    async with await client_manager.connect() as client:
        print("🔗 Connected to the durability server")
        
        while True:
            print("\n" + "=" * 40)
            print("Available options:")
            print("1. Start data migration")
            print("2. Start batch processing")
            print("3. Start ML training")
            print("4. View server statistics")
            print("5. View task list")
            print("6. Monitor specific task")
            print("7. Cancel task")
            print("8. Exit")
            
            try:
                choice = input("\nSelect an option (1-8): ").strip()
                
                if choice == "1":
                    records = int(input("Number of records to migrate (default 500): ") or "500")
                    uri = await client_manager.start_data_migration(client, record_count=records)
                    print(f"Task URI: {uri}")
                    
                elif choice == "2":
                    total = int(input("Total elements (default 300): ") or "300")
                    batch_size = int(input("Batch size (default 30): ") or "30")
                    uri = await client_manager.start_batch_processing(client, total_items=total, batch_size=batch_size)
                    print(f"Task URI: {uri}")
                    
                elif choice == "3":
                    model_name = input("Model name (default 'demo-model'): ") or "demo-model"
                    epochs = int(input("Number of epochs (default 25): ") or "25")
                    uri = await client_manager.start_ml_training(client, model_name=model_name, epochs=epochs)
                    print(f"Task URI: {uri}")
                    
                elif choice == "4":
                    await client_manager.print_server_stats(client)
                    
                elif choice == "5":
                    await client_manager.print_task_list(client)
                    
                elif choice == "6":
                    task_id = await client_manager.select_task(client)
                    if task_id:
                        uri = f"task://status/{task_id}"
                        await client_manager.poll_task_until_complete(client, uri)
                    
                elif choice == "7":
                    task_id = await client_manager.select_task(client)
                    if task_id:
                        await client_manager.cancel_task(client, task_id)
                    
                elif choice == "8":
                    print("👋 Bye!")
                    break
                    
                else:
                    print("❌ Invalid option. Please select 1-8.")
                    
            except KeyboardInterrupt:
                print("\n👋 Demo interrupted. Bye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    try:
        asyncio.run(interactive_demo())
    except KeyboardInterrupt:
        print("\n👋 Bye!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
