import os
from typing import List
from PyPDF2 import PdfReader

def load_pdf(file_path: str) -> str:
    """Read PDF file and return full text."""
    text = ""
    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def load_txt(file_path: str) -> str:
    """Read TXT file and return full text."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks.
    Args:
        text: full text
        chunk_size: number of characters per chunk
        overlap: number of characters to overlap between chunks
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap  # move start forward
    return chunks
