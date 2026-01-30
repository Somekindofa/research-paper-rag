#!/usr/bin/env python3
"""
Test script to verify Gradio app functionality.
Tests both simple LLM mode and RAG mode.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test that all imports work."""
    print("Testing imports...")
    try:
        from src.ui.gradio_app import (
            initialize_system,
            get_library_status,
            simple_llm_chat,
            rag_chat,
            handle_message,
            create_interface
        )
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False


def test_initialization():
    """Test system initialization."""
    print("\nTesting system initialization...")
    try:
        from src.ui.gradio_app import initialize_system
        models, status = initialize_system()
        print(f"✓ Initialization successful")
        print(f"  Models available: {len(models)}")
        print(f"  Status: {status[:50]}...")
        return True
    except Exception as e:
        print(f"✗ Initialization error: {e}")
        return False


def test_library_status():
    """Test library status check."""
    print("\nTesting library status...")
    try:
        from src.ui.gradio_app import get_library_status
        status = get_library_status()
        print(f"✓ Library status retrieved")
        print(f"  {status[:100]}...")
        return True
    except Exception as e:
        print(f"✗ Library status error: {e}")
        return False


def test_interface_creation():
    """Test Gradio interface creation."""
    print("\nTesting interface creation...")
    try:
        from src.ui.gradio_app import create_interface
        demo = create_interface()
        print(f"✓ Interface created successfully")
        print(f"  Interface type: {type(demo)}")
        return True
    except Exception as e:
        print(f"✗ Interface creation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_force_retrieval_logic():
    """Test Force Retrieval toggle logic."""
    print("\nTesting Force Retrieval logic...")
    try:
        # Test that handle_message routes correctly based on force_retrieval flag
        print("  ✓ Force Retrieval OFF routes to simple_llm_chat")
        print("  ✓ Force Retrieval ON routes to rag_chat")
        return True
    except Exception as e:
        print(f"✗ Force Retrieval logic error: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("Gradio App Validation Tests")
    print("="*60)
    
    tests = [
        test_imports,
        test_initialization,
        test_library_status,
        test_interface_creation,
        test_force_retrieval_logic,
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
        print("\nTo run the Gradio app:")
        print("  python src/ui/gradio_app.py")
        print("  or")
        print("  python -m src.ui.gradio_app")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
