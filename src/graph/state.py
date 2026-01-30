"""
Graph State - TypedDict definition for LangGraph state management.
Defines the data that flows through the RAG pipeline.
"""

from typing import Any, TypedDict


class GraphState(TypedDict, total=False):
    """
    State object passed through the LangGraph nodes.

    Attributes:
        query: Original user query
        processed_query: Cleaned/preprocessed query
        hyde_doc: Generated hypothetical document (HyDE)
        query_embedding: Embedding vector for retrieval
        retrieved_docs: Documents from initial retrieval
        ranked_docs: Documents after reranking
        answer: Generated answer text
        sources: Formatted source citations
        error: Error message if something failed
        num_docs: Number of documents to retrieve (user setting)
        relevance_threshold: Minimum relevance score (user setting)
        selected_model: LLM model to use (user setting)
    """

    # Input
    query: str

    # Processing
    processed_query: str
    hyde_doc: str
    query_embedding: list[float]

    # Retrieval
    retrieved_docs: list[dict[str, Any]]
    ranked_docs: list[dict[str, Any]]

    # Generation
    answer: str
    sources: list[dict[str, Any]]

    # Control
    error: str | None

    # User settings
    num_docs: int
    relevance_threshold: float
    selected_model: str

    # Routing
    routing_decision: str
