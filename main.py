import os
import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from summarizer import summarize_text, clean_text
from PyPDF2 import PdfReader
import docx

load_dotenv()

app = FastAPI(title="AI Content Summarizer")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/summarize")
async def summarize_endpoint(text: str = Form(...), length: str = Form("medium"), action_items: bool = Form(False)):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    summary = summarize_text(text, length, action_items)
    return JSONResponse({"summary": summary})

def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n".join([page.extract_text() or "" for page in reader.pages])

def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join([p.text for p in doc.paragraphs])

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), length: str = Form("medium"), action_items: bool = Form(False)):
    content = await file.read()
    if file.filename.lower().endswith(".pdf"):
        extracted = extract_text_from_pdf(content)
    elif file.filename.lower().endswith((".docx", ".doc")):
        extracted = extract_text_from_docx(content)
    elif file.filename.lower().endswith(".txt"):
        extracted = content.decode("utf-8", errors="ignore")
    else:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, TXT supported.")

    cleaned = clean_text(extracted)
    summary = summarize_text(cleaned, length, action_items)
    return JSONResponse({"filename": file.filename, "summary": summary})
