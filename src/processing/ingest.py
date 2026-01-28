"""
Ingestion Pipeline - Orchestrates PDF scanning, parsing, chunking, and embedding.
"""
import uuid
from pathlib import Path
from typing import Callable

from src.config import settings
from src.processing.pdf_scanner import get_pdf_list
from src.processing.duplicates import ChecksumStore, find_new_pdfs
from src.processing.pdf_parser import parse_pdf, PDFDocument
from src.processing.chunker import chunk_document, Chunk


def generate_doc_id() -> str:
    """Generate a unique document ID."""
    return f"doc_{uuid.uuid4().hex[:12]}"


def ingest_pdf(
    pdf_path: Path,
    checksum_store: ChecksumStore,
    progress_callback: Callable[[str], None] | None = None
) -> tuple[PDFDocument, list[Chunk]] | None:
    """
    Ingest a single PDF file.
    
    Args:
        pdf_path: Path to PDF file.
        checksum_store: Checksum store for duplicate tracking.
        progress_callback: Optional callback for progress updates.
    
    Returns:
        Tuple of (PDFDocument, list[Chunk]) or None if failed/duplicate.
    """
    def log(msg: str):
        if progress_callback:
            progress_callback(msg)
        else:
            print(msg)
    
    # Check for duplicates
    if checksum_store.is_known(pdf_path):
        log(f"Skipping duplicate: {pdf_path.name}")
        return None
    
    log(f"Processing: {pdf_path.name}")
    
    try:
        # Parse PDF
        doc = parse_pdf(pdf_path)
        
        if not doc.text.strip():
            log(f"Warning: No text extracted from {pdf_path.name}")
            return None
        
        # Generate doc ID and chunk
        doc_id = generate_doc_id()
        chunks = chunk_document(doc, doc_id)
        
        # Register in checksum store
        checksum_store.add(pdf_path, doc_id)
        
        log(f"Created {len(chunks)} chunks from {pdf_path.name}")
        return (doc, chunks)
    
    except Exception as e:
        log(f"Error processing {pdf_path.name}: {e}")
        return None


def ingest_folder(
    folder_path: str | None = None,
    progress_callback: Callable[[str], None] | None = None
) -> tuple[list[PDFDocument], list[Chunk]]:
    """
    Ingest all new PDFs from a folder.
    
    Args:
        folder_path: Path to scan. Defaults to config setting.
        progress_callback: Optional callback for progress updates.
    
    Returns:
        Tuple of (list of parsed docs, list of all chunks).
    """
    def log(msg: str):
        if progress_callback:
            progress_callback(msg)
        else:
            print(msg)
    
    # Initialize
    checksum_store = ChecksumStore()
    config = settings()
    folder = folder_path or config["pdf"]["folder_path"]
    
    # Scan for PDFs
    log(f"Scanning folder: {folder}")
    all_pdfs = get_pdf_list(folder)
    log(f"Found {len(all_pdfs)} PDF files")
    
    # Filter to new ones
    new_pdfs = find_new_pdfs(all_pdfs, checksum_store)
    log(f"New files to process: {len(new_pdfs)}")
    
    if not new_pdfs:
        return ([], [])
    
    # Process each PDF
    all_docs = []
    all_chunks = []
    
    for i, pdf_path in enumerate(new_pdfs):
        log(f"[{i+1}/{len(new_pdfs)}] Processing {pdf_path.name}")
        result = ingest_pdf(pdf_path, checksum_store, progress_callback)
        
        if result:
            doc, chunks = result
            all_docs.append(doc)
            all_chunks.extend(chunks)
    
    log(f"Ingestion complete: {len(all_docs)} documents, {len(all_chunks)} chunks")
    return (all_docs, all_chunks)


def get_pending_pdfs(folder_path: str | None = None) -> list[Path]:
    """
    Get list of PDFs that haven't been processed yet.
    
    Args:
        folder_path: Path to scan. Defaults to config setting.
    
    Returns:
        List of new PDF paths.
    """
    config = settings()
    folder = folder_path or config["pdf"]["folder_path"]
    
    checksum_store = ChecksumStore()
    all_pdfs = get_pdf_list(folder)
    return find_new_pdfs(all_pdfs, checksum_store)


def get_stats() -> dict:
    """Get ingestion statistics."""
    checksum_store = ChecksumStore()
    config = settings()
    
    all_pdfs = get_pdf_list()
    new_pdfs = find_new_pdfs(all_pdfs, checksum_store)
    
    return {
        "total_pdfs_in_folder": len(all_pdfs),
        "processed_pdfs": checksum_store.count(),
        "pending_pdfs": len(new_pdfs),
        "pdf_folder": config["pdf"]["folder_path"],
    }


if __name__ == "__main__":
    # Quick test
    stats = get_stats()
    print("Ingestion Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
