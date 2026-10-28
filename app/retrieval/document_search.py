from pathlib import Path
from typing import Any

import pymupdf

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DOCUMENT_FOLDERS = [
    PROJECT_ROOT / "corpus" / "government_rules",
    PROJECT_ROOT / "corpus" / "policy_orders",
    PROJECT_ROOT / "corpus" / "tender",
]


def search_documents(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """Search local PDF documents for pages containing the query."""
    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    if max_results < 1:
        raise ValueError("max_results must be at least 1.")

    results = []
    query_words = query.casefold().split()

    for folder in DOCUMENT_FOLDERS:
        if not folder.exists():
            continue

        for pdf_path in folder.glob("*.pdf"):
            try:
                with pymupdf.open(str(pdf_path)) as pdf:
                    for page_number, page in enumerate(pdf, start=1):
                        page_text = page.get_text("text") or ""
                        page_lower = page_text.casefold()

                        matched_words = [
                            word for word in query_words if word in page_lower
                        ]

                        if not matched_words:
                            continue

                        results.append(
                            {
                                "document": pdf_path.name,
                                "page": page_number,
                                "matched_terms": matched_words,
                                "text": page_text[:2500],
                            }
                        )

            except Exception as error:
                print(f"Warning: Could not search {pdf_path.name}: {error}")

    results.sort(
        key=lambda result: len(result["matched_terms"]),
        reverse=True,
    )

    return results[:max_results]


if __name__ == "__main__":
    matches = search_documents("startup turnover experience")

    if not matches:
        print("No matching pages found.")
    else:
        for result in matches:
            print(f"\nDocument: {result['document']}")
            print(f"Page: {result['page']}")
            print(f"Matched terms: {', '.join(result['matched_terms'])}")
            print(result["text"][:500])
            print("-" * 60)