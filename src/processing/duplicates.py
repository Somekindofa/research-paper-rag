"""
Duplicate Detection - SHA256 checksum-based deduplication for PDFs.
Persists checksums to JSON for cross-session tracking.
"""
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import settings


def compute_checksum(file_path: Path | str) -> str:
    """
    Compute SHA256 checksum of a file.
    
    Args:
        file_path: Path to the file.
    
    Returns:
        Hex digest string of SHA256 hash.
    """
    sha256 = hashlib.sha256()
    file_path = Path(file_path)
    
    with open(file_path, "rb") as f:
        # Read in chunks for memory efficiency with large PDFs
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    
    return sha256.hexdigest()


class ChecksumStore:
    """
    Manages checksum storage and lookup for duplicate detection.
    Persists to JSON file.
    """
    
    def __init__(self, store_path: str | None = None):
        """
        Initialize checksum store.
        
        Args:
            store_path: Path to JSON file. Defaults to config setting.
        """
        config = settings()
        self.store_path = Path(store_path or config["metadata"]["checksums_file"])
        self._data: dict[str, Any] = self._load()
    
    def _load(self) -> dict[str, Any]:
        """Load checksums from disk."""
        if self.store_path.exists():
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load checksums file: {e}")
                return {"checksums": {}, "last_scan": None}
        return {"checksums": {}, "last_scan": None}
    
    def _save(self) -> None:
        """Save checksums to disk."""
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self._data["last_scan"] = datetime.now().isoformat()
        
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)
    
    def is_known(self, file_path: Path | str) -> bool:
        """
        Check if file has been processed before.
        
        Args:
            file_path: Path to check.
        
        Returns:
            True if checksum exists in store.
        """
        checksum = compute_checksum(file_path)
        return checksum in self._data["checksums"]
    
    def add(self, file_path: Path | str, doc_id: str | None = None) -> str:
        """
        Add file checksum to store.
        
        Args:
            file_path: Path to file.
            doc_id: Optional document ID to associate.
        
        Returns:
            The computed checksum.
        """
        file_path = Path(file_path)
        checksum = compute_checksum(file_path)
        
        self._data["checksums"][checksum] = {
            "filename": file_path.name,
            "path": str(file_path),
            "doc_id": doc_id,
            "added": datetime.now().isoformat()
        }
        self._save()
        return checksum
    
    def get_doc_id(self, file_path: Path | str) -> str | None:
        """Get document ID for a file if it exists."""
        checksum = compute_checksum(file_path)
        entry = self._data["checksums"].get(checksum)
        return entry["doc_id"] if entry else None
    
    def remove(self, checksum: str) -> bool:
        """Remove a checksum from store."""
        if checksum in self._data["checksums"]:
            del self._data["checksums"][checksum]
            self._save()
            return True
        return False
    
    def get_all_checksums(self) -> set[str]:
        """Get all known checksums."""
        return set(self._data["checksums"].keys())
    
    def get_all_known_paths(self) -> set[str]:
        """Get all known file paths."""
        return {
            entry["path"] 
            for entry in self._data["checksums"].values()
        }
    
    def count(self) -> int:
        """Get number of tracked files."""
        return len(self._data["checksums"])


def find_new_pdfs(pdf_paths: list[Path], store: ChecksumStore | None = None) -> list[Path]:
    """
    Filter list of PDFs to only new (unprocessed) ones.
    
    Args:
        pdf_paths: List of PDF paths to check.
        store: Optional ChecksumStore instance. Creates new one if None.
    
    Returns:
        List of paths not yet in checksum store.
    """
    if store is None:
        store = ChecksumStore()
    
    new_pdfs = []
    for path in pdf_paths:
        if not store.is_known(path):
            new_pdfs.append(path)
    
    return new_pdfs


if __name__ == "__main__":
    # Quick test
    store = ChecksumStore()
    print(f"Tracked files: {store.count()}")
