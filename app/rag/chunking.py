# app/rag/chunking.py


def chunk_text(text: str, *, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """
    Splits text into overlapping word-based chunks. Overlap helps preserve
    context across chunk boundaries so a fact split across two chunks is
    still retrievable.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks
