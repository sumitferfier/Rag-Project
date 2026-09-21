from langgraph.graph import (
    StateGraph,
    START,
    END
)

from app.graph.state import RAGState
from app.graph.nodes import (
    classify_question,
    retrieve,
    generate,
    generate_chat
)

# EXISTING RAG GRAPH
# This graph is used by the existing /ask endpoint.

# START
#   ↓
# classify_question
#   ↓
# ┌───────────────┐
# │               │
# normal          PDF
# │               │
# generate_chat   retrieve
# │               │
# END             generate
#                   │
#                  END
graph_builder = StateGraph(RAGState)

graph_builder.add_node(
    "classify_question",
    classify_question
)
graph_builder.add_node(
    "retrieve",
    retrieve
)

graph_builder.add_node(
    "generate",
    generate
)

graph_builder.add_node(
    "generate_chat",
    generate_chat
)


graph_builder.add_edge(
    START,
    "classify_question"
)


def route_question(state: RAGState):

    if state["question_type"] == "normal":
        return "generate_chat"

    return "retrieve"

graph_builder.add_conditional_edges(
    "classify_question",
    route_question,

    {
        "generate_chat": "generate_chat",
        "retrieve": "retrieve"
    }
)

graph_builder.add_edge(
    "retrieve",
    "generate"
)

graph_builder.add_edge(
    "generate_chat",
    END
)

graph_builder.add_edge(
    "generate",
    END
)

# Existing graph.
rag_graph = graph_builder.compile()

# STREAMING PREPARATION GRAPH
# This graph DOES NOT generate the Gemini answer.
#
# It only:
#
# 1. Classifies the question
# 2. Retrieves PDF documents if required

# START
#   ↓
# classify_question
#   ↓
# ┌───────────────┐
# │               │
# normal          PDF
# │               │
# END            retrieve
#                 │
#                END
#
stream_graph_builder = StateGraph(RAGState)

stream_graph_builder.add_node(
    "classify_question",
    classify_question
)

stream_graph_builder.add_node(
    "retrieve",
    retrieve
)

stream_graph_builder.add_edge(
    START,
    "classify_question"
)

def route_stream_question(state: RAGState):
    if state["question_type"] == "normal":
        return "normal"

    return "retrieve"

stream_graph_builder.add_conditional_edges(
    "classify_question",

    route_stream_question,

    {
        "normal": END,
        "retrieve": "retrieve"
    }
)

stream_graph_builder.add_edge(
    "retrieve",
    END
)

# Graph used by the streaming endpoint.
stream_graph = stream_graph_builder.compile()