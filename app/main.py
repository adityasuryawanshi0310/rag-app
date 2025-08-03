import os
import requests
from tempfile import NamedTemporaryFile
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from app.rag_pipeline import load_and_chunk, build_vectorstore, get_rag_chain
from app.security import get_current_user
from pathlib import Path

app = FastAPI()

class QueryRequest(BaseModel):
    documents: str
    questions: list[str]

class QueryResponse(BaseModel):
    answers: list[str]

@app.post("/api/v1/hackrx/run", response_model=QueryResponse)
def run_query(payload: QueryRequest, token: str = Depends(get_current_user)):
    # Check if the document is a URL
    if payload.documents.startswith("http://") or payload.documents.startswith("https://"):
        # Download the file temporarily
        response = requests.get(payload.documents)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download document from URL.")
        
        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(response.content)
            tmp_file_path = tmp_file.name
    else:
        tmp_file_path = str(Path(f"app/documents/{payload.documents}"))
        if not os.path.exists(tmp_file_path):
            raise HTTPException(status_code=404, detail="Document not found.")

    # Load and process
    chunks = load_and_chunk(tmp_file_path)
    vectorstore = build_vectorstore(chunks)
    rag_chain = get_rag_chain(vectorstore)

    answers = []
    for question in payload.questions:
        response = rag_chain.invoke({"question": question})
        answers.append(response.content)


    return QueryResponse(answers=answers)
