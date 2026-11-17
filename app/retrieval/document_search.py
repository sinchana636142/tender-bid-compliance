
from pathlib import Path
from typing import Any
import pymupdf

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCUMENT_FOLDERS = [
    PROJECT_ROOT / "corpus" / "government_rules",
    PROJECT_ROOT / "corpus" / "policy_orders",
    PROJECT_ROOT / "corpus" / "tender",
]

def iter_pdf_pages():
    for folder in DOCUMENT_FOLDERS:
        if not folder.exists():
            continue
        for pdf_path in sorted(folder.glob("*.pdf")):
            try:
                with pymupdf.open(str(pdf_path)) as pdf:
                    for page_number, page in enumerate(pdf, start=1):
                        text = (page.get_text("text") or "").strip()
                        if text:
                            yield pdf_path, page_number, text
            except Exception as exc:
                print(f"Warning: cannot read {pdf_path.name}: {exc}")

def search_documents(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    if not query.strip():
        raise ValueError("Search query cannot be empty.")
    if max_results < 1:
        raise ValueError("max_results must be at least 1.")
    words = query.casefold().split()
    results = []
    for path, page, content in iter_pdf_pages():
        lowered = content.casefold()
        matches = [word for word in words if word in lowered]
        if matches:
            results.append({
                "document": path.name, "page": page,
                "matched_terms": matches, "text": content[:2500],
                "source": str(path.relative_to(PROJECT_ROOT))
            })
    results.sort(key=lambda item: len(item["matched_terms"]), reverse=True)
    return results[:max_results]
