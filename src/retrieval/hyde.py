"""
HyDE - Hypothetical Document Embeddings.
Generates a hypothetical answer to improve retrieval.
"""
from src.config import prompts
from src.integrations.lm_studio_client import get_jan_client
from src.retrieval.embeddings import embed_query


def generate_hypothetical_document(query: str) -> str:
    """
    Generate a hypothetical academic paragraph that would answer the query.
    
    This is the core of HyDE: instead of embedding the query directly,
    we generate what an ideal answer might look like, then embed that.
    This often produces better retrieval results for complex queries.
    
    Args:
        query: User's research question.
    
    Returns:
        Hypothetical academic paragraph.
    """
    prompt_template = prompts()["hyde"]["template"]
    prompt = prompt_template.format(query=query)
    
    client = get_jan_client()
    
    # Generate with moderate temperature for creativity
    hypothetical_doc = client.generate(
        prompt=prompt,
        temperature=0.7,
        max_tokens=300,  # Keep it concise
    )
    
    return hypothetical_doc.strip()


def hyde_embed(query: str) -> tuple[list[float], str]:
    """
    Generate hypothetical document and embed it.
    
    Args:
        query: User's research question.
    
    Returns:
        Tuple of (embedding vector, hypothetical document text).
    """
    # Generate hypothetical document
    hyde_doc = generate_hypothetical_document(query)
    
    # Embed the hypothetical document (as a document, not query)
    # This is key: we embed the generated text as if it were a document
    from src.retrieval.embeddings import get_embedding_model
    model = get_embedding_model()
    embedding = model.embed_single(hyde_doc, is_query=False)
    
    return (embedding, hyde_doc)


def hybrid_embed(query: str, use_hyde: bool = True) -> tuple[list[float], str | None]:
    """
    Get query embedding with optional HyDE enhancement.
    
    Args:
        query: User's query.
        use_hyde: Whether to use HyDE. If False, embeds query directly.
    
    Returns:
        Tuple of (embedding, hypothetical_doc or None).
    """
    if use_hyde:
        return hyde_embed(query)
    else:
        embedding = embed_query(query)
        return (embedding, None)


if __name__ == "__main__":
    # Quick test
    test_query = "What are the main approaches to neural network pruning?"
    
    print(f"Query: {test_query}")
    print("\nGenerating hypothetical document...")
    
    try:
        hyde_doc = generate_hypothetical_document(test_query)
        print(f"\nHyDE Document:\n{hyde_doc}")
    except Exception as e:
        print(f"Error (Jan server may not be running): {e}")
