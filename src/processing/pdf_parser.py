"""
PDF Parser - Extract text and metadata from PDF files using PyMuPDF.
"""
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF


@dataclass
class PDFDocument:
    """Represents a parsed PDF document."""
    path: str
    filename: str
    text: str
    title: str
    authors: str
    year: str
    num_pages: int
    metadata: dict[str, Any]


def extract_text_from_pdf(file_path: Path | str) -> str:
    """
    Extract all text from a PDF file.
    
    Args:
        file_path: Path to PDF file.
    
    Returns:
        Extracted text as string.
    """
    file_path = Path(file_path)
    text_parts = []
    
    try:
        with fitz.open(file_path) as doc:
            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                if page_text.strip():
                    text_parts.append(f"[Page {page_num + 1}]\n{page_text}")
    except Exception as e:
        print(f"Error extracting text from {file_path.name}: {e}")
        return ""
    
    return "\n\n".join(text_parts)


def extract_metadata_from_pdf(file_path: Path | str) -> dict[str, Any]:
    """
    Extract metadata from PDF file.
    
    Args:
        file_path: Path to PDF file.
    
    Returns:
        Dictionary with metadata fields.
    """
    file_path = Path(file_path)
    
    try:
        with fitz.open(file_path) as doc:
            metadata = doc.metadata or {}
            return {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "keywords": metadata.get("keywords", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "creation_date": metadata.get("creationDate", ""),
                "mod_date": metadata.get("modDate", ""),
                "num_pages": doc.page_count,
            }
    except Exception as e:
        print(f"Error extracting metadata from {file_path.name}: {e}")
        return {"num_pages": 0}


def extract_title_from_text(text: str, fallback: str = "Unknown Title") -> str:
    """
    Attempt to extract title from first page text.
    Falls back to provided string if not found.
    """
    if not text:
        return fallback
    
    # Get first page content
    lines = text.split("\n")[:50]  # First 50 lines
    
    # Look for title patterns (usually early, larger text, may be all caps)
    for line in lines[:20]:
        line = line.strip()
        # Skip empty lines, page numbers, headers
        if not line or len(line) < 10:
            continue
        if line.lower().startswith(("page ", "[page", "abstract", "introduction")):
            continue
        if re.match(r"^\d+$", line):  # Just a number
            continue
        # First substantial line is often title
        if len(line) > 15 and len(line) < 300:
            return line
    
    return fallback


def extract_authors_from_text(text: str) -> str:
    """
    Attempt to extract authors from first page text.
    """
    if not text:
        return "Unknown Authors"
    
    lines = text.split("\n")[:30]
    
    # Look for author patterns (names with commas, "and", affiliations)
    for i, line in enumerate(lines):
        line = line.strip()
        # Authors often contain multiple names separated by comma or "and"
        if " and " in line.lower() or line.count(",") >= 1:
            # Check if it looks like names (capitalized words)
            words = line.split()
            capitalized = sum(1 for w in words if w and w[0].isupper())
            if capitalized > len(words) * 0.5 and len(line) < 500:
                # Likely an author line
                return line
    
    return "Unknown Authors"


def extract_year_from_text(text: str, metadata: dict[str, Any]) -> str:
    """
    Extract publication year from text or metadata.
    """
    # Try metadata first
    creation_date = metadata.get("creation_date", "")
    if creation_date:
        year_match = re.search(r"(19|20)\d{2}", creation_date)
        if year_match:
            return year_match.group()
    
    # Search in first page for year patterns
    if text:
        first_page = text[:3000]  # First ~3000 chars
        # Look for years in typical citation contexts
        year_patterns = [
            r"\b(20[0-2]\d)\b",  # 2000-2029
            r"\b(19[89]\d)\b",   # 1980-1999
        ]
        for pattern in year_patterns:
            matches = re.findall(pattern, first_page)
            if matches:
                # Return most recent year found
                return max(matches)
    
    return "Unknown Year"


def parse_pdf(file_path: Path | str) -> PDFDocument:
    """
    Parse a PDF file and extract text and metadata.
    
    Args:
        file_path: Path to PDF file.
    
    Returns:
        PDFDocument with extracted content.
    """
    file_path = Path(file_path)
    
    # Extract raw data
    text = extract_text_from_pdf(file_path)
    metadata = extract_metadata_from_pdf(file_path)
    
    # Get or infer title
    title = metadata.get("title", "").strip()
    if not title:
        title = extract_title_from_text(text, fallback=file_path.stem)
    
    # Get or infer authors
    authors = metadata.get("author", "").strip()
    if not authors:
        authors = extract_authors_from_text(text)
    
    # Get or infer year
    year = extract_year_from_text(text, metadata)
    
    return PDFDocument(
        path=str(file_path),
        filename=file_path.name,
        text=text,
        title=title,
        authors=authors,
        year=year,
        num_pages=metadata.get("num_pages", 0),
        metadata=metadata
    )


if __name__ == "__main__":
    # Quick test - run with a PDF path as argument
    import sys
    if len(sys.argv) > 1:
        doc = parse_pdf(sys.argv[1])
        print(f"Title: {doc.title}")
        print(f"Authors: {doc.authors}")
        print(f"Year: {doc.year}")
        print(f"Pages: {doc.num_pages}")
        print(f"Text length: {len(doc.text)} chars")
