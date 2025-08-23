#!/bin/bash

# Script para ejecutar el servidor MCP streaming
# Uso: ./run.sh [puerto]

PORT=${1:-8000}  # Puerto por defecto 8000

echo "🚀 Iniciando servidor MCP streaming..."
echo "📡 Puerto: $PORT"
echo "🔗 URL: http://localhost:$PORT/mcp/"
echo ""

# Verificar si FastMCP está instalado
python -c "import fastmcp" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ FastMCP no está instalado"
    echo "📦 Instalando dependencias..."
    pip install -r requirements.txt
    echo ""
fi

# Ejecutar servidor
echo "▶️  Ejecutando servidor..."
python servidor.py

echo "⏹️  Servidor detenido"