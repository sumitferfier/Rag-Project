from pathlib import Path
import fitz
from langchain_community.document_loaders import (
    PyPDFLoader
)
class PdfService:
    def load_pdf(
        self,
        pdf_path: str
    ):

        loader = PyPDFLoader(
            pdf_path
        )
        documents = loader.load()
        return documents