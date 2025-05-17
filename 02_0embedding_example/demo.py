from sentence_transformers import SentenceTransformer

# Carga el modelo como SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Ahora puedes generar embeddings con el método encode
embedding = model.encode("Tu texto aquí")
print(type(embedding))  # Debería mostrar <class 'numpy.ndarray'>
print(embedding.shape)  # Debería mostrar (768,) en un caso típico
print(embedding)