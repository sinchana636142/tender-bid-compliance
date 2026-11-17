
from pathlib import Path
from typing import Any
import pymupdf
from app.retrieval.document_search import DOCUMENT_FOLDERS

def verify_citation(document_name: str, page_number: int, supporting_text: str = "") -> dict[str, Any]:
    if Path(document_name).name != document_name:
        return {"verified":False,"reason":"Invalid document name."}
    if page_number < 1:
        return {"verified":False,"reason":"Page number must be at least 1."}
    path = next((folder / document_name for folder in DOCUMENT_FOLDERS if (folder / document_name).is_file()), None)
    if path is None:
        return {"verified":False,"reason":"Document was not found in the approved corpus."}
    try:
        with pymupdf.open(str(path)) as pdf:
            if page_number > len(pdf):
                return {"verified":False,"reason":"Page number exceeds document length."}
            page_text = pdf[page_number - 1].get_text("text") or ""
        if supporting_text.strip():
            norm = lambda s: " ".join(s.casefold().split())
            if norm(supporting_text) not in norm(page_text):
                return {"verified":False,"reason":"Supporting text was not found on the cited page.",
                        "document":document_name,"page":page_number}
        return {"verified":True,"document":document_name,"page":page_number,"reason":"Document and cited page exist."}
    except Exception as exc:
        return {"verified":False,"reason":f"Could not read citation: {exc}"}
