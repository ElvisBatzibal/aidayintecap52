import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer
import subprocess
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
# 1. Cargar el modelo para generar embeddings
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# 2. Conexión a la base de datos
conn = psycopg2.connect(
    dbname="intecap52",
    user="admin",
    password="secret",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Función para convertir el embedding a lista (si es necesario)
def vector_to_list(vector: np.ndarray):
    return vector.tolist()

# 3. Generar el embedding para la consulta del usuario
consulta = "¿Blister con 10 anclajes para redes cual es el limite de carga?"
query_embedding = model.encode(consulta)
query_embedding_list = vector_to_list(query_embedding)
query_embedding_str = "[" + ",".join(map(str, query_embedding_list)) + "]"

# 4. Ejecutar la consulta de búsqueda semántica
sql = """
SELECT 
  T0.document_id, 
  T1.file_name,
  T0.chunk_index,
  T0.chunk_text,
  T0.embedding <-> (%s)::vector(768) AS distance
FROM 
  productembeddings AS T0
  INNER JOIN documents AS T1 ON T0.document_id = T1.doc_id
ORDER BY 
  distance ASC
LIMIT 5;
"""
cur.execute(sql, (query_embedding_str,))
resultados = cur.fetchall()

# 5. Mostrar los resultados
print("Registros más similares:")
for fila in resultados:
    print(f"DocumentID: {fila[0]}, NombreDocumento: {fila[1]}, Distancia: {fila[4]}, chunk_index: {fila[2]}")

# Cerrar conexión a la base de datos
cur.close()
conn.close()

# 6. Concatenar los textos relevantes de los chunks para formar el contexto.
context = " ".join([fila[3] for fila in resultados[:1]])
print("\nContexto combinado:")
print(context)

# 7. Función para consultar a Ollama a través de subprocess
def query_ollama(model_name, prompt):
    """
    Llama a Ollama con el modelo especificado y un prompt.
    Se asume que Ollama está instalado y configurado en el sistema.
    """
    command = ["ollama", "query", model_name, "-p", prompt]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout.strip()

# 8. Crear el prompt para Ollama combinando el contexto y la pregunta
prompt = f"Utilizando la siguiente información, responde a la pregunta.\n\nContexto: {context}\n\nPregunta: {consulta}\n\nRespuesta:"
ollama_model = "ollama-llama2-7b"  # Reemplaza con el nombre del modelo que deseas usar en Ollama

# 9. Consultar a Ollama y obtener la respuesta
respuesta_ollama = query_ollama(ollama_model, prompt)
print("\nRespuesta generada por Ollama:")
print(respuesta_ollama)