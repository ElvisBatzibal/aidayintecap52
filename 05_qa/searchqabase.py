import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import pipeline

# Cargar el modelo para generar embeddings
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Conexión a la base de datos
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

# 1. Generar el embedding para la consulta del usuario
consulta = "¿Blister con 10 anclajes para redes cual es el limite de carga?"
query_embedding = model.encode(consulta)
query_embedding_list = vector_to_list(query_embedding)

query_embedding_str = "[" + ",".join(map(str, query_embedding_list)) + "]"


# 2. Ejecutar la consulta de búsqueda semántica
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

# 3. Mostrar los resultados
print("Registros más similares:")
for fila in resultados:
    #chunk_text: {fila[3]}
    print(f"DocumentID: {fila[0]}, NombreDocumento: {fila[1]}, Distancia: {fila[4]}, chunk_index: {fila[2]} ")

# Cerrar conexión
cur.close()
conn.close()

# 1. Concatenar los textos relevantes de los chunks para formar el contexto.
context = " ".join([fila[3] for fila in resultados[:1]])
print("\nContexto combinado:")
print(context)

# 2. Inicializar el pipeline de pregunta-respuesta
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

# 3. Ejecutar el modelo QA con la consulta y el contexto combinado
respuesta = qa_pipeline(question=consulta, context=context)
print("\nRespuesta generada:")
print(respuesta["answer"])