from pathlib import Path
from typing import Any

import pymupdf

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DOCUMENT_FOLDERS = [
    PROJECT_ROOT / "corpus" / "government_rules",
    PROJECT_ROOT / "corpus" / "policy_orders",
    PROJECT_ROOT / "corpus" / "tender",
]


def verify_citation(
    document_name: str,
    page_number: int,
    supporting_text: str = "",
) -> dict[str, Any]:
    """Check that a cited PDF page exists and optionally contains evidence."""
    if Path(document_name).name != document_name:
        return {
            "verified": False,
            "reason": "Invalid document name.",
        }

    if page_number < 1:
        return {
            "verified": False,
            "reason": "Page number must be at least 1.",
        }

    document_path = next(
        (
            folder / document_name
            for folder in DOCUMENT_FOLDERS
            if (folder / document_name).is_file()
        ),
        None,
    )

    if document_path is None:
        return {
            "verified": False,
            "reason": "Document was not found in the approved corpus.",
        }

    try:
        with pymupdf.open(str(document_path)) as pdf:
            if page_number > len(pdf):
                return {
                    "verified": False,
                    "reason": "Page number exceeds the document length.",
                }

            page_text = pdf[page_number - 1].get_text("text") or ""

        if supporting_text.strip():
            normalized_page = " ".join(page_text.casefold().split())
            normalized_quote = " ".join(supporting_text.casefold().split())

            if normalized_quote not in normalized_page:
                return {
                    "verified": False,
                    "reason": (
                        "The supplied supporting text was not found "
                        "exactly on the cited page."
                    ),
                    "document": document_name,
                    "page": page_number,
                }

        return {
            "verified": True,
            "document": document_name,
            "page": page_number,
            "reason": "The document and cited page exist.",
        }

    except Exception as error:
        return {
            "verified": False,
            "reason": f"Could not read the cited document: {error}",
        }


if __name__ == "__main__":
    result = verify_citation(
        document_name="startup_mse_relaxation.pdf",
        page_number=3,
    )
    print(result)