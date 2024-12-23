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


# ------------------------------------------------
# Pydantic Models: for success and error responses
# ------------------------------------------------

class DocumentSuccessResponse(BaseModel):
    """
    Represents a successful response containing
    the text of the processed OceerDocument.
    """
    oceer_document: Dict


class ErrorResponse(BaseModel):
    """
    Represents an error response containing
    a description of what went wrong.
    """
    error: str


# --------------------------------------------------------------------
# Endpoint to accept a PDF via file upload and process it accordingly
# --------------------------------------------------------------------
@app.post(
    "/process-pdf",
    responses={
        200: {"model": DocumentSuccessResponse},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def process_pdf(uploaded_file: UploadFile = File(...)):
    """
    Receives a PDF file upload, extracts text using the docling library,
    and returns the processed document as JSON.
    """

    try:
        # Read the uploaded file into a BytesIO stream
        file_bytes = await uploaded_file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="No file content provided.")

        stream = io.BytesIO(file_bytes)
        pdf_reader = PdfReader(stream)

        # If the PDF has no pages, handle gracefully
        total_pages = len(pdf_reader.pages)
        if total_pages == 0:
            raise HTTPException(status_code=400, detail="Uploaded PDF is empty.")

        # Reset stream position after reading
        stream.seek(0)

        # Convert the PDF to a DocumentStream (required by docling)
        doc = DocumentStream(name=uploaded_file.filename or "", stream=stream)
        conversion_result = converter.convert(doc)

        # Build an OceerDocument from the converted data
        document = OceerDocument()
        for page_no in range(1, total_pages + 1):
            page_markdown = conversion_result.document.export_to_markdown(page_no=page_no)
            document.page_text.append(page_markdown)

        # Return a well-structured success response
        return DocumentSuccessResponse(oceer_document=document.to_json())

    except HTTPException as http_exc:
        # If we intentionally raised an HTTPException (e.g., 400), re-raise it.
        raise http_exc

    except Exception as exc:
        # Capture full traceback for logging/debugging
        error_trace = traceback.format_exc()
        # In production, consider logging instead of printing
        print(f"Exception in process_pdf: {error_trace}")

        # Return a standardized 500 response with some error detail
        return JSONResponse(
            status_code=500,
            content={"error": f"An unexpected error occurred: {str(exc)}"},
        )
