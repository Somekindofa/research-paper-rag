"""
Vector Store - Chroma wrapper with MMR search support.
Handles document storage, retrieval, and management.
"""
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings

from src.config import settings
from src.processing.chunker import Chunk
from src.retrieval.embeddings import get_embedding_model, embed_documents


class VectorStore:
    """
    Chroma vector store wrapper with MMR (Maximal Marginal Relevance) support.
    """
    
    def __init__(
        self,
        persist_directory: str | None = None,
        collection_name: str | None = None,
    ):
        """
        Initialize vector store.
        
        Args:
            persist_directory: Path for persistence. Defaults to config.
            collection_name: Collection name. Defaults to config.
        """
        config = settings()["chroma"]
        
        self.persist_directory = persist_directory or config["persist_directory"]
        self.collection_name = collection_name or config["collection_name"]
        
        # Ensure directory exists
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize Chroma client with persistence
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False),
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},  # Cosine similarity
        )
        
        print(f"Vector store initialized: {self.collection.count()} documents")
    
    def add_chunks(self, chunks: list[Chunk]) -> int:
        """
        Add chunks to the vector store.
        
        Args:
            chunks: List of Chunk objects to add.
        
        Returns:
            Number of chunks added.
        """
        if not chunks:
            return 0
        
        # Chroma has a max batch size limit (~5461), so we batch the additions
        batch_size = 1000  # Safe batch size well below the limit
        total_added = 0
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            # Prepare data for this batch
            texts = [chunk.content for chunk in batch]
            ids = [f"{chunk.doc_id}_{chunk.chunk_index}" for chunk in batch]
            
            # Clean metadata to ensure no None values (Chroma requirement)
            metadatas = []
            for chunk in batch:
                cleaned = {}
                for key, value in chunk.metadata.items():
                    if value is None:
                        # Default based on key type
                        if key in ["year", "page_number", "chunk_index", "total_chunks"]:
                            cleaned[key] = 0
                        else:
                            cleaned[key] = "Unknown"
                    else:
                        cleaned[key] = value
                metadatas.append(cleaned)
            
            # Generate embeddings
            print(f"Generating embeddings for batch {i//batch_size + 1} ({len(texts)} chunks)...")
            embeddings = embed_documents(texts)
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )
            
            total_added += len(batch)
            print(f"Added {total_added}/{len(chunks)} chunks to vector store")
        
        return total_added
    
    def similarity_search(
        self,
        query_embedding: list[float],
        k: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Simple similarity search.
        
        Args:
            query_embedding: Query embedding vector.
            k: Number of results. Defaults to config.
        
        Returns:
            List of results with content, metadata, and score.
        """
        config = settings()["retrieval"]
        k = k or config["k"]
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )
        
        return self._format_results(results)
    
    def mmr_search(
        self,
        query_embedding: list[float],
        k: int | None = None,
        fetch_k: int | None = None,
        lambda_mult: float | None = None,
    ) -> list[dict[str, Any]]:
        """
        Maximal Marginal Relevance search for diverse results.
        
        MMR balances relevance to query with diversity among results.
        Higher lambda = more relevance, lower lambda = more diversity.
        
        Args:
            query_embedding: Query embedding vector.
            k: Final number of results. Defaults to config.
            fetch_k: Initial pool size. Defaults to config.
            lambda_mult: Diversity factor (0-1). Defaults to config.
        
        Returns:
            List of diverse, relevant results.
        """
        config = settings()["retrieval"]
        k = k or config["k"]
        fetch_k = fetch_k or config["fetch_k"]
        lambda_mult = lambda_mult if lambda_mult is not None else config["lambda_mult"]
        
        # Get initial candidates
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=fetch_k,
            include=["documents", "metadatas", "distances", "embeddings"],
        )
        
        if not results["ids"][0]:
            return []
        
        # Apply MMR algorithm
        candidate_embeddings = results["embeddings"][0]
        candidate_docs = results["documents"][0]
        candidate_metadatas = results["metadatas"][0]
        candidate_distances = results["distances"][0]
        candidate_ids = results["ids"][0]
        
        selected_indices = self._mmr_selection(
            query_embedding=query_embedding,
            candidate_embeddings=candidate_embeddings,
            k=k,
            lambda_mult=lambda_mult,
        )
        
        # Format selected results
        output = []
        for idx in selected_indices:
            output.append({
                "id": candidate_ids[idx],
                "content": candidate_docs[idx],
                "metadata": candidate_metadatas[idx],
                "distance": candidate_distances[idx],
                "score": 1 - candidate_distances[idx],  # Convert distance to similarity
            })
        
        return output
    
    def _mmr_selection(
        self,
        query_embedding: list[float],
        candidate_embeddings: list[list[float]],
        k: int,
        lambda_mult: float,
    ) -> list[int]:
        """
        MMR selection algorithm.
        
        Iteratively selects documents that are:
        - Similar to the query (relevance)
        - Dissimilar to already selected documents (diversity)
        """
        import numpy as np
        
        query_embedding = np.array(query_embedding)
        candidate_embeddings = np.array(candidate_embeddings)
        
        # Compute query similarities
        query_similarities = np.dot(candidate_embeddings, query_embedding)
        
        selected = []
        remaining = list(range(len(candidate_embeddings)))
        
        for _ in range(min(k, len(remaining))):
            if not remaining:
                break
            
            if not selected:
                # First selection: most similar to query
                best_idx = remaining[np.argmax([query_similarities[i] for i in remaining])]
            else:
                # MMR score: lambda * relevance - (1-lambda) * max_similarity_to_selected
                mmr_scores = []
                selected_embeddings = candidate_embeddings[selected]
                
                for idx in remaining:
                    relevance = query_similarities[idx]
                    
                    # Max similarity to any selected document
                    similarities_to_selected = np.dot(
                        selected_embeddings, candidate_embeddings[idx]
                    )
                    max_sim_to_selected = np.max(similarities_to_selected)
                    
                    mmr_score = lambda_mult * relevance - (1 - lambda_mult) * max_sim_to_selected
                    mmr_scores.append(mmr_score)
                
                best_idx = remaining[np.argmax(mmr_scores)]
            
            selected.append(best_idx)
            remaining.remove(best_idx)
        
        return selected
    
    def _format_results(self, results: dict) -> list[dict[str, Any]]:
        """Format Chroma results into standard format."""
        output = []
        
        if not results["ids"][0]:
            return output
        
        for i in range(len(results["ids"][0])):
            output.append({
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
                "score": 1 - results["distances"][0][i],
            })
        
        return output
    
    def delete_by_doc_id(self, doc_id: str) -> int:
        """
        Delete all chunks for a document.
        
        Args:
            doc_id: Document ID to delete.
        
        Returns:
            Number of chunks deleted.
        """
        # Find all chunks with this doc_id
        results = self.collection.get(
            where={"doc_id": doc_id},
            include=["metadatas"],
        )
        
        if not results["ids"]:
            return 0
        
        count = len(results["ids"])
        self.collection.delete(ids=results["ids"])
        
        return count
    
    def get_all_doc_ids(self) -> set[str]:
        """Get all unique document IDs in the store."""
        results = self.collection.get(include=["metadatas"])
        
        doc_ids = set()
        for metadata in results["metadatas"]:
            if metadata and "doc_id" in metadata:
                doc_ids.add(metadata["doc_id"])
        
        return doc_ids
    
    def count(self) -> int:
        """Get total number of chunks in store."""
        return self.collection.count()
    
    def clear(self) -> None:
        """Clear all documents from the collection."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )


# Global instance (lazy loaded)
_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    """Get cached vector store instance."""
    global _store
    if _store is None:
        _store = VectorStore()
    return _store


if __name__ == "__main__":
    # Quick test
    store = get_vector_store()
    print(f"Documents in store: {store.count()}")
    print(f"Unique doc IDs: {len(store.get_all_doc_ids())}")
