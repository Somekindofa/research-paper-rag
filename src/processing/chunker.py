"""
Text Chunker - Split documents into chunks for embedding.
Uses semantic-aware chunking with configurable size and overlap.
"""
from dataclasses import dataclass
from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import settings
from src.processing.pdf_parser import PDFDocument


@dataclass
class Chunk:
    """Represents a text chunk with metadata."""
    content: str
    chunk_index: int
    doc_id: str
    metadata: dict[str, Any]


def create_text_splitter(
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
    separators: list[str] | None = None
) -> RecursiveCharacterTextSplitter:
    """
    Create a text splitter with configuration.
    
    Args:
        chunk_size: Max characters per chunk. Defaults to config.
        chunk_overlap: Overlap between chunks. Defaults to config.
        separators: Split priority order. Defaults to config.
    
    Returns:
        Configured RecursiveCharacterTextSplitter.
    """
    config = settings()["chunking"]
    
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or config["chunk_size"],
        chunk_overlap=chunk_overlap or config["chunk_overlap"],
        separators=separators or config["separators"],
        length_function=len,
        is_separator_regex=False,
    )


def chunk_document(
    doc: PDFDocument,
    doc_id: str,
    splitter: RecursiveCharacterTextSplitter | None = None
) -> list[Chunk]:
    """
    Split a document into chunks with metadata.
    
    Args:
        doc: Parsed PDF document.
        doc_id: Unique identifier for the document.
        splitter: Optional pre-configured splitter.
    
    Returns:
        List of Chunk objects with metadata.
    """
    if splitter is None:
        splitter = create_text_splitter()
    
    # Split text
    text_chunks = splitter.split_text(doc.text)
    
    # Create Chunk objects with metadata
    chunks = []
    for i, content in enumerate(text_chunks):
        # Extract page number if present in chunk
        page_num = _extract_page_number(content)
        
        # Ensure all metadata values are valid (no None values for Chroma)
        chunk = Chunk(
            content=content,
            chunk_index=i,
            doc_id=doc_id,
            metadata={
                "doc_id": doc_id,
                "chunk_index": i,
                "total_chunks": len(text_chunks),
                "title": doc.title or "Unknown",
                "authors": doc.authors or "Unknown",
                "year": doc.year or 0,
                "filename": doc.filename,
                "source_path": doc.path,
                "page_number": page_num if page_num is not None else 0,
            }
        )
        chunks.append(chunk)
    
    return chunks


def _extract_page_number(text: str) -> int | None:
    """Extract page number from chunk text if present."""
    import re
    match = re.search(r"\[Page (\d+)\]", text)
    if match:
        return int(match.group(1))
    return None


def _clean_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """
    Clean metadata to ensure all values are valid for Chroma.
    Chroma doesn't accept None values - convert to appropriate defaults.
    
    Args:
        metadata: Raw metadata dictionary.
    
    Returns:
        Cleaned metadata with no None values.
    """
    cleaned = {}
    for key, value in metadata.items():
        if value is None:
            # Use appropriate default based on common field types
            if key in ["year", "page_number", "chunk_index", "total_chunks"]:
                cleaned[key] = 0
            else:
                cleaned[key] = "Unknown"
        else:
            cleaned[key] = value
    return cleaned


def chunk_text(
    text: str,
    metadata: dict[str, Any] | None = None,
    doc_id: str = "unknown"
) -> list[Chunk]:
    """
    Chunk raw text with optional metadata.
    
    Args:
        text: Text to chunk.
        metadata: Optional metadata to attach.
        doc_id: Document identifier.
    
    Returns:
        List of Chunk objects.
    """
    splitter = create_text_splitter()
    text_chunks = splitter.split_text(text)
    
    base_metadata = metadata or {}
    
    chunks = []
    for i, content in enumerate(text_chunks):
        raw_metadata = {
            **base_metadata,
            "doc_id": doc_id,
            "chunk_index": i,
            "total_chunks": len(text_chunks),
        }
        
        chunk = Chunk(
            content=content,
            chunk_index=i,
            doc_id=doc_id,
            metadata=_clean_metadata(raw_metadata)
        )
        chunks.append(chunk)
    
    return chunks


if __name__ == "__main__":
    # Quick test
    test_text = """
    [Page 1]
    This is the first page of a test document. It contains some introductory
    information about the research topic.
    
    [Page 2]
    This is the second page with more detailed content. The methodology section
    describes the approach used in this study.
    """ * 10  # Repeat to create enough text
    
    chunks = chunk_text(test_text, {"title": "Test Doc"}, doc_id="test_001")
    print(f"Created {len(chunks)} chunks")
    for chunk in chunks[:3]:
        print(f"  Chunk {chunk.chunk_index}: {len(chunk.content)} chars, page={chunk.metadata.get('page_number')}")
