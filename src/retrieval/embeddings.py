"""
Embeddings - Load and manage embedding model for semantic search.
Uses sentence-transformers with GPU acceleration.
"""
import numpy as np
from typing import Any

from sentence_transformers import SentenceTransformer

from src.config import settings


class EmbeddingModel:
    """
    Wrapper for sentence-transformers embedding model.
    Handles GPU/CPU device selection and batched embedding.
    """
    
    def __init__(
        self,
        model_name: str | None = None,
        device: str | None = None,
    ):
        """
        Initialize embedding model.
        
        Args:
            model_name: Model name/path. Defaults to config.
            device: Device to use (cuda/cpu). Defaults to config.
        """
        config = settings()["embeddings"]
        
        self.model_name = model_name or config["model_name"]
        self.device = device or config["device"]
        self.batch_size = config.get("batch_size", 32)
        
        print(f"Loading embedding model: {self.model_name} on {self.device}")
        
        # Load model with trust_remote_code for nomic
        self.model = SentenceTransformer(
            self.model_name,
            device=self.device,
            trust_remote_code=True,
        )
        
        # Get embedding dimension
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"Embedding dimension: {self.dimension}")
    
    def embed_query(self, text: str) -> list[float]:
        """
        Embed a single query text.
        
        Args:
            text: Text to embed.
        
        Returns:
            List of floats (embedding vector).
        """
        # Nomic recommends prefixing queries
        if "nomic" in self.model_name.lower():
            text = f"search_query: {text}"
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embed multiple documents.
        
        Args:
            texts: List of texts to embed.
        
        Returns:
            List of embedding vectors.
        """
        if not texts:
            return []
        
        # Nomic recommends prefixing documents differently
        if "nomic" in self.model_name.lower():
            texts = [f"search_document: {t}" for t in texts]
        
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=len(texts) > 10,
            convert_to_numpy=True,
        )
        
        return embeddings.tolist()
    
    def embed_single(self, text: str, is_query: bool = False) -> list[float]:
        """
        Embed a single text with query/document prefix handling.
        
        Args:
            text: Text to embed.
            is_query: If True, use query prefix; else document prefix.
        
        Returns:
            Embedding vector.
        """
        if is_query:
            return self.embed_query(text)
        return self.embed_documents([text])[0]


# Global model instance (lazy loaded)
_model: EmbeddingModel | None = None


def get_embedding_model() -> EmbeddingModel:
    """Get cached embedding model instance."""
    global _model
    if _model is None:
        _model = EmbeddingModel()
    return _model


def embed_query(text: str) -> list[float]:
    """Convenience function to embed a query."""
    return get_embedding_model().embed_query(text)


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Convenience function to embed documents."""
    return get_embedding_model().embed_documents(texts)


def test_embedding_model() -> dict[str, Any]:
    """Test that embedding model is working."""
    try:
        model = get_embedding_model()
        
        # Test query embedding
        query_emb = model.embed_query("test query")
        
        # Test document embedding
        doc_emb = model.embed_documents(["test document"])
        
        return {
            "status": "healthy",
            "model_name": model.model_name,
            "device": model.device,
            "dimension": model.dimension,
            "query_embedding_shape": len(query_emb),
            "doc_embedding_shape": len(doc_emb[0]) if doc_emb else 0,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(type(e).__name__),
            "details": str(e),
        }


if __name__ == "__main__":
    print("Testing embedding model...")
    result = test_embedding_model()
    for key, value in result.items():
        print(f"  {key}: {value}")
