#!/bin/bash

# URL del endpoint de la API
API_URL="http://127.0.0.1:5000/query"

# Consulta que deseas enviar
QUERY_TEXT="¿Blister con 10 anclajes para redes cual es el limite de carga?"

# Enviar la solicitud POST y guardar la respuesta
response=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$QUERY_TEXT\"}")

# Imprimir la respuesta
echo "Respuesta de la API:"
echo "$response"