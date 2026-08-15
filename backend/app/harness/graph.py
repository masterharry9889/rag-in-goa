from langgraph.graph import StateGraph, END
from harps.state import GraphState
from harps.nodes import stt_node, retrieve_node, guardrails_node, generation_node

def create_rag_graph() -> StateGraph:
    """Create the RAG pipeline as a LangGraph StateGraph."""
    # Initialize the graph with our state type
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("stt", stt_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("guardrails", guardrails_node)
    workflow.add_node("generation", generation_node)

    # Set the entry point
    workflow.set_entry_point("stt")

    # Add edges
    workflow.add_edge("stt", "retrieve")
    workflow.add_edge("retrieve", "guardrails")
    workflow.add_edge("guardrails", "generation")
    workflow.add_edge("generation", END)

    # Compile the graph
    app = workflow.compile()
    return app

# If we want to run the graph as a standalone script for testing
if __name__ == "__main__":
    # This is just for testing; in practice, we would import and use the graph in the API
    app = create_rag_graph()
    # Example input (we would need to provide audio_data in a real scenario)
    # For now, we'll just show that the graph is created.
    print("RAG graph created successfully.")