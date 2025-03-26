# Intecap52

Este proyecto tiene como objetivo procesar documentos y generar embeddings utilizando modelos de aprendizaje automático para su almacenamiento y consulta en una base de datos PostgreSQL con soporte para vectores (pgvector).

## Tabla de Contenidos
- [Intecap52](#intecap52)
  - [Tabla de Contenidos](#tabla-de-contenidos)
  - [Descripción del Proyecto](#descripción-del-proyecto)
  - [Requisitos](#requisitos)
    - [Software](#software)
    - [Librerías de Python](#librerías-de-python)
    - [Pasos.](#pasos)

---

## Descripción del Proyecto

El proyecto **Intecap52** permite:
1. Procesar documentos almacenados en la base de datos.
2. Generar embeddings de texto utilizando el modelo `all-MiniLM-L6-v2` de la librería `SentenceTransformers`.
3. Almacenar los embeddings en una base de datos PostgreSQL con soporte para vectores mediante la extensión `pgvector`.
4. Realizar consultas eficientes sobre los embeddings para tareas como búsqueda semántica.

---

## Requisitos

Antes de comenzar, asegúrate de tener instalados los siguientes componentes:

### Software
- Python 3.8 o superior
- PostgreSQL 14 o superior
- Extensión `pgvector` para PostgreSQL

### Librerías de Python
Las dependencias necesarias están listadas en el archivo `requirements.txt`. Incluyen:
- `psycopg2-binary`: Para conectarse a PostgreSQL.
- `sentence-transformers`: Para generar embeddings.
- `numpy`: Para manejar vectores.

---


### Pasos. 

1. 


Extensiones y Modelos Utilizados

Extensiones

pgvector: Extensión para PostgreSQL que permite almacenar y consultar vectores de manera eficiente.

Modelos

all-MiniLM-L6-v2: Modelo de SentenceTransformers utilizado para generar embeddings compactos y eficientes.




https://www.truper.com/CatVigente/productosNuevos?page=1


https://github.com/pgvector/pgvector



ollama list

ollama pull ollama-llama2-7b

