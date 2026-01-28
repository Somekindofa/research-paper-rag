"""
PDF Scanner - Recursively scan folders for PDF files.
Handles Better BibTeX export folder structure (single subfolder depth).
"""
import os
from pathlib import Path
from typing import Generator

from src.config import settings


def scan_pdf_folder(
    folder_path: str | None = None,
    max_depth: int | None = None
) -> Generator[Path, None, None]:
    """
    Scan folder recursively for PDF files.
    
    Args:
        folder_path: Path to scan. Defaults to config setting.
        max_depth: Maximum subfolder depth. Defaults to config setting.
    
    Yields:
        Path objects for each PDF found.
    """
    config = settings()
    folder = Path(folder_path or config["pdf"]["folder_path"])
    depth = max_depth if max_depth is not None else config["pdf"]["scan_depth"]
    extensions = config["pdf"]["supported_extensions"]
    
    if not folder.exists():
        print(f"Warning: PDF folder does not exist: {folder}")
        return
    
    yield from _scan_recursive(folder, extensions, depth, current_depth=0)


def _scan_recursive(
    folder: Path,
    extensions: list[str],
    max_depth: int,
    current_depth: int
) -> Generator[Path, None, None]:
    """Recursively scan with depth limit."""
    try:
        for entry in folder.iterdir():
            if entry.is_file() and entry.suffix.lower() in extensions:
                yield entry
            elif entry.is_dir() and current_depth < max_depth:
                yield from _scan_recursive(
                    entry, extensions, max_depth, current_depth + 1
                )
    except PermissionError as e:
        print(f"Permission denied scanning: {folder} - {e}")


def get_pdf_list(folder_path: str | None = None) -> list[Path]:
    """
    Get all PDFs as a list (non-generator version).
    
    Args:
        folder_path: Optional override for folder path.
    
    Returns:
        List of Path objects for all PDFs found.
    """
    return list(scan_pdf_folder(folder_path))


def count_pdfs(folder_path: str | None = None) -> int:
    """Count PDFs in folder without loading all paths into memory."""
    return sum(1 for _ in scan_pdf_folder(folder_path))


if __name__ == "__main__":
    # Quick test
    pdfs = get_pdf_list()
    print(f"Found {len(pdfs)} PDFs:")
    for pdf in pdfs[:10]:  # Show first 10
        print(f"  - {pdf.name}")
