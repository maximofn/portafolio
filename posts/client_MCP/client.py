
import sys
import asyncio
from contextlib import AsyncExitStack
from anthropic import Anthropic
from dotenv import load_dotenv
from fastmcp import Client

# Load environment variables from .env file
load_dotenv()

class FastMCPClient:
    """
    FastMCP client that integrates with Claude to process user queries
    and use tools exposed by a FastMCP server.
    """

    def __init__(self):
        """Initialize the FastMCP client with Anthropic and resource management."""
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.client = None

    async def connect_to_server(self, server_script_path: str):
        """
        Connect to the specified FastMCP server.

        Args:
            server_script_path: Path to the server script (Python)
        """
        print(f"🔗 Connecting to FastMCP server: {server_script_path}")

        # Determine the server type based on the extension
        if not server_script_path.endswith('.py'):
            raise ValueError(f"Unsupported server type. Use .py files. Received: {server_script_path}")

        # Create FastMCP client 
        self.client = Client(server_script_path)
        # Note: FastMCP Client automatically infers transport from .py files

        print("✅ Client created successfully")

    async def list_available_tools(self):
        """List available tools in the FastMCP server."""
        try:
            # Get list of tools from the server using FastMCP context
            async with self.client as client:
                tools = await client.list_tools()

                if tools:
                    print(f"\n🛠️  Available tools ({len(tools)}):")
                    print("=" * 50)

                    for tool in tools:
                        print(f"📋 {tool.name}")
                        if tool.description:
                            print(f"   Description: {tool.description}")

                        # Show parameters if available
                        if hasattr(tool, 'inputSchema') and tool.inputSchema:
                            if 'properties' in tool.inputSchema:
                                params = list(tool.inputSchema['properties'].keys())
                                print(f"   Parameters: {', '.join(params)}")
                        print()
                else:
                    print("⚠️  No tools found in the server")

        except Exception as e:
            print(f"❌ Error listing tools: {str(e)}")

    async def process_query(self, query: str) -> str:
        """
        Process a user query, interacting with Claude and FastMCP tools.

        Args:
            query: User query

        Returns:
            str: Final processed response
        """
        try:
            # Use FastMCP context for all operations
            async with self.client as client:
                # Get available tools
                tools_list = await client.list_tools()

                # Prepare tools for Claude in correct format
                claude_tools = []
                for tool in tools_list:
                    claude_tool = {
                        "name": tool.name,
                        "description": tool.description or f"Tool {tool.name}",
                        "input_schema": tool.inputSchema or {"type": "object", "properties": {}}
                    }
                    claude_tools.append(claude_tool)

                # Create initial message for Claude
                messages = [
                    {
                        "role": "user",
                        "content": query
                    }
                ]

                # First call to Claude
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=6000,
                    messages=messages,
                    tools=claude_tools if claude_tools else None
                )

                # Process Claude's response
                response_text = ""

                for content_block in response.content:
                    if content_block.type == "text":
                        response_text += content_block.text

                    elif content_block.type == "tool_use":
                        # Claude wants to use a tool
                        tool_name = content_block.name
                        tool_args = content_block.input
                        tool_call_id = content_block.id

                        print(f"🔧 Claude wants to use: {tool_name}")
                        print(f"📝 Arguments: {tool_args}")

                        try:
                            # Execute tool on the FastMCP server
                            tool_result = await client.call_tool(tool_name, tool_args)

                            print(f"✅ Tool executed successfully")

                            # Add tool result to the conversation
                            messages.append({
                                "role": "assistant", 
                                "content": response.content
                            })

                            # Format result for Claude
                            if tool_result:
                                # Convert result to string format for Claude
                                result_content = str(tool_result)

                                messages.append({
                                    "role": "user",
                                    "content": [{
                                        "type": "tool_result",
                                        "tool_use_id": tool_call_id,
                                        "content": f"Tool result: {result_content}"
                                    }]
                                })
                            else:
                                messages.append({
                                    "role": "user", 
                                    "content": [{
                                        "type": "tool_result",
                                        "tool_use_id": tool_call_id, 
                                        "content": "Tool executed without response content"
                                    }]
                                })

                            # Second call to Claude with the tool result
                            final_response = self.anthropic.messages.create(
                                model="claude-3-5-sonnet-20241022",
                                max_tokens=6000,
                                messages=messages,
                                tools=claude_tools if claude_tools else None
                            )

                            # Extract text from the final response
                            for final_content in final_response.content:
                                if final_content.type == "text":
                                    response_text += final_content.text

                        except Exception as e:
                            error_msg = f"❌ Error executing {tool_name}: {str(e)}"
                            print(error_msg)
                            response_text += f"\n\n{error_msg}"

                return response_text

        except Exception as e:
            error_msg = f"❌ Error processing query: {str(e)}"
            print(error_msg)
            return error_msg

    async def chat_loop(self):
        """
        Main chat loop with user interaction.
        """
        print("\n🤖 FastMCP client started. Write 'quit', 'q', 'exit', 'salir' to exit.")
        print("💬 You can ask questions about GitHub repositories!")
        print("📚 The client can use tools from the FastMCP server")
        print("-" * 60)

        while True:
            try:
                # Request user input
                user_input = input("\n👤 You: ").strip()

                if user_input.lower() in ['quit', 'q', 'exit', 'salir']:
                    print("👋 Bye!")
                    break

                if not user_input:
                    continue

                print("\n🤔 Claude is thinking...")

                # Process query
                response = await self.process_query(user_input)

                # Show response
                print(f"\n🤖 Claude: {response}")

            except KeyboardInterrupt:
                print("\n\n👋 Disconnecting...")
                break
            except Exception as e:
                print(f"\n❌ Error in chat: {str(e)}")
                continue

    async def cleanup(self):
        """Clean up resources and close connections."""
        print("🧹 Cleaning up resources...")
        # FastMCP Client cleanup is handled automatically by context manager
        await self.exit_stack.aclose()
        print("✅ Resources released")


async def main():
    """
    Main function that initializes and runs the FastMCP client.
    """
    # Verify command line arguments
    if len(sys.argv) != 2:
        print("❌ Usage: python client.py <path_to_fastmcp_server>")
        print("📝 Example: python client.py ../MCP_github/github_server.py")
        sys.exit(1)

    server_script_path = sys.argv[1]

    # Create and run client
    client = FastMCPClient()

    try:
        # Connect to the server
        await client.connect_to_server(server_script_path)

        # List available tools after connection
        await client.list_available_tools()

        # Start chat loop
        await client.chat_loop()

    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
    finally:
        # Ensure resources are cleaned up
        await client.cleanup()


if __name__ == "__main__":
    # Entry point of the script
    asyncio.run(main())
