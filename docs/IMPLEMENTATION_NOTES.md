# Implementation notes

The semantic layer uses sentence-transformer embeddings and a persistent ChromaDB collection. Each PDF page is split into overlapping text chunks; each chunk stores document name, page number and chunk index as metadata. Query results return the source document and page.

The API does not generate legal advice or final bid eligibility determinations. The screening route preserves the original caller-supplied relaxation flag for compatibility; a production-grade workflow should derive policy evidence from retrieved, verified clauses rather than trust a client boolean.
