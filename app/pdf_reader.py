from pathlib import Path
import pymupdf


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF using PyMuPDF."""
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("The supplied file must be a PDF.")

    extracted_pages = []

    with pymupdf.open(str(path)) as document:
        for page_number, page in enumerate(document, start=1):
            page_text = page.get_text("text")

            if page_text.strip():
                extracted_pages.append(
                    f"\n--- Page {page_number} ---\n{page_text}"
                )

    return "\n".join(extracted_pages)


def main():
    project_root = Path(__file__).resolve().parent.parent

    documents = [
        project_root / "corpus" / "government_rules" / "GFR2017.pdf",
        project_root / "corpus" / "policy_orders" / "startup_mse_relaxation.pdf",
    ]

    for document in documents:
        print(f"\nReading: {document.name}")

        try:
            text = extract_text_from_pdf(str(document))
            print(f"Extracted characters: {len(text)}")
            print("Text preview:")
            print(text[:500] if text else "No readable text found.")
        except (FileNotFoundError, ValueError) as error:
            print(f"Could not read document: {error}")


if __name__ == "__main__":
    main()