import os

import uvicorn
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from docling.document_converter import DocumentConverter
import tempfile

app = FastAPI()


@app.post("/test")
async def test():
    return 'Slt'

