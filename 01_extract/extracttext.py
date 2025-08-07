import os
import PyPDF2
from PIL import Image
import pytesseract
import psycopg2
from pdf2image import convert_from_path
import fitz  # PyMuPDF
from paddleocr import PaddleOCR

# Inicializar PaddleOCR
ocr = PaddleOCR(use_textline_orientation=True, lang='es')

def extract_text_with_paddleocr(image_path):
    try:
        result = ocr.ocr(image_path, cls=True)
        text = "\n".join([line[1][0] for line in result[0]])
    except Exception as e:
        print(f"Error al procesar {image_path} con PaddleOCR: {e}")
        text = ""
    return text

def extract_text_with_pymupdf(pdf_path):
    text = ""
    try:
        pdf_document = fitz.open(pdf_path)
        for page in pdf_document:
            text += page.get_text()
    except Exception as e:
        print(f"Error al procesar {pdf_path} con PyMuPDF: {e}")
    return text

# Función para extraer texto de un PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
        # Si no se extrajo texto, usar OCR como respaldo
        if not text.strip():
            print(f"[Advertencia] No se extrajo texto del archivo: {pdf_path}. Intentando con OCR...")
            text = extract_text_with_paddleocr(pdf_path)
            # Si aún no se extrajo texto, intentar con PyMuPDF
            if not text.strip():
                print(f"[Advertencia] OCR no extrajo texto del archivo: {pdf_path}. Intentando con PyMuPDF...")
                text = extract_text_with_pymupdf(pdf_path)
                if not text.strip():
                    print(f"[Advertencia] PyMuPDF no extrajo texto del archivo: {pdf_path}.")
                    text = ""

    except Exception as e:
        print(f"Error al procesar {pdf_path}: {e}")
    return text

# Función para extraer texto de una imagen utilizando OCR (pytesseract)
def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang="spa")  # Asumiendo que el contenido está en español
    except Exception as e:
        print(f"Error al procesar {image_path}: {e}")
        text = ""
    return text

# Función para procesar todos los PDFs de una carpeta
def process_pdf_files(directory):
    documents = []
    for filename in os.listdir(directory):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(directory, filename)
            text = extract_text_from_pdf(pdf_path)
            
            # Validar si se extrajo texto del PDF
            if not text.strip():
                print(f"[Advertencia] No se extrajo texto del archivo: {pdf_path}")
                continue
            
            documents.append({
                'file_name': filename,
                'doc_type': 'pdf',
                'content': text
            })
            print(f"[PDF] Procesado: {filename}")
    return documents

# Función para procesar todas las imágenes de una carpeta
def process_image_files(directory):
    documents = []
    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
    for filename in os.listdir(directory):
        if filename.lower().endswith(valid_extensions):
            img_path = os.path.join(directory, filename)
            text = extract_text_from_image(img_path)
            documents.append({
                'file_name': filename,
                'doc_type': 'image',
                'content': text
            })
            print(f"[Imagen] Procesado: {filename}")
    return documents



def insert_document(conn, doc):
    query = """
        INSERT INTO Documents (product_id, file_name, doc_type, content)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (file_name) DO UPDATE SET
            content = EXCLUDED.content,
            created_at = CURRENT_TIMESTAMP
    """
    # En este ejemplo, product_id se asigna como None, ya que no está relacionado directamente.
    params = (None, doc['file_name'], doc['doc_type'], doc['content'])
    with conn.cursor() as cur:
        cur.execute(query, params)
    conn.commit()


def main():
    # Rutas de las carpetas de PDFs e imágenes
    #pdf_dir = '/Users/elvysbatzibal/EBSolTech/OpenShareTechnology/intecap52/data/pdfs'
    pdf_dir = '/Users/elvysbatzibal/EBSolTech/OpenShareTechnology/intecap52/data/dpis'
    img_dir = '/Users/elvysbatzibal/EBSolTech/OpenShareTechnology/intecap52/data/img'
    output_dir = '/Users/elvysbatzibal/EBSolTech/OpenShareTechnology/intecap52/data/output'

    # create output directory if not exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print("Ingesta de PDFs...")
    pdf_documents = process_pdf_files(pdf_dir)
    
    print("Ingesta de Imágenes...")
    image_documents = process_image_files(img_dir)
    
    # Unir ambos conjuntos de documentos
    all_documents = pdf_documents + image_documents
    
    # Conexión a PostgreSQL
    conn = psycopg2.connect(
        dbname="intecap52",
        user="admin",
        password="secret",
        host="localhost",
        port="5432"
    )
    
     # Save to txt files 
    for doc in all_documents:
        # Si el contenido length es mayor a cero , guardar en un archivo de texto
        if len(doc['content']) > 0:
            print(f"Guardando archivo: {doc['file_name']}.txt")
            with open(f"{output_dir}/{doc['file_name']}.txt", "w") as f:
                f.write(doc['content'])     
              


       # Inserción de cada documento en la base de datos
    for doc in all_documents:
        if len(doc['content']) > 0:
            insert_document(conn, doc)
            print(f"Documento insertado: {doc['file_name']}")
    
    conn.close()
    print("Ingesta completada.")

if __name__ == '__main__':
    main()