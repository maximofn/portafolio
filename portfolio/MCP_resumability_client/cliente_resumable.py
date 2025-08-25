#!/usr/bin/env python3
"""
Client MCP with resumability and session persistence capabilities.
Demonstrates how to connect to a resumable server and handle interruptions.
"""

import asyncio
import json
import time
import uuid
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


@dataclass
class TaskProgress:
    """Represents the progress of a task."""
    task_id: str
    task_name: str
    current_step: int
    total_steps: int
    last_message: str
    started_at: datetime = field(default_factory=datetime.now)
    last_update: datetime = field(default_factory=datetime.now)
    
    @property
    def progress_percent(self) -> float:
        """Calculate progress percentage."""
        if self.total_steps == 0:
            return 0.0
        return (self.current_step / self.total_steps) * 100


@dataclass
class SessionState:
    """Session state of the client."""
    client_id: str  # Persistent client ID
    session_id: str  # Session ID of the server (can change)
    server_url: str
    active_tasks: Dict[str, TaskProgress]
    completed_tasks: List[str]
    created_at: datetime = field(default_factory=datetime.now)


class ResumableProgressHandler:
    """Handles progress with resumability capabilities."""
    
    def __init__(self, task_name: str, session_state: SessionState):
        self.task_name = task_name
        self.session_state = session_state
        self.start_time = time.time()
        self.last_progress = 0
        self.task_progress: Optional[TaskProgress] = None
        
    def __call__(self, progress: float, total: float, message: str):
        """Callback for progress updates."""
        # Create or update task progress
        if not self.task_progress:
            # Try to find task_id from the message
            task_id = self._extract_task_id(message)
            if not task_id:
                task_id = f"task_{int(time.time())}"
            
            self.task_progress = TaskProgress(
                task_id=task_id,
                task_name=self.task_name,
                current_step=int(progress),
                total_steps=int(total),
                last_message=message
            )
            self.session_state.active_tasks[task_id] = self.task_progress
        else:
            self.task_progress.current_step = int(progress)
            self.task_progress.total_steps = int(total)
            self.task_progress.last_message = message
            self.task_progress.last_update = datetime.now()
        
        # Display progress visually
        self._display_progress(progress, total, message)
        
        # Save session state
        self._save_session_state()
    
    def _extract_task_id(self, message: str) -> Optional[str]:
        """Try to extract task_id from the message."""
        # Search for patterns like "task_id: abc123" in the message
        import re
        match = re.search(r'task[_\s]*id[:\s]*([a-f0-9]{16})', message.lower())
        return match.group(1) if match else None
    
    def _display_progress(self, progress: float, total: float, message: str):
        """Display progress visually."""
        percentage = (progress / total) * 100 if total > 0 else 0
        bar_length = 30
        filled_length = int(bar_length * percentage / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        elapsed = time.time() - self.start_time
        
        print(f"\r📊 {self.task_name}: |{bar}| {percentage:.1f}% "
              f"({progress:.0f}/{total:.0f}) - {message} [{elapsed:.1f}s]", 
              end='', flush=True)
        
        if progress >= total:
            print()  # New line when completed
            if self.task_progress:
                # Move to completed
                task_id = self.task_progress.task_id
                self.session_state.completed_tasks.append(task_id)
                if task_id in self.session_state.active_tasks:
                    del self.session_state.active_tasks[task_id]
                self._save_session_state()
    
    def _save_session_state(self):
        """Save session state."""
        # In a real case, this would be saved to disk
        pass


class MCPResumableClient:
    """Client MCP with resumability capabilities."""
    
    def __init__(self, server_url: str = "http://localhost:8001/mcp/"):
        self.server_url = server_url
        self.transport = None
        self.client = None
        self.session_state: Optional[SessionState] = None
        self.state_file = Path("session_state.json")
        
    async def __aenter__(self):
        """Initialize connection and load state."""
        # Load previous state if it exists
        self._load_session_state()
        
        self.transport = StreamableHttpTransport(
            url=self.server_url,
            sse_read_timeout=120.0  # Timeout for resumable tasks
        )
        
        self.client = Client(transport=self.transport)
        await self.client.__aenter__()
        
        # Create new session state if it doesn't exist
        if not self.session_state:
            # Generate unique persistent client ID
            client_id = str(uuid.uuid4())[:16]  # Use only the first 16 characters
            
            # Get real session_id from the server
            try:
                session_info_result = await self.client.call_tool("get_session_info", {})
                session_info = session_info_result.content[0].text if hasattr(session_info_result, 'content') else {}
                if isinstance(session_info, str):
                    import json
                    session_info = json.loads(session_info)
                real_session_id = session_info.get("session_id", f"session_{int(time.time())}")
                print("🏗️  Creating new session")
                print(f"🔗 Session ID of the server: {real_session_id}")
                print(f"🆔 Persistent Client ID: {client_id}")
            except Exception as e:
                print(f"⚠️  Could not get session_id from the server: {e}")
                real_session_id = f"session_{int(time.time())}"
            
            self.session_state = SessionState(
                client_id=client_id,
                session_id=real_session_id,
                server_url=self.server_url,
                active_tasks={},
                completed_tasks=[]
            )
            self._save_session_state()
        else:
            # Reuse existing client_id
            print(f"🆔 Reusing Persistent Client ID: {self.session_state.client_id}")
            
            # Verify if the session_id matches the server
            try:
                session_info_result = await self.client.call_tool("get_session_info", {})
                session_info = session_info_result.content[0].text if hasattr(session_info_result, 'content') else {}
                if isinstance(session_info, str):
                    import json
                    session_info = json.loads(session_info)
                server_session_id = session_info.get("session_id")
                if server_session_id and server_session_id != self.session_state.session_id:
                    print(f"⚠️  Session ID of the server changed: {self.session_state.session_id} → {server_session_id}")
                    self.session_state.session_id = server_session_id
                    self._save_session_state()
            except Exception as e:
                print(f"⚠️  Could not verify session_id: {e}")
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close connection and save state."""
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
        
        self._save_session_state()
    
    def _load_session_state(self):
        """Load session state from disk."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                
                # Reconstruct objects
                active_tasks = {}
                for task_id, task_data in data.get('active_tasks', {}).items():
                    task_data['started_at'] = datetime.fromisoformat(task_data['started_at'])
                    task_data['last_update'] = datetime.fromisoformat(task_data['last_update'])
                    active_tasks[task_id] = TaskProgress(**task_data)
                
                self.session_state = SessionState(
                    client_id=data.get('client_id', str(uuid.uuid4())[:16]),  # Generate if not exists
                    session_id=data['session_id'],
                    server_url=data['server_url'],
                    active_tasks=active_tasks,
                    completed_tasks=data.get('completed_tasks', []),
                    created_at=datetime.fromisoformat(data['created_at'])
                )
                
                print(f"📂 Session state loaded: {self.session_state.session_id}")
                
            except Exception as e:
                print(f"⚠️  Error loading session state: {e}")
                self.session_state = None

        else:
            print("💬 No session state found, starting new session")
            self.session_state = None
    
    def _save_session_state(self):
        """Save session state to disk."""
        if not self.session_state:
            return
        
        try:
            # Convert to serializable format
            active_tasks = {}
            for task_id, task_progress in self.session_state.active_tasks.items():
                active_tasks[task_id] = {
                    'task_id': task_progress.task_id,
                    'task_name': task_progress.task_name,
                    'current_step': task_progress.current_step,
                    'total_steps': task_progress.total_steps,
                    'last_message': task_progress.last_message,
                    'started_at': task_progress.started_at.isoformat(),
                    'last_update': task_progress.last_update.isoformat()
                }
            
            data = {
                'client_id': self.session_state.client_id,
                'session_id': self.session_state.session_id,
                'server_url': self.session_state.server_url,
                'active_tasks': active_tasks,
                'completed_tasks': self.session_state.completed_tasks,
                'created_at': self.session_state.created_at.isoformat()
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Error saving session state: {e}")
    
    async def test_connection(self) -> bool:
        """Test connection to the server."""
        try:
            await self.client.ping()
            print(f"✅ Connection established with the resumable server")
            return True
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    async def call_resumable_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        allow_resume: bool = True
    ) -> Dict[str, Any]:
        """Call tool with resumability capabilities."""
        
        progress_handler = ResumableProgressHandler(tool_name, self.session_state)
        
        start_time = time.time()
        
        # Add client_id to the parameters if allow_resume is enabled
        if allow_resume and self.session_state:
            parameters = {**parameters, 'client_id': self.session_state.client_id}
        
        try:
            print(f"🚀 Executing {tool_name} (resumption: {'✅' if allow_resume else '❌'})")
            
            result = await self.client.call_tool(
                tool_name,
                parameters,
                progress_handler=progress_handler
            )
            
            duration = time.time() - start_time
            print(f"✅ {tool_name} completed in {duration:.2f}s")
            
            return result
            
        except KeyboardInterrupt:
            print(f"\n⏸️  {tool_name} interrupted by the user")
            # In a real implementation, here we would pause the task
            raise
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"❌ {tool_name} failed after {duration:.2f}s: {e}")
            raise
    
    async def list_session_tasks(self) -> Dict[str, Any]:
        """List session tasks."""
        try:
            parameters = {}
            if self.session_state:
                parameters['client_id'] = self.session_state.client_id
            result = await self.client.call_tool("list_session_tasks", parameters)
            return result
        except Exception as e:
            print(f"❌ Error listing session tasks: {e}")
            return {"error": str(e)}
    
    async def pause_task(self, task_id: str) -> Dict[str, Any]:
        """Pause a specific task."""
        try:
            result = await self.client.call_tool("pause_task", {"task_id": task_id})
            return result
        except Exception as e:
            print(f"❌ Error pausing task {task_id}: {e}")
            return {"error": str(e)}
    
    async def get_checkpoint_stats(self) -> Dict[str, Any]:
        """Get checkpoint statistics."""
        try:
            result = await self.client.call_tool("get_checkpoint_stats", {})
            return result
        except Exception as e:
            print(f"❌ Error getting checkpoint statistics: {e}")
            return {"error": str(e)}
    
    def show_session_summary(self):
        """Show session summary."""
        if not self.session_state:
            print("❌ No session state available")
            return
        
        print("\n" + "="*60)
        print("📋 SESSION SUMMARY")
        print("="*60)
        print(f"🆔 Client ID (persistent): {self.session_state.client_id}")
        print(f"📌 Session ID (server): {self.session_state.session_id}")
        print(f"🔗 Server: {self.session_state.server_url}")
        print(f"📅 Created: {self.session_state.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n🔄 Active Tasks: {len(self.session_state.active_tasks)}")
        for task_id, task in self.session_state.active_tasks.items():
            progress = task.progress_percent
            print(f"  • {task.task_name} ({task_id[:8]}...): {progress:.1f}%")
            print(f"    └─ {task.last_message}")
        
        print(f"\n✅ Completed Tasks: {len(self.session_state.completed_tasks)}")
        for task_id in self.session_state.completed_tasks[-5:]:  # Last 5
            print(f"  • {task_id[:8]}...")


