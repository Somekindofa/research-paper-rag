"""
Diagnostics - System health checks and debugging utilities.
Run this to verify all components are working before starting the UI.
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv(project_root / ".env")


def test_imports() -> dict:
    """Test that all required packages can be imported."""
    results = {"status": "checking", "packages": {}}
    
    packages = [
        ("langgraph", "LangGraph"),
        ("langchain", "LangChain"),
        ("chromadb", "ChromaDB"),
        ("sentence_transformers", "Sentence Transformers"),
        ("fitz", "PyMuPDF"),
        ("chainlit", "Chainlit"),
        ("openai", "OpenAI SDK"),
        ("yaml", "PyYAML"),
        ("torch", "PyTorch"),
    ]
    
    all_ok = True
    for module, name in packages:
        try:
            __import__(module)
            results["packages"][name] = "✅ OK"
        except ImportError as e:
            results["packages"][name] = f"❌ {e}"
            all_ok = False
    
    results["status"] = "healthy" if all_ok else "missing_packages"
    return results


def test_gpu() -> dict:
    """Test CUDA/GPU availability."""
    results = {"status": "checking"}
    
    try:
        import torch
        
        results["cuda_available"] = torch.cuda.is_available()
        results["cuda_version"] = torch.version.cuda if torch.cuda.is_available() else None
        
        if torch.cuda.is_available():
            results["gpu_name"] = torch.cuda.get_device_name(0)
            results["gpu_memory_total"] = f"{torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB"
            results["gpu_memory_allocated"] = f"{torch.cuda.memory_allocated(0) / 1e9:.2f} GB"
            results["status"] = "healthy"
        else:
            results["status"] = "no_gpu"
            results["note"] = "Will use CPU for embeddings (slower but works)"
    
    except Exception as e:
        results["status"] = "error"
        results["error"] = str(e)
    
    return results


def test_jan_server() -> dict:
    """Test Jan LLM server connection."""
    try:
        from src.integrations.jan_client import check_jan_server
        return check_jan_server()
    except Exception as e:
        return {"status": "error", "error": str(e)}


def test_embedding_model() -> dict:
    """Test embedding model loading."""
    try:
        from src.retrieval.embeddings import test_embedding_model
        return test_embedding_model()
    except Exception as e:
        return {"status": "error", "error": str(e)}


def test_vector_store() -> dict:
    """Test Chroma vector store."""
    results = {"status": "checking"}
    
    try:
        from src.retrieval.vectorstore import get_vector_store
        
        store = get_vector_store()
        results["document_count"] = store.count()
        results["unique_docs"] = len(store.get_all_doc_ids())
        results["persist_directory"] = store.persist_directory
        results["status"] = "healthy"
    
    except Exception as e:
        results["status"] = "error"
        results["error"] = str(e)
    
    return results


def test_pdf_folder() -> dict:
    """Test PDF folder configuration."""
    results = {"status": "checking"}
    
    try:
        from src.config import settings
        from src.processing.pdf_scanner import get_pdf_list
        from src.processing.duplicates import ChecksumStore
        
        config = settings()
        folder = config["pdf"]["folder_path"]
        
        results["folder_path"] = folder
        results["folder_exists"] = Path(folder).exists()
        
        if results["folder_exists"]:
            pdfs = get_pdf_list()
            store = ChecksumStore()
            
            results["total_pdfs"] = len(pdfs)
            results["indexed_pdfs"] = store.count()
            results["pending_pdfs"] = len(pdfs) - store.count()
            results["status"] = "healthy"
        else:
            results["status"] = "folder_not_found"
            results["note"] = f"Create the folder or update PDF_FOLDER_PATH in .env"
    
    except Exception as e:
        results["status"] = "error"
        results["error"] = str(e)
    
    return results


def test_config() -> dict:
    """Test configuration loading."""
    results = {"status": "checking"}
    
    try:
        from src.config import settings, prompts
        
        config = settings()
        prompt_config = prompts()
        
        results["jan_url"] = config["jan"]["base_url"]
        results["jan_model"] = config["jan"]["model"]
        results["embedding_model"] = config["embeddings"]["model_name"]
        results["embedding_device"] = config["embeddings"]["device"]
        results["chunk_size"] = config["chunking"]["chunk_size"]
        results["prompts_loaded"] = list(prompt_config.keys())
        results["status"] = "healthy"
    
    except Exception as e:
        results["status"] = "error"
        results["error"] = str(e)
    
    return results


def run_all_tests(verbose: bool = True) -> dict:
    """Run all diagnostic tests."""
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("GPU/CUDA", test_gpu),
        ("PDF Folder", test_pdf_folder),
        ("Jan Server", test_jan_server),
        ("Embedding Model", test_embedding_model),
        ("Vector Store", test_vector_store),
    ]
    
    all_results = {}
    all_healthy = True
    
    for name, test_func in tests:
        if verbose:
            print(f"\n{'='*50}")
            print(f"Testing: {name}")
            print('='*50)
        
        try:
            result = test_func()
            all_results[name] = result
            
            status = result.get("status", "unknown")
            is_healthy = status == "healthy"
            
            if not is_healthy:
                all_healthy = False
            
            if verbose:
                status_emoji = "✅" if is_healthy else "⚠️" if status != "error" else "❌"
                print(f"Status: {status_emoji} {status}")
                
                for key, value in result.items():
                    if key != "status":
                        print(f"  {key}: {value}")
        
        except Exception as e:
            all_results[name] = {"status": "error", "error": str(e)}
            all_healthy = False
            if verbose:
                print(f"Status: ❌ Error - {e}")
    
    all_results["overall"] = "healthy" if all_healthy else "issues_found"
    
    return all_results


def print_summary(results: dict):
    """Print a summary of test results."""
    print("\n" + "="*50)
    print("DIAGNOSTIC SUMMARY")
    print("="*50)
    
    for name, result in results.items():
        if name == "overall":
            continue
        
        status = result.get("status", "unknown")
        emoji = "✅" if status == "healthy" else "⚠️" if status != "error" else "❌"
        print(f"{emoji} {name}: {status}")
    
    print("\n" + "-"*50)
    overall = results.get("overall", "unknown")
    if overall == "healthy":
        print("✅ All systems operational! Ready to start the UI.")
        print("\nRun: chainlit run src/ui/app.py")
    else:
        print("⚠️ Some issues found. Review the details above.")
        print("\nCommon fixes:")
        print("  - Jan not running: Start Jan and enable Local API Server")
        print("  - Missing packages: pip install -r requirements.txt")
        print("  - No GPU: Set EMBEDDING_DEVICE=cpu in .env")
        print("  - PDF folder: Create folder or update PDF_FOLDER_PATH in .env")


if __name__ == "__main__":
    print("Research RAG - System Diagnostics")
    print("="*50)
    
    results = run_all_tests(verbose=True)
    print_summary(results)
