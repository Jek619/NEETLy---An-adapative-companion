# backend/app.py
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pdfminer.high_level import extract_text
from typing import List
import asyncio
import tempfile

from backend.db import mongo
from backend import rag

import openai

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY not set. /ask will fail until you set it.")
openai.api_key = OPENAI_API_KEY

app = FastAPI(title="NEET Learning Assistant - Phase1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "NEET Learning Assistant backend is running!"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/seed_chunks")
async def seed_chunks(payload: dict):
    """
    Payload example:
    {
      "chunks": [
        {"subject":"Physics","chapter":"Motion","page":1,"text":"Newton's laws ..."},
        ...
      ]
    }
    """
    chunks = payload.get("chunks") or []
    if not chunks:
        raise HTTPException(status_code=400, detail="No chunks provided")
    col = mongo.ncert_chunks()
    await col.insert_many(chunks)
    added = await rag.embed_and_add(chunks)
    return {"seeded": len(chunks), "vectors_added": added}

@app.post("/ingest_pdf")
async def ingest_pdf(file: UploadFile = File(...)):
    """
    Upload an NCERT PDF. We extract text, split by paragraph and store as chunks.
    This endpoint is synchronous for simplicity but uses pdfminer which can be slow for big PDFs.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF supported")
    # save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    # extract text (blocking) -> use run_in_executor
    loop = asyncio.get_running_loop()
    def _extract():
        return extract_text(tmp_path)
    text = await loop.run_in_executor(None, _extract)

    # naive splitting: by double newline or by lines if needed
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    for i, p in enumerate(paras):
        chunks.append({
            "subject": "unknown",
            "chapter": "unknown",
            "page": i+1,
            "text": p
        })
    if chunks:
        col = mongo.ncert_chunks()
        await col.insert_many(chunks)
        added = await rag.embed_and_add(chunks)
        return {"ingested_paragraphs": len(chunks), "vectors_added": added}
    return {"ingested_paragraphs": 0, "vectors_added": 0}

@app.post("/ask")
async def ask(payload: dict):
    """
    Payload: {"question": "Explain osmosis"}
    Returns: {answer: "...", retrieved: [...]}
    """
    q = (payload or {}).get("question")
    if not q:
        raise HTTPException(status_code=400, detail="Provide 'question' in payload")
    # retrieve top chunks
    retrieved = await rag.retrieve(q, k=5)

    # build context from retrieved
    context_parts = []
    for r in retrieved:
        md = r.get("metadata", {})
        context_parts.append(f"[Chapter: {md.get('chapter')} | Page: {md.get('page')}]\n{md.get('text_preview')}")
    context = "\n\n".join(context_parts) or "No NCERT context found."

    # construct prompt to instruct model to use only the provided context
    prompt_user = (
        "You are a NEET instructor. Use ONLY the provided NCERT context to answer the question.\n\n"
        f"Context:\n{context}\n\nQuestion: {q}\n\nAnswer concisely and show NCERT references if present."
    )

    if not OPENAI_API_KEY:
        # return retrieved content so user can inspect
        return JSONResponse(status_code=500, content={
            "error": "OPENAI_API_KEY not set. Set env var OPENAI_API_KEY to use /ask.",
            "retrieved": retrieved
        })

    # call OpenAI ChatCompletion (blocking) inside executor
    loop = asyncio.get_running_loop()
    def _call_openai():
        # use ChatCompletion if available; adjust model name as per your access
        resp = openai.ChatCompletion.create(
            model=os.environ.get("CHAT_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You are a helpful NEET instructor. Use only the context provided."},
                {"role": "user", "content": prompt_user}
            ],
            max_tokens=400,
            temperature=0.0,
        )
        return resp
    try:
        resp = await loop.run_in_executor(None, _call_openai)
        answer = resp["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {e}")

    return {"answer": answer, "retrieved": retrieved}

