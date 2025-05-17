CREATE TABLE Products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    specs JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE EXTENSION vector;



CREATE TABLE Documents (
    doc_id SERIAL PRIMARY KEY,
    product_id INTEGER, -- Si deseas relacionarlo con algún producto
    file_name VARCHAR(255) NOT NULL,
    doc_type VARCHAR(50), -- 'pdf' o 'image'
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE Documents
ADD CONSTRAINT unique_file_name UNIQUE (file_name);



CREATE TABLE ProductEmbeddings (
  document_id SERIAL NOT NULL,
  chunk_index INTEGER NOT NULL,
  embedding VECTOR(768) NOT NULL,
  chunk_text TEXT, -- opcional, para guardar el texto del chunk
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (document_id, chunk_index),
  FOREIGN KEY (document_id) REFERENCES Documents(doc_id)
);

CREATE INDEX ON productembeddings USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

