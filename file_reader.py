import pymupdf as fitz
import docx
from PIL import Image
import os
import chardet
import requests


def read_txt(file_path):
 try:
    with open(file_path, 'rb') as f:
            raw_data = f.read()
            encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()
 except Exception as e:
        raise ValueError(f"Error reading text file: {e}")

def read_docx(file_path):
 try:
    doc1= docx.Document(file_path)
    return '\n'.join([para.text for para in doc1.paragraphs])
 except Exception as e:
        raise ValueError(f"Error reading docx: {e}")

def read_pdf(file_path):
 try:
    doc = fitz.open(file_path)
    text = ''
    for page in doc:
        text += page.get_text()
    doc.close()  
    return text
 except Exception as e:
        raise ValueError(f"Error reading PDF: {e}")
def read_image(file_path):
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(
                'https://api.ocr.space/parse/image',
                files={'filename': f},
                data={
                    'apikey': 'K88180486988957',
                    'language': 'eng',
                },
            )
        result = response.json()
        if result.get("IsErroredOnProcessing"):
            raise ValueError(result.get("ErrorMessage", "OCR failed"))
        return result['ParsedResults'][0]['ParsedText']
    except Exception as e:
        raise ValueError(f"Cloud OCR failed: {e}")
def extract_text(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == '.txt':
        return read_txt(file_path)
    elif ext == '.docx':
        return read_docx(file_path)
    elif ext == '.pdf':
        return read_pdf(file_path)
    elif ext in ['.jpg', '.jpeg', '.png']:
        return read_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
