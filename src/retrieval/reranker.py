"""
Reranker - Cross-encoder reranking for improved retrieval precision.
Takes initial retrieval results and re-scores them with a more powerful model.
"""
from typing import Any

from sentence_transformers import CrossEncoder

from src.config import settings


class Reranker:
    """
    Cross-encoder based reranker.
    More accurate than embedding similarity but slower.
    Use after initial retrieval to refine top results.
    """
    
    def __init__(self, model_name: str | None = None):
        """
        Initialize reranker.
        
        Args:
            model_name: Cross-encoder model. Defaults to config.
        """
        config = settings()["reranker"]
        self.model_name = model_name or config["model_name"]
        self.top_k = config.get("top_k", 5)
        
        print(f"Loading reranker model: {self.model_name}")
        self.model = CrossEncoder(self.model_name)
    
    def rerank(
        self,
        query: str,
        documents: list[dict[str, Any]],
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Rerank documents by relevance to query.
        
        Args:
            query: User's query.
            documents: List of document dicts with 'content' field.
            top_k: Number of top results to return.
        
        Returns:
            Reranked documents with updated scores.
        """
        if not documents:
            return []
        
        top_k = top_k or self.top_k
        
        # Prepare query-document pairs
        pairs = [[query, doc["content"]] for doc in documents]
        
        # Score all pairs
        scores = self.model.predict(pairs)
        
        # Attach scores and sort
        for doc, score in zip(documents, scores):
            doc["rerank_score"] = float(score)
        
        # Sort by rerank score (descending)
        ranked = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)
        
        return ranked[:top_k]


# Global instance (lazy loaded)
_reranker: Reranker | None = None


def get_reranker() -> Reranker:
    """Get cached reranker instance."""
    global _reranker
    if _reranker is None:
        _reranker = Reranker()
    return _reranker


def rerank_documents(
    query: str,
    documents: list[dict[str, Any]],
    top_k: int | None = None,
) -> list[dict[str, Any]]:
    """Convenience function to rerank documents."""
    reranker = get_reranker()
    return reranker.rerank(query, documents, top_k)


if __name__ == "__main__":
    # Quick test
    print("Testing reranker...")
    reranker = get_reranker()
    
    test_query = "What is machine learning?"
    test_docs = [
        {"content": "Machine learning is a subset of AI that enables systems to learn from data."},
        {"content": "The weather today is sunny with clouds."},
        {"content": "Deep learning uses neural networks with many layers."},
    ]
    
    results = reranker.rerank(test_query, test_docs)
    
    print(f"\nQuery: {test_query}")
    print("\nRanked results:")
    for doc in results:
        print(f"  Score: {doc['rerank_score']:.4f} - {doc['content'][:50]}...")
