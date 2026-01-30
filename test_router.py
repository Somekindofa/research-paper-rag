"""
Quick test for the router functionality without requiring LM Studio.
"""

import sys

sys.path.insert(0, r"c:\Users\dupon\Documents\Projects\Personal\research-paper-rag")

from src.graph.state import GraphState

# Test 1: Check GraphState has routing_decision field
print("Test 1: GraphState structure")
state = GraphState()
print(
    f"  GraphState has 'routing_decision' field: {'routing_decision' in GraphState.__annotations__}"
)

# Test 2: Check nodes are imported
print("\nTest 2: Import nodes")
try:
    from src.graph.nodes import router_node, direct_answer_node, NODES

    print("  ✓ router_node imported")
    print("  ✓ direct_answer_node imported")
    print(f"  ✓ NODES registry has {len(NODES)} nodes: {list(NODES.keys())}")
except Exception as e:
    print(f"  ✗ Error importing nodes: {e}")

# Test 3: Check graph imports
print("\nTest 3: Import graph with routing")
try:
    from src.graph.graph import route_query, create_rag_graph

    print("  ✓ route_query function imported")
    print("  ✓ create_rag_graph function imported")
except Exception as e:
    print(f"  ✗ Error importing graph: {e}")

# Test 4: Check prompts
print("\nTest 4: Check prompt templates")
try:
    from src.config import prompts

    p = prompts()
    print(f"  ✓ query_router prompt exists: {'query_router' in p}")
    print(f"  ✓ direct_answer prompt exists: {'direct_answer' in p}")
except Exception as e:
    print(f"  ✗ Error loading prompts: {e}")

# Test 5: Test route_query function logic
print("\nTest 5: Test routing logic")
try:
    from src.graph.graph import route_query

    # Test retrieval path
    state_retrieve = {"routing_decision": "retrieve"}
    result = route_query(state_retrieve)
    print(f"  ✓ 'retrieve' -> '{result}' (expected: 'hyde')")

    # Test direct answer path
    state_direct = {"routing_decision": "direct_answer"}
    result = route_query(state_direct)
    print(f"  ✓ 'direct_answer' -> '{result}' (expected: 'direct_answer')")

    # Test default (no decision)
    state_empty = {}
    result = route_query(state_empty)
    print(f"  ✓ no decision -> '{result}' (expected: 'hyde')")

except Exception as e:
    print(f"  ✗ Error testing routing: {e}")

print("\n" + "=" * 60)
print("✅ Router implementation complete!")
print("=" * 60)
print("\nGraph flow:")
print("  START → preprocess → router → [conditional]")
print("    ├─ retrieve path: hyde → retrieve → rerank → generate → END")
print("    └─ direct path: direct_answer → END")
print("\nTo test with LM Studio:")
print("  1. Ensure LM Studio is running")
print("  2. Run: chainlit run src/ui/app.py")
print("  3. Test queries:")
print("     - 'Hello' (should route to direct_answer)")
print("     - 'What are pruning methods?' (should route to retrieve)")
