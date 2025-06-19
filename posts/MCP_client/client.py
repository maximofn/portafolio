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

class MCPClient:
    """
    MCP client that integrates with Claude to process user queries
    and use tools exposed by an MCP server.
    """
    
    def __init__(self):
        """Initialize the MCP client with Anthropic and resource management."""
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.session = None
        self.server_params = None
        
    async def connect_to_server(self, server_script_path: str):
        """
        Connect to the specified MCP server.
        
        Args:
            server_script_path: Path to the server script (Python or JavaScript)
        """
        print(f"🔗 Conectando al servidor MCP: {server_script_path}")
        
        # Determine the server type based on the extension
        if server_script_path.endswith('.py'):
            # Python server
            self.server_params = StdioServerParameters(
                command="python",
                args=[server_script_path],
                env=None
            )
        elif server_script_path.endswith('.js'):
            # JavaScript/Node.js server
            self.server_params = StdioServerParameters(
                command="node", 
                args=[server_script_path],
                env=None
            )
        else:
            raise ValueError(f"Tipo de servidor no soportado. Use archivos .py o .js. Recibido: {server_script_path}")
        
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
        
        # Listar herramientas disponibles
        await self.list_available_tools()
        
    async def list_available_tools(self):
        """Lista y muestra las herramientas disponibles en el servidor MCP."""
        try:
            # Obtener lista de herramientas del servidor
            tools_result = await self.session.list_tools()
            
            if tools_result.tools:
                print(f"\n🛠️  Herramientas disponibles ({len(tools_result.tools)}):")
                print("=" * 50)
                
                for tool in tools_result.tools:
                    print(f"📋 {tool.name}")
                    if tool.description:
                        print(f"   Descripción: {tool.description}")
                    
                    # Mostrar parámetros si están disponibles
                    if hasattr(tool, 'inputSchema') and tool.inputSchema:
                        if 'properties' in tool.inputSchema:
                            params = list(tool.inputSchema['properties'].keys())
                            print(f"   Parámetros: {', '.join(params)}")
                    print()
            else:
                print("⚠️  No se encontraron herramientas disponibles en el servidor")
                
        except Exception as e:
            print(f"❌ Error al listar herramientas: {str(e)}")
    
    async def process_query(self, query: str) -> str:
        """
        Process a user query, interacting with Claude and MCP tools.
        
        Args:
            query: User query
            
        Returns:
            str: Final processed response
        """
        try:
            # Get available tools
            tools_result = await self.session.list_tools()
            
            # Prepare tools for Claude in correct format
            claude_tools = []
            for tool in tools_result.tools:
                claude_tool = {
                    "name": tool.name,
                    "description": tool.description or f"Herramienta {tool.name}",
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
                max_tokens=6000,  # Increase tokens for longer responses
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
                    
                    print(f"🔧 Claude wants to use tool: {tool_name}")
                    print(f"📝 Arguments: {tool_args}")
                    
                    try:
                        # Execute tool on the MCP server
                        tool_result = await self.session.call_tool(
                            tool_name, 
                            tool_args
                        )
                        
                        print(f"✅ Tool executed successfully")
                        
                        # Add tool result to the conversation
                        messages.append({
                            "role": "assistant", 
                            "content": response.content
                        })
                        
                        # Format result for Claude
                        if tool_result.content:
                            # Combine all content into a single result
                            combined_content = ""
                            for content in tool_result.content:
                                if content.type == "text":
                                    combined_content += content.text + "\n"
                                elif content.type == "image":
                                    combined_content += f"[Image returned by the tool {tool_name}]\n"
                            
                            messages.append({
                                "role": "user",
                                "content": [{
                                    "type": "tool_result",
                                    "tool_use_id": tool_call_id,
                                    "content": combined_content.strip()
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
                            max_tokens=6000,  # Increase tokens for longer responses
                            messages=messages,
                            tools=claude_tools if claude_tools else None
                        )
                        
                        # Extract text from the final response
                        for final_content in final_response.content:
                            if final_content.type == "text":
                                response_text += final_content.text
                                
                    except Exception as e:
                        error_msg = f"❌ Error al ejecutar herramienta {tool_name}: {str(e)}"
                        print(error_msg)
                        response_text += f"\n\n{error_msg}"
            
            return tool_result.content
            
        except Exception as e:
            error_msg = f"❌ Error al procesar consulta: {str(e)}"
            print(error_msg)
            return error_msg
    
    async def chat_loop(self):
        """
        Main chat loop with user interaction.
        """
        print("\n🤖 MCP client started. Write 'quit' to exit.")
        print("💬 You can ask questions about GitHub repositories!")
        print("-" * 60)
        
        while True:
            try:
                # Solicitar entrada del usuario
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
    Main function that initializes and runs the MCP client.
    """
    # Verify command line arguments
    if len(sys.argv) != 2:
        print("❌ Usage: python client.py <path_to_mcp_server>")
        print("📝 Example: python client.py ../MCP_github/github_server.py")
        sys.exit(1)
    
    server_script_path = sys.argv[1]
    
    # Create and run client
    client = MCPClient()
    
    try:
        # Connect to the server
        await client.connect_to_server(server_script_path)
        
        # Start chat loop
        await client.chat_loop()
        
    except Exception as e:
        print(f"❌ Error fatal: {str(e)}")
    finally:
        # Ensure resources are cleaned up
        await client.cleanup()


if __name__ == "__main__":
    # Entry point of the script
    asyncio.run(main())

