import pytest
from app.graph.build_graph import build_graph

def test_guardrails_structurally_wired():
    """
    Fails the build if guardrail nodes aren't structurally present in the compiled graph.
    This is the regression test for the bypass issue.
    """
    graph = build_graph()
    
    # Check that input_guard and output_guard are present as nodes
    assert "input_guard" in graph.nodes, "input_guard node is missing from the compiled graph."
    assert "output_guard" in graph.nodes, "output_guard node is missing from the compiled graph."
    
    # Check that there are edges flowing into/out of them.
    # In LangGraph compiled graphs, we can inspect builder.
    builder = graph.builder
    
    edges = builder.edges
    # edges is a set of tuples (start_node, end_node)
    
    # input_guard should have at least one outgoing edge
    has_input_outgoing = any(edge[0] == "input_guard" for edge in edges)
    # output_guard should have at least one incoming edge and one outgoing edge
    has_output_incoming = any(edge[1] == "output_guard" for edge in edges)
    has_output_outgoing = any(edge[0] == "output_guard" for edge in edges)
    
    assert has_input_outgoing, "input_guard has no outgoing edges, meaning it's disconnected."
    assert has_output_incoming, "output_guard has no incoming edges, meaning it's disconnected."
    assert has_output_outgoing, "output_guard has no outgoing edges, meaning it's disconnected."
