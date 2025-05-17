import psycopg2
from sentence_transformers import SentenceTransformer

# Inicializar el modelo de embeddings
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Función para generar embeddings
def generate_embedding(text):
    embeddings = model.encode(text)
    return embeddings.tolist()

# Función simple para dividir el texto en chunks
def chunk_text(text, chunk_size=500):
    """
    Divide el texto en fragmentos de aproximadamente 'chunk_size' caracteres.
    Puedes ajustar este método para que respete límites de párrafos o sentencias.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        # Se puede mejorar para evitar cortar a mitad de palabra o oración
        chunk = text[start:end]
        chunks.append(chunk)
        start = end
    return chunks

# Conexión a Postgres
conn = psycopg2.connect(
    dbname="intecap52",
    user="admin",
    password="secret",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Obtener documentos desde la tabla Documents
cursor.execute("SELECT doc_id, content FROM Documents")
documents = cursor.fetchall()

# Procesar cada documento y generar embeddings por chunk
for doc_id, content in documents:
    # Dividir el contenido en chunks
    chunks = chunk_text(content, chunk_size=500)
    for idx, chunk in enumerate(chunks):
        # Generar embedding para cada chunk
        embedding = generate_embedding(chunk)
        print(f"Embedding generado para el documento {doc_id}, chunk {idx}")
        # Insertar el embedding junto con el chunk_text en la tabla
        cursor.execute("""
            INSERT INTO ProductEmbeddings (document_id, chunk_index, embedding, chunk_text, updated_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (document_id, chunk_index) DO UPDATE 
            SET embedding = EXCLUDED.embedding, 
                chunk_text = EXCLUDED.chunk_text,
                updated_at = CURRENT_TIMESTAMP
        """, (doc_id, idx, embedding, chunk))

# Confirmar los cambios y cerrar la conexión
conn.commit()
cursor.close()
conn.close()

print("Embeddings por chunks almacenados exitosamente!")