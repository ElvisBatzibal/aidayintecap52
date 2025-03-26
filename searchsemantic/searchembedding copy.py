import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer

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
consulta = "¿Qué características tiene el producto 13472?"
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
    print(f"DocumentID: {fila[0]}, NombreDocumento: {fila[1]}, Distancia: {fila[4]}, chunk_index: {fila[2]} , chunk_text: {fila[3]}")

# Cerrar conexión
cur.close()
conn.close()