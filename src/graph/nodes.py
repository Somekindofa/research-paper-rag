"""
Graph Nodes - Individual processing steps in the RAG pipeline.
Each node takes state, processes it, and returns updated state.
"""

import json
import re
from typing import Any

from src.config import prompts
from src.graph.state import GraphState
from src.integrations.lm_studio_client import get_jan_client
from src.retrieval.hyde import generate_hypothetical_document
from src.retrieval.embeddings import get_embedding_model
from src.retrieval.vectorstore import get_vector_store
from src.retrieval.reranker import rerank_documents


def router_node(state: GraphState) -> GraphState:
    """
    Node 0: Route the query to either retrieval or direct answer path.

    Uses LLM to classify if query needs database retrieval or can be answered directly.
    Can be overridden by force_retrieval setting.

    Examples:
    - "Hello" -> direct_answer (unless force_retrieval=True)
    - "What are neural network pruning methods?" -> retrieve
    """
    query = state.get("processed_query", state.get("query", ""))
    force_retrieval = state.get("force_retrieval", False)

    # If force_retrieval is enabled, always route to retrieval
    if force_retrieval:
        return {**state, "routing_decision": "retrieve", "error": None}

    if not query:
        # Default to retrieval for safety
        return {**state, "routing_decision": "retrieve", "error": None}

    try:
        # Get routing prompt
        router_template = prompts()["query_router"]["template"]
        prompt = router_template.format(query=query)

        # Use LLM to classify
        from src.integrations.lm_studio_client import get_lm_studio_client

        selected_model = state.get("selected_model")
        client = get_lm_studio_client(model=selected_model)

        response = client.generate(
            prompt=prompt,
            temperature=0.1,  # Low temperature for consistent classification
            max_tokens=150,
        )

        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                needs_retrieval = result.get("needs_retrieval", True)
                reasoning = result.get("reasoning", "")

                decision = "retrieve" if needs_retrieval else "direct_answer"

                print(f"Router decision: {decision} - {reasoning}")

                return {
                    **state,
                    "routing_decision": decision,
                    "error": None,
                }
            else:
                # Fallback: if no JSON found, default to retrieval
                print("Router: No JSON found in response, defaulting to retrieval")
                return {**state, "routing_decision": "retrieve", "error": None}

        except json.JSONDecodeError:
            # Fallback to retrieval on parse error
            print("Router: JSON parse error, defaulting to retrieval")
            return {**state, "routing_decision": "retrieve", "error": None}

    except Exception as e:
        # On any error, default to retrieval to be safe
        print(f"Router error: {e}, defaulting to retrieval")
        return {**state, "routing_decision": "retrieve", "error": None}


def direct_answer_node(state: GraphState) -> GraphState:
    """
    Node: Generate direct answer without retrieval.

    Used for greetings, small talk, or general questions that don't need research papers.
    """
    query = state.get("processed_query", state.get("query", ""))

    if not query:
        return {
            **state,
            "answer": "I'm here to help with research questions!",
            "sources": [],
            "error": None,
        }

    try:
        # Get direct answer prompt
        direct_template = prompts()["direct_answer"]["template"]
        prompt = direct_template.format(query=query)

        # Generate answer
        from src.integrations.lm_studio_client import get_lm_studio_client

        selected_model = state.get("selected_model")
        client = get_lm_studio_client(model=selected_model)

        answer = client.generate(
            prompt=prompt,
            temperature=0.7,  # Higher temperature for conversational tone
            max_tokens=300,
        )

        return {
            **state,
            "answer": answer.strip(),
            "sources": [],
            "error": None,
        }

    except ConnectionError as e:
        return {
            **state,
            "answer": "I'm a research assistant, but I'm having trouble connecting to my language model right now. Please make sure LM Studio is running.",
            "sources": [],
            "error": str(e),
        }

    except Exception as e:
        return {
            **state,
            "answer": f"I'm a research assistant here to help answer questions about research papers. Error: {e}",
            "sources": [],
            "error": str(e),
        }


def preprocess_node(state: GraphState) -> GraphState:
    """
    Node 1: Preprocess the query.

    - Cleans whitespace
    - Basic validation
    - Could be extended for query expansion
    """
    query = state.get("query", "").strip()

    if not query:
        return {**state, "error": "Empty query provided", "processed_query": ""}

    # Basic cleaning
    processed = " ".join(query.split())  # Normalize whitespace

    return {**state, "processed_query": processed, "error": None}


def hyde_node(state: GraphState) -> GraphState:
    """
    Node 2: Generate Hypothetical Document Embedding (HyDE).

    Creates a hypothetical academic paragraph that would answer the query.
    This improves retrieval for complex research questions.
    """
    query = state.get("processed_query", state.get("query", ""))

    if not query:
        return {**state, "error": "No query for HyDE generation"}

    try:
        # Generate hypothetical document
        hyde_doc = generate_hypothetical_document(query)

        # Embed the hypothetical document
        model = get_embedding_model()
        embedding = model.embed_single(hyde_doc, is_query=False)

        return {
            **state,
            "hyde_doc": hyde_doc,
            "query_embedding": embedding,
            "error": None,
        }

    except ConnectionError as e:
        # Fall back to direct query embedding if Jan is unavailable
        print(f"HyDE fallback: {e}")
        model = get_embedding_model()
        embedding = model.embed_query(query)

        return {
            **state,
            "hyde_doc": "",
            "query_embedding": embedding,
            "error": None,
        }

    except Exception as e:
        return {**state, "error": f"HyDE generation failed: {e}"}


def retrieve_node(state: GraphState) -> GraphState:
    """
    Node 3: Retrieve relevant documents using MMR search.

    Uses the HyDE embedding (or direct query embedding) to find
    diverse, relevant documents from the vector store.
    Uses num_docs from state if provided.
    """
    embedding = state.get("query_embedding")
    num_docs = state.get("num_docs", None)  # Get from state if available

    if not embedding:
        return {**state, "error": "No embedding for retrieval"}

    try:
        store = get_vector_store()

        # Check if store has any documents
        if store.count() == 0:
            return {
                **state,
                "retrieved_docs": [],
                "error": "No documents in vector store. Please add PDFs first.",
            }

        # MMR search for diverse results, using custom k if provided
        results = store.mmr_search(query_embedding=embedding, k=num_docs)

        if not results:
            return {
                **state,
                "retrieved_docs": [],
                "error": "No relevant documents found.",
            }

        return {**state, "retrieved_docs": results, "error": None}

    except Exception as e:
        return {**state, "error": f"Retrieval failed: {e}"}


def rerank_node(state: GraphState) -> GraphState:
    """
    Node 4: Rerank retrieved documents.

    Uses a cross-encoder model to re-score documents based on
    query-document relevance, improving precision.
    """
    docs = state.get("retrieved_docs", [])
    query = state.get("processed_query", state.get("query", ""))

    if not docs:
        return {**state, "ranked_docs": [], "error": state.get("error")}

    try:
        ranked = rerank_documents(query, docs)
        return {**state, "ranked_docs": ranked, "error": None}

    except Exception as e:
        # Fall back to original order if reranking fails
        print(f"Reranking failed, using original order: {e}")
        return {**state, "ranked_docs": docs, "error": None}


def generate_node(state: GraphState) -> GraphState:
    """
    Node 5: Generate final answer with citations.

    Synthesizes an answer from the ranked documents,
    including proper academic citations.
    Uses selected_model from state if provided.
    """
    docs = state.get("ranked_docs", [])
    query = state.get("processed_query", state.get("query", ""))
    selected_model = state.get("selected_model", None)

    if not docs:
        error = state.get("error") or "No documents available for answer generation."
        return {
            **state,
            "answer": f"I couldn't find relevant information to answer your question. {error}",
            "sources": [],
        }

    try:
        # Deduplicate documents by doc_id to ensure diverse citations
        # Keep only the highest-scored chunk from each document
        seen_docs = {}
        deduplicated_docs = []

        for doc in docs:
            doc_id = doc.get("metadata", {}).get("doc_id", "unknown")
            score = doc.get("rerank_score", doc.get("score", 0))

            if doc_id not in seen_docs or score > seen_docs[doc_id]["score"]:
                seen_docs[doc_id] = {"doc": doc, "score": score}

        # Convert back to list, sorted by score
        deduplicated_docs = [
            item["doc"]
            for item in sorted(
                seen_docs.values(), key=lambda x: x["score"], reverse=True
            )
        ]

        # Use deduplicated docs for answer generation
        docs = deduplicated_docs

        # Format sources for the prompt
        source_template = prompts()["source_format"]["template"]
        formatted_sources = []
        source_info = []

        for i, doc in enumerate(docs):
            metadata = doc.get("metadata", {})

            source_text = source_template.format(
                index=i + 1,
                title=metadata.get("title", "Unknown"),
                authors=metadata.get("authors", "Unknown"),
                year=metadata.get("year", "Unknown"),
                content=doc.get("content", "")[:500],  # Truncate for prompt
            )
            formatted_sources.append(source_text)

            # Store source info for UI (including new metadata fields)
            source_info.append(
                {
                    "index": i + 1,
                    "title": metadata.get("title", "Unknown"),
                    "authors": metadata.get("authors", "Unknown"),
                    "year": metadata.get("year", "Unknown"),
                    "content": doc.get("content", ""),
                    "score": doc.get("rerank_score", doc.get("score", 0)),
                    "page": metadata.get("page_number"),
                    "filename": metadata.get("filename", ""),
                    "metadata": {
                        "summary": metadata.get("summary"),
                        "gap": metadata.get("gap"),
                        "methodology": metadata.get("methodology"),
                        "results": metadata.get("results"),
                        "discussion": metadata.get("discussion"),
                        "conclusion": metadata.get("conclusion"),
                    },
                }
            )

        # Generate answer
        synthesis_template = prompts()["synthesis"]["template"]
        prompt = synthesis_template.format(
            query=query,
            sources="\n".join(formatted_sources),
        )

        # Use selected model if provided
        from src.integrations.lm_studio_client import get_lm_studio_client

        client = get_lm_studio_client(model=selected_model)
        answer = client.generate(
            prompt=prompt,
            temperature=0.3,  # Lower temperature for factual synthesis
            max_tokens=1024,
        )

        return {
            **state,
            "answer": answer.strip(),
            "sources": source_info,
            "error": None,
        }

    except ConnectionError as e:
        return {
            **state,
            "answer": "I couldn't generate an answer because the LLM server is not available. Please ensure LM Studio is running.",
            "sources": [],
            "error": str(e),
        }

    except Exception as e:
        return {
            **state,
            "answer": f"Error generating answer: {e}",
            "sources": [],
            "error": str(e),
        }


# Node registry for easy access
NODES = {
    "router": router_node,
    "preprocess": preprocess_node,
    "hyde": hyde_node,
    "retrieve": retrieve_node,
    "rerank": rerank_node,
    "generate": generate_node,
    "direct_answer": direct_answer_node,
}
