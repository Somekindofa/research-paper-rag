"""
RAG Graph - LangGraph assembly for the RAG pipeline.
Connects nodes into a directed graph with state management.
"""
from typing import Any, Generator

from langgraph.graph import StateGraph, START, END

from src.graph.state import GraphState
from src.graph.nodes import (
    preprocess_node,
    hyde_node,
    retrieve_node,
    rerank_node,
    generate_node,
)


def create_rag_graph() -> StateGraph:
    """
    Create the RAG pipeline graph.
    
    Flow:
    START -> preprocess -> hyde -> retrieve -> rerank -> generate -> END
    
    Returns:
        Compiled StateGraph ready for invocation.
    """
    # Create graph with state schema
    graph = StateGraph(GraphState)
    
    # Add nodes
    graph.add_node("preprocess", preprocess_node)
    graph.add_node("hyde", hyde_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("rerank", rerank_node)
    graph.add_node("generate", generate_node)
    
    # Define edges (linear flow for MVP)
    graph.add_edge(START, "preprocess")
    graph.add_edge("preprocess", "hyde")
    graph.add_edge("hyde", "retrieve")
    graph.add_edge("retrieve", "rerank")
    graph.add_edge("rerank", "generate")
    graph.add_edge("generate", END)
    
    # Compile the graph
    return graph.compile()


class RAGPipeline:
    """
    High-level interface for the RAG pipeline.
    Wraps the LangGraph for easy invocation.
    """
    
    def __init__(self):
        """Initialize the RAG pipeline."""
        self.graph = create_rag_graph()
    
    def invoke(self, query: str, num_docs: int = None, relevance_threshold: float = None, selected_model: str = None) -> dict[str, Any]:
        """
        Run the full RAG pipeline.
        
        Args:
            query: User's research question.
            num_docs: Number of documents to retrieve (optional).
            relevance_threshold: Minimum relevance score (optional).
            selected_model: LLM model to use (optional).
        
        Returns:
            Final state with answer and sources.
        """
        initial_state: GraphState = {
            "query": query,
        }
        
        # Add optional parameters to state
        if num_docs is not None:
            initial_state["num_docs"] = num_docs
        if relevance_threshold is not None:
            initial_state["relevance_threshold"] = relevance_threshold
        if selected_model is not None:
            initial_state["selected_model"] = selected_model
        
        result = self.graph.invoke(initial_state)
        return result
    
    def stream(self, query: str) -> Generator[dict[str, Any], None, None]:
        """
        Stream the RAG pipeline execution.
        
        Yields state updates as each node completes.
        Useful for showing progress in UI.
        
        Args:
            query: User's research question.
        
        Yields:
            State updates from each node.
        """
        initial_state: GraphState = {"query": query}
        
        for event in self.graph.stream(initial_state):
            yield event
    
    def get_answer(self, query: str) -> tuple[str, list[dict[str, Any]]]:
        """
        Convenience method to get just answer and sources.
        
        Args:
            query: User's research question.
        
        Returns:
            Tuple of (answer text, list of sources).
        """
        result = self.invoke(query)
        return (
            result.get("answer", "No answer generated."),
            result.get("sources", []),
        )


# Global pipeline instance (lazy loaded)
_pipeline: RAGPipeline | None = None


def get_pipeline() -> RAGPipeline:
    """Get cached pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline


def query_rag(query: str) -> tuple[str, list[dict[str, Any]]]:
    """
    Convenience function to query the RAG system.
    
    Args:
        query: Research question.
    
    Returns:
        Tuple of (answer, sources).
    """
    pipeline = get_pipeline()
    return pipeline.get_answer(query)


if __name__ == "__main__":
    # Quick test (requires Jan server and indexed documents)
    print("Testing RAG pipeline...")
    
    pipeline = RAGPipeline()
    
    test_query = "What are the main methods for neural network pruning?"
    print(f"\nQuery: {test_query}")
    
    try:
        print("\nRunning pipeline (streaming)...")
        for event in pipeline.stream(test_query):
            node_name = list(event.keys())[0]
            print(f"  Completed: {node_name}")
        
        answer, sources = pipeline.get_answer(test_query)
        print(f"\nAnswer:\n{answer}")
        print(f"\nSources: {len(sources)}")
        
    except Exception as e:
        print(f"Error: {e}")
