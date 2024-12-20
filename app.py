from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from docling.document_converter import DocumentConverter
import tempfile

app = FastAPI()

@app.post("/convert-pdf")
async def convert_pdf(file: UploadFile):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Save the uploaded file to a temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name

        # Convert the PDF to Markdown using DocumentConverter
        converter = DocumentConverter()
        result = converter.convert(temp_file_path)
        large_text = result.document.export_to_markdown()

        return JSONResponse(content={"markdown": large_text})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    finally:
        # Ensure the temporary file is cleaned up
        if temp_file_path:
            import os
            os.remove(temp_file_path)
