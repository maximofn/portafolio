
import sys
import asyncio
from contextlib import AsyncExitStack
from anthropic import Anthropic
from dotenv import load_dotenv
import mcp.types as types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables from .env file
load_dotenv()

class FastMCPClient:
    """
    FastMCP client that integrates with Claude to process user queries
    and use tools exposed by a FastMCP server via STDIO.
    """

    def __init__(self, server_script_path: str):
        """Initialize the FastMCP client with Anthropic and resource management."""
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.session = None
        self.server_params = None
        self.server_script_path = server_script_path

    async def connect_to_server(self):
        """
        Connect to the FastMCP server via STDIO.
        """
        print(f"🔗 Connecting to FastMCP server: {self.server_script_path}")

        # Determine the server type based on the extension
        if self.server_script_path.endswith('.py'):
            # Python server
            self.server_params = StdioServerParameters(
                command="python",
                args=[self.server_script_path],
                env=None
            )
        elif self.server_script_path.endswith('.js'):
            # JavaScript/Node.js server
            self.server_params = StdioServerParameters(
                command="node", 
                args=[self.server_script_path],
                env=None
            )
        else:
            raise ValueError(f"Unsupported server type. Use .py or .js files. Got: {self.server_script_path}")

        # Set up connection to the server
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(self.server_params)
        )

        # Create MCP session
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(stdio_transport[0], stdio_transport[1])
        )

        # Initialize the session
        await self.session.initialize()

        print("✅ Connection established successfully")

        # List available tools and resources
        await self.list_available_tools()

    async def list_available_tools(self):
        """List available tools in the FastMCP server."""
        try:
            # Get list of tools from the server
            tools_result = await self.session.list_tools()

            if tools_result.tools:
                print(f"\n🛠️  Available tools ({len(tools_result.tools)}):")
                print("=" * 50)

                for tool in tools_result.tools:
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

    async def call_tool(self, tool_name: str, arguments: dict) -> str:
        """
        Call a tool on the FastMCP server via STDIO.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments for the tool

        Returns:
            str: Result from the tool
        """
        try:
            print(f"🔧 Calling tool: {tool_name}")
            print(f"📝 Arguments: {arguments}")

            # Execute tool on the MCP server
            tool_result = await self.session.call_tool(tool_name, arguments)

            print(f"✅ Tool executed successfully")

            # Format result for Claude
            if tool_result.content:
                # Combine all content into a single result
                combined_content = ""
                for content in tool_result.content:
                    # Check if it's TextContent (has text attribute)
                    if hasattr(content, 'text'):
                        combined_content += content.text + "\n"
                    # Check if it's ImageContent (has data attribute)  
                    elif hasattr(content, 'data'):
                        combined_content += f"[Binary content returned by tool {tool_name}]\n"
                    else:
                        combined_content += f"[Unknown content type returned by tool {tool_name}]\n"

                return combined_content.strip()
            else:
                return "Tool executed without response content"

        except Exception as e:
            error_msg = f"❌ Error calling tool {tool_name}: {str(e)}"
            print(error_msg)
            return error_msg

    async def process_query(self, query: str) -> str:
        """
        Process a user query, interacting with Claude and FastMCP tools.

        Args:
            query: User query

        Returns:
            str: Final processed response
        """
        try:
            # Get available tools, resources and templates from the server
            tools_result = await self.session.list_tools()

            # Prepare tools for Claude in correct format
            claude_tools = []
            for tool in tools_result.tools:
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

                    # Check if it's the special resource reading tool
                    if tool_name == "read_mcp_resource":
                        # Read resource directly
                        tool_result = await self.read_resource(tool_args["uri"])
                    else:
                        # Execute regular tool on the FastMCP server
                        tool_result = await self.call_tool(tool_name, tool_args)

                    # Add tool result to the conversation
                    messages.append({
                        "role": "assistant", 
                        "content": response.content
                    })

                    messages.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": tool_call_id,
                            "content": f"Tool result: {tool_result}"
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
        print("📚 The client can use both tools and resources from the FastMCP server")
        print("-" * 60)

        while True:
            try:
                # Get user input
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

    print(f"🚀 Starting FastMCP client...")
    print(f"📄 Server script: {server_script_path}")

    # Create and run client
    client = FastMCPClient(server_script_path)

    try:
        # Connect to the server
        await client.connect_to_server()

        # Start chat loop
        await client.chat_loop()

    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        print("💡 Make sure:")
        print("   1. The server script path is correct")
        print("   2. You have ANTHROPIC_API_KEY in your .env file")
        print("   3. The server script is executable")
    finally:
        # Ensure resources are cleaned up
        await client.cleanup()


if __name__ == "__main__":
    # Entry point of the script
    asyncio.run(main()) 
