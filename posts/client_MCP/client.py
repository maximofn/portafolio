
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
    and use tools and resources exposed by a FastMCP server.
    """

    def __init__(self):
        """Initialize the FastMCP client with Anthropic and resource management."""
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.client = None

    async def connect_to_server(self, server_url: str):
        """
        Connect to the specified FastMCP server via HTTP.

        Args:
            server_url: URL of the HTTP server (e.g., "http://localhost:8000/mcp")
        """
        print(f"🔗 Connecting to FastMCP HTTP server: {server_url}")

        # Create FastMCP client for HTTP connection using SSE transport
        self.client = Client(server_url)
        # Note: FastMCP Client automatically detects HTTP URLs and uses SSE transport

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

    async def list_available_resources(self):
        """List available resources in the FastMCP server."""
        try:
            # Get list of resources from the server using FastMCP context
            async with self.client as client:
                resources = await client.list_resources()

                if resources:
                    print(f"\n📚 Available resources ({len(resources)}):")
                    print("=" * 50)

                    for resource in resources:
                        print(f"📄 {resource.uri}")
                        if resource.name:
                            print(f"   Name: {resource.name}")
                        if resource.description:
                            print(f"   Description: {resource.description}")
                        if resource.mimeType:
                            print(f"   MIME Type: {resource.mimeType}")
                        print()
                else:
                    print("⚠️  No resources found in the server")

        except Exception as e:
            print(f"❌ Error listing resources: {str(e)}")

    async def list_available_prompts(self):
        """List available prompts in the FastMCP server."""
        try:
            # Get list of prompts from the server using FastMCP context
            async with self.client as client:
                prompts = await client.list_prompts()

                if prompts:
                    print(f"\n💭 Available prompts ({len(prompts)}):")
                    print("=" * 50)

                    for prompt in prompts:
                        print(f"🎯 {prompt.name}")
                        if prompt.description:
                            print(f"   Description: {prompt.description}")

                        # Show parameters if available
                        if hasattr(prompt, 'arguments') and prompt.arguments:
                            params = []
                            for arg in prompt.arguments:
                                param_info = f"{arg.name}: {arg.description or 'No description'}"
                                if arg.required:
                                    param_info += " (required)"
                                params.append(param_info)
                            print(f"   Parameters: {', '.join(params)}")
                        print()
                else:
                    print("⚠️  No prompts found in the server")

        except Exception as e:
            print(f"❌ Error listing prompts: {str(e)}")

    async def read_resource(self, resource_uri: str):
        """
        Read a specific resource from the server.

        Args:
            resource_uri: URI of the resource to read

        Returns:
            str: Resource content
        """
        try:
            async with self.client as client:
                result = await client.read_resource(resource_uri)
                return result
        except Exception as e:
            print(f"❌ Error reading resource {resource_uri}: {str(e)}")
            return None

    async def get_prompt(self, prompt_name: str, prompt_args: dict = None):
        """
        Get/call a specific prompt from the server.

        Args:
            prompt_name: Name of the prompt to call
            prompt_args: Arguments for the prompt (if any)

        Returns:
            str: Generated prompt content
        """
        try:
            async with self.client as client:
                if prompt_args:
                    result = await client.get_prompt(prompt_name, prompt_args)
                else:
                    result = await client.get_prompt(prompt_name)

                # Extract the prompt text from the response
                if hasattr(result, 'messages') and result.messages:
                    # FastMCP returns prompts as message objects
                    return '\n'.join([msg.content.text for msg in result.messages if hasattr(msg.content, 'text')])
                elif hasattr(result, 'content'):
                    return str(result.content)
                else:
                    return str(result)

        except Exception as e:
            print(f"❌ Error getting prompt {prompt_name}: {str(e)}")
            return None

    async def process_query(self, query: str) -> str:
        """
        Process a user query, interacting with Claude and FastMCP tools and resources.

        Args:
            query: User query

        Returns:
            str: Final processed response
        """
        try:
            # Use FastMCP context for all operations
            async with self.client as client:
                # Get available tools, resources, and prompts
                tools_list = await client.list_tools()
                resources_list = await client.list_resources()
                prompts_list = await client.list_prompts()

                # Prepare tools for Claude in correct format
                claude_tools = []
                for tool in tools_list:
                    claude_tool = {
                        "name": tool.name,
                        "description": tool.description or f"Tool {tool.name}",
                        "input_schema": tool.inputSchema or {"type": "object", "properties": {}}
                    }
                    claude_tools.append(claude_tool)

                # Add a special tool for reading resources (including template resources)
                resource_description = "Read a resource from the MCP server. "
                if resources_list:
                    # Convert URIs to strings to avoid AnyUrl object issues
                    resource_uris = [str(r.uri) for r in resources_list]
                    resource_description += f"Available static resources: {', '.join(resource_uris)}. "

                resource_description += "Also supports template resources like github://repo/owner/repo_name for GitHub repository information."

                claude_tools.append({
                    "name": "read_mcp_resource",
                    "description": resource_description,
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "resource_uri": {
                                "type": "string",
                                "description": "URI of the resource to read. Can be static (like resource://server_info) or template-based (like github://repo/facebook/react)"
                            }
                        },
                        "required": ["resource_uri"]
                    }
                })

                # Add a special tool for using prompts
                prompt_description = "Generate specialized prompts from the MCP server. Use this when users want to:\n"
                prompt_description += "- Create well-structured questions about repositories\n"
                prompt_description += "- Get help formulating prompts for specific tasks\n"
                prompt_description += "- Generate template questions for analysis\n"
                if prompts_list:
                    prompt_names = [p.name for p in prompts_list]
                    prompt_description += f"\nAvailable prompts: {', '.join(prompt_names)}\n"
                    prompt_description += "- generate_issues_prompt: Creates structured questions about GitHub repository issues"

                prompt_description += "\n\nIMPORTANT: Use prompts when users explicitly ask for help creating questions or prompts, or when they want to formulate better questions about repositories."

                claude_tools.append({
                    "name": "use_mcp_prompt",
                    "description": prompt_description,
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "prompt_name": {
                                "type": "string",
                                "description": "Name of the prompt to use. Available: 'generate_issues_prompt'"
                            },
                            "prompt_args": {
                                "type": "object",
                                "description": "Arguments for the prompt. For generate_issues_prompt: {'owner': 'repo-owner', 'repo_name': 'repo-name'}",
                                "properties": {
                                    "owner": {
                                        "type": "string",
                                        "description": "Repository owner (e.g., 'huggingface', 'microsoft')"
                                    },
                                    "repo_name": {
                                        "type": "string", 
                                        "description": "Repository name (e.g., 'transformers', 'vscode')"
                                    }
                                }
                            }
                        },
                        "required": ["prompt_name"]
                    }
                })

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
                            if tool_name == "read_mcp_resource":
                                # Handle resource reading
                                resource_uri = tool_args.get("resource_uri")
                                if resource_uri:
                                    tool_result = await client.read_resource(resource_uri)
                                    print(f"📖 Resource read successfully: {resource_uri}")

                                    # Better handling of resource result
                                    if hasattr(tool_result, 'content'):
                                        # If it's a resource response object, extract content
                                        if hasattr(tool_result.content, 'text'):
                                            result_content = tool_result.content.text
                                        else:
                                            result_content = str(tool_result.content)
                                    else:
                                        # If it's already a string or simple object
                                        result_content = str(tool_result)
                                else:
                                    tool_result = "Error: No resource URI provided"
                                    result_content = tool_result

                            elif tool_name == "use_mcp_prompt":
                                # Handle prompt usage
                                prompt_name = tool_args.get("prompt_name")
                                prompt_args = tool_args.get("prompt_args", {})

                                if prompt_name:
                                    tool_result = await self.get_prompt(prompt_name, prompt_args)
                                    print(f"💭 Prompt '{prompt_name}' generated successfully")
                                    result_content = str(tool_result) if tool_result else "Error generating prompt"
                                else:
                                    tool_result = "Error: No prompt name provided"
                                    result_content = tool_result

                            else:
                                # Execute regular tool on the FastMCP server
                                tool_result = await client.call_tool(tool_name, tool_args)
                                print(f"✅ Tool executed successfully")
                                result_content = str(tool_result)

                            # Add tool result to the conversation
                            messages.append({
                                "role": "assistant", 
                                "content": response.content
                            })

                            # Format result for Claude
                            if tool_result:
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
        print("📚 The client can use tools, resources, and prompts from the FastMCP server")
        print()
        print("💭 PROMPT Examples:")
        print("   • 'Generate a prompt for asking about issues in facebook/react'")
        print("   • 'Help me create a good question about microsoft/vscode issues'") 
        print("   • 'I need a structured prompt for analyzing tensorflow/tensorflow'")
        print()
        print("🔧 DIRECT Examples:")
        print("   • 'Show me the issues in huggingface/transformers'")
        print("   • 'Get repository info for github://repo/google/chrome'")
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
        await client.connect_to_server(server_url)

        # List available tools, resources, and prompts after connection
        await client.list_available_tools()
        await client.list_available_resources()
        await client.list_available_prompts()

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
