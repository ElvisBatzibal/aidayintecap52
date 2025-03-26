import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer
import subprocess
import os
import re

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
context_combinado = " ".join([fila[3] for fila in resultados[:1]])
print("\nContexto combinado:")
print(context_combinado)
context_combinado = context_combinado.replace('\n', ' ')
context_combinado = re.sub(r'\s+', ' ', context_combinado)

# 7. Función para consultar a Ollama a través de subprocess
def query_mistral(prompt, model_name="mistral:latest", temperature=0.7, max_tokens=200):
    """
    Llama al modelo Mistral mediante la CLI de Ollama.
    
    Parámetros:
    - prompt: El texto que se envía al modelo.
    - model_name: Nombre del modelo a usar (por defecto "mistral:latest").
    - temperature y max_tokens: Opcionales para controlar la generación.
    
    Retorna la respuesta del modelo como string.
    """
    # Construir el comando con parámetros adicionales, si fueran necesarios.
    # Puedes agregar banderas como --temperature y --max_tokens según la documentación.
    # command = [
    #     "ollama", "run", model_name,
    #     "-p", prompt
    # ]   
    command = f'ollama run mistral:latest "{prompt}"'
    print (command)
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)
    return result.stdout.strip()
# Ejemplo de cómo construir el prompt:
# Supongamos que ya tienes el contexto combinado de los tres chunks relevantes:
context = f"Información relevante extraída de documentos: {context_combinado}"

prompt = (
    f"Utilizando la siguiente información, responde a la pregunta. "
    f"Contexto: {context} "
    f"Pregunta: {consulta} "
    f"Respuesta:"
)

# Llamar a Mistral a través de Ollama:
respuesta_mistral = query_mistral(prompt)
print("Respuesta generada por Mistral:")
print(respuesta_mistral)