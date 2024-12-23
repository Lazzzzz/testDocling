import asyncio
import io
import traceback
from typing import Dict

from PyPDF2 import PdfReader
from docling.datamodel.base_models import DocumentStream
from docling.document_converter import DocumentConverter
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from oceer_document import OceerDocument

app = FastAPI()
converter = DocumentConverter()


class DocumentSuccessResponse(BaseModel):
    oceer_document: Dict


class ErrorResponse(BaseModel):
    error: str


def convert_pdf_sync(file_bytes: bytes, filename: str) -> OceerDocument:
    """
    Fonction synchrone qui gère la lecture du PDF,
    la conversion docling et la génération d'un OceerDocument.
    """
    # Lire le PDF
    stream = io.BytesIO(file_bytes)
    pdf_reader = PdfReader(stream)

    total_pages = len(pdf_reader.pages)
    if total_pages == 0:
        raise ValueError("Uploaded PDF is empty.")

    # Remettre le curseur du stream au début
    stream.seek(0)

    # Convertir via docling
    doc = DocumentStream(name=filename, stream=stream)
    conversion_result = converter.convert(doc)

    # Construire l'OceerDocument
    document = OceerDocument()
    for page_no in range(1, total_pages + 1):
        page_markdown = conversion_result.document.export_to_markdown(page_no=page_no)
        document.page_text.append(page_markdown)

    return document


@app.post(
    "/process-pdf",
    responses={
        200: {"model": DocumentSuccessResponse},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def process_pdf(uploaded_file: UploadFile = File(...)):
    try:
        file_bytes = await uploaded_file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="No file content provided.")

        # On exécute la partie bloquante (lecture & conversion PDF) dans un thread séparé
        loop = asyncio.get_event_loop()
        document = await loop.run_in_executor(
            None,
            convert_pdf_sync,
            file_bytes,
            uploaded_file.filename or "",
        )

        return DocumentSuccessResponse(oceer_document=document.to_json())

    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc:
        error_trace = traceback.format_exc()
        print(f"Exception in process_pdf: {error_trace}")
        return JSONResponse(
            status_code=500,
            content={"error": f"An unexpected error occurred: {str(exc)}"},
        )