async def demo_resumable_data_processing(client: MCPResumableClient):
    """Demo of resumable data processing."""
    print("\n" + "="*60)
    print("📊 DEMO: Resumable Data Processing")
    print("="*60)
    
    result = await client.call_resumable_tool(
        "resumable_data_processing",
        {
            "dataset_name": "customer_data",
            "total_records": 50,
            "batch_size": 5
        }
    )
    
    if "error" not in result:
        print(f"📊 Result: {result.get('total_processed', 0)} records processed")
        print(f"🆔 Task ID: {result.get('task_id', 'N/A')}")


# async def demo_large_file_download(client: MCPResumableClient):
#     """Demo of resumable file download."""
#     print("\n" + "="*60)
#     print("📥 DEMO: Large File Download")
#     print("="*60)
    
#     result = await client.call_resumable_tool(
#         "large_file_download",
#         {
#             "file_url": "https://example.com/dataset.zip",
#             "file_size_mb": 200,
#             "chunk_size_mb": 25
#         }
#     )
    
#     if "error" not in result:
#         print(f"📁 Download: {result.get('total_size_mb', 0)} MB in {result.get('total_chunks', 0)} chunks")
#         print(f"🆔 Task ID: {result.get('task_id', 'N/A')}")


# async def demo_ml_training(client: MCPResumableClient):
#     """Demo of ML training resumable."""
#     print("\n" + "="*60)
#     print("🤖 DEMO: ML Training")
#     print("="*60)
    
#     result = await client.call_resumable_tool(
#         "machine_learning_training",
#         {
#             "model_name": "customer_classifier",
#             "total_epochs": 30,
#             "batch_size": 64
#         }
#     )
    
#     if "error" not in result:
#         print(f"🎯 Final accuracy: {result.get('final_accuracy', 0):.4f}")
#         print(f"📉 Loss final: {result.get('final_loss', 0):.4f}")
#         print(f"🆔 Task ID: {result.get('task_id', 'N/A')}")


async def interactive_demo(client: MCPResumableClient):
    """Interactive demo with options."""
    
    while True:
        print("\n" + "="*60)
        print("🎮 INTERACTIVE DEMO - Resumable Client")
        print("="*60)
        print("1. Resumable data processing")
        # print("2. Descarga de archivo grande")
        # print("3. Entrenamiento de ML")
        print("2. List session tasks")
        print("3. Checkpoint statistics")
        print("4. Session summary")
        print("0. Exit")
        print("-" * 60)
        
        try:
            choice = input("Select an option (0-4): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                await demo_resumable_data_processing(client)
            # elif choice == "2":
            #     await demo_large_file_download(client)
            # elif choice == "3":
            #     await demo_ml_training(client)
            elif choice == "2":
                tasks = await client.list_session_tasks()
                print(f"📋 Session tasks: {json.dumps(tasks, indent=2)}")
            elif choice == "3":
                stats = await client.get_checkpoint_stats()
                print(f"📊 Checkpoint statistics: {json.dumps(stats, indent=2)}")
            elif choice == "4":
                client.show_session_summary()
            else:
                print("❌ Invalid option")
                
        except KeyboardInterrupt:
            print("\n⏸️  Demo interrupted")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


async def run_resumable_demo():
    """Run resumable demo."""
    print("🌟 Resumable Client MCP - Demo")
    print("="*60)
    
    try:
        async with MCPResumableClient() as client:
            # Test connection
            if not await client.test_connection():
                print("❌ Could not connect to the resumable server.")
                print("   Make sure the server is running on port 8001")
                return
            
            # Show session state
            client.show_session_summary()
            
            # Run interactive demo
            await interactive_demo(client)
            
            print("\n🎉 Demo completed")
            
    except Exception as e:
        print(f"❌ Error in the demo: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(run_resumable_demo())
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by the user")
    except Exception as e:
        print(f"❌ Error running demo: {e}")