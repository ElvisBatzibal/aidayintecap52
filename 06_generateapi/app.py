from flask import Flask, request, jsonify
import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer
import subprocess
import os
import re

# Desactivar la paralelización de tokenizers para evitar advertencias
os.environ["TOKENIZERS_PARALLELISM"] = "false"

app = Flask(__name__)

# Cargar el modelo de embeddings (se carga una sola vez al iniciar la API)
embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

def vector_to_list(vector: np.ndarray):
    return vector.tolist()

def get_results_from_db(query_embedding_str):
    """Conecta a la base de datos, ejecuta la consulta de búsqueda semántica y devuelve los resultados."""
    db_host = os.getenv("DB_HOST", "localhost")
    conn = psycopg2.connect(
        dbname="intecap52",
        user="admin",
        password="secret",
        host=db_host,
        port="5432"
    )
    cur = conn.cursor()
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
    cur.close()
    conn.close()
    return resultados

def query_mistral(prompt, model_name="mistral:latest"):
    """
    Llama al modelo Mistral mediante la CLI de Ollama y retorna la respuesta generada.
    Se utiliza subprocess con shell=True para ejecutar el comando.
    """
    command = f'ollama run {model_name} "{prompt}"'
    print("Ejecutando comando:", command)
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result.stdout.strip()

@app.route('/query', methods=['POST'])
def process_query():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'No query provided'}), 400

    consulta = data['query']
    
    # 1. Generar el embedding para la consulta
    query_embedding = embedding_model.encode(consulta)
    query_embedding_list = vector_to_list(query_embedding)
    query_embedding_str = "[" + ",".join(map(str, query_embedding_list)) + "]"
    
    # 2. Ejecutar la consulta de búsqueda semántica en la base de datos
    resultados = get_results_from_db(query_embedding_str)
    if not resultados:
        return jsonify({'error': 'No results found'}), 404
    
    # 3. Concatenar los textos relevantes de los chunks para formar el contexto.
    # Aquí se usa el chunk_text del primer registro; se puede ajustar para usar más registros.
    context_combinado = " ".join([fila[3] for fila in resultados[:1]])
    context_combinado = context_combinado.replace('\n', ' ')
    context_combinado = re.sub(r'\s+', ' ', context_combinado)
    
    context = f"Información relevante extraída de documentos: {context_combinado}"
    
    # 4. Construir el prompt para Mistral
    prompt = (
        f"Utilizando la siguiente información, responde a la pregunta. "
        f"Contexto: {context} "
        f"Pregunta: {consulta} "
        f"Respuesta:"
    )
    
    # 5. Consultar a Mistral a través de Ollama
    respuesta = query_mistral(prompt)
    
    # 6. Retornar la respuesta en formato JSON
    return jsonify({
        'query': consulta,
        'context': context,
        'prompt': prompt,
        'response': respuesta
    })

if __name__ == '__main__':
    app.run(debug=True)