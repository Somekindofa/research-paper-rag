#!/usr/bin/env python3
"""
Quick validation script to test key components of the RAG system.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config():
    """Test configuration loading."""
    print("Testing configuration...")
    try:
        from src.config import settings, prompts
        config = settings()
        prompt_config = prompts()
        
        assert "lm_studio" in config, "LM Studio config missing"
        assert "retrieval" in config, "Retrieval config missing"
        assert "metadata_extraction" in prompt_config, "Metadata extraction prompt missing"
        
        print("✓ Configuration loads correctly")
        print(f"  - LM Studio URL: {config['lm_studio']['base_url']}")
        print(f"  - Default docs: {config['retrieval']['k']}")
        print(f"  - Default threshold: {config['retrieval']['score_threshold']}")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


def test_client_structure():
    """Test LM Studio client structure."""
    print("\nTesting LM Studio client...")
    try:
        # Just check if the file has correct structure
        import ast
        with open("src/integrations/lm_studio_client.py") as f:
            tree = ast.parse(f.read())
        
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        assert "LMStudioClient" in classes, "LMStudioClient class not found"
        assert "get_lm_studio_client" in functions, "get_lm_studio_client function not found"
        
        print("✓ LM Studio client structure valid")
        print(f"  - Classes: {', '.join(classes)}")
        print(f"  - Key functions: get_lm_studio_client, check_lm_studio_server")
        return True
    except Exception as e:
        print(f"✗ Client structure error: {e}")
        return False


def test_graph_structure():
    """Test graph components."""
    print("\nTesting graph structure...")
    try:
        import ast
        
        # Check state.py
        with open("src/graph/state.py") as f:
            tree = ast.parse(f.read())
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        assert "GraphState" in classes, "GraphState class not found"
        
        # Check nodes.py has all required nodes
        with open("src/graph/nodes.py") as f:
            content = f.read()
        
        required_nodes = ["preprocess_node", "hyde_node", "retrieve_node", "rerank_node", "generate_node"]
        for node in required_nodes:
            assert node in content, f"Node {node} not found"
        
        # Check for new parameters
        assert "num_docs" in content, "num_docs parameter not in nodes"
        assert "selected_model" in content, "selected_model parameter not in nodes"
        
        print("✓ Graph structure valid")
        print(f"  - All required nodes present")
        print(f"  - User settings parameters integrated")
        return True
    except Exception as e:
        print(f"✗ Graph structure error: {e}")
        return False


def test_ui_features():
    """Test UI features."""
    print("\nTesting UI features...")
    try:
        with open("src/ui/app.py") as f:
            content = f.read()
        
        # Check for key features
        features = {
            "get_available_models": "Model selection",
            "send_settings_panel": "Settings panel",
            "run_indexing_background": "Background indexing",
            "generate_document_metadata": "Metadata extraction",
            "on_message": "Message handling",
        }
        
        for func, desc in features.items():
            assert func in content, f"{desc} function not found"
        
        # Check for user controls
        assert "num_docs" in content, "Document count control missing"
        assert "relevance_threshold" in content, "Relevance threshold control missing"
        assert "selected_model" in content, "Model selection missing"
        
        print("✓ UI features present")
        for desc in features.values():
            print(f"  - {desc}")
        return True
    except Exception as e:
        print(f"✗ UI features error: {e}")
        return False


def test_css_and_js():
    """Test custom CSS and JS files."""
    print("\nTesting custom assets...")
    try:
        assert Path("public/custom.css").exists(), "custom.css not found"
        assert Path("public/custom.js").exists(), "custom.js not found"
        
        # Check CSS has key styles
        with open("public/custom.css") as f:
            css = f.read()
        
        assert "#model-selector-container" in css, "Model selector CSS missing"
        assert "#settings-panel" in css, "Settings panel CSS missing"
        assert "#indexing-progress" in css, "Indexing progress CSS missing"
        
        print("✓ Custom assets present")
        print("  - CSS: Model selector, settings, indexing progress")
        print("  - JS: UI interactions")
        return True
    except Exception as e:
        print(f"✗ Custom assets error: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("Research RAG System - Validation Tests")
    print("="*60)
    
    tests = [
        test_config,
        test_client_structure,
        test_graph_structure,
        test_ui_features,
        test_css_and_js,
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total} tests")
    
    if passed == total:
        print("\n✓ All validation tests passed!")
        print("\nNext steps:")
        print("1. Ensure LM Studio is running and accessible")
        print("2. Update .env with correct LM_STUDIO_BASE_URL")
        print("3. Add PDFs to data/pdfs/")
        print("4. Run: chainlit run src/ui/app.py")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
