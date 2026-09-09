from pathlib import Path
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from pydantic import BaseModel

class DocumentChunk(BaseModel):
    content: str
    metadata: dict

def parse_pdf(file_path: Path) -> str:
    doc = fitz.open(file_path)
    text = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text.append(page.get_text())
    return "\n".join(text)

def parse_html(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    # Strip script and style elements
    for element in soup(["script", "style", "nav", "footer"]):
        element.decompose()
    return soup.get_text(separator="\n", strip=True)
