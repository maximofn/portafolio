#!/bin/bash

# Script para ejecutar el cliente MCP streaming
# Uso: ./run.sh [server_url]

SERVER_URL=${1:-"http://localhost:8000/mcp/"}

echo "🌟 Cliente MCP Streaming"
echo "🔗 Servidor: $SERVER_URL"
echo ""

# Verificar si FastMCP está instalado
python -c "import fastmcp" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ FastMCP no está instalado"
    echo "📦 Instalando dependencias..."
    pip install -r requirements.txt
    echo ""
fi

echo "▶️  Ejecutando cliente..."
python cliente.py

echo "⏹️  Cliente finalizado"