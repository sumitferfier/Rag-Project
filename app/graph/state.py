# Responsibility:
# Define the information that travels through our graph.
from typing import List
from typing_extensions import TypedDict
from langchain_core.documents import Document

class RAGState(TypedDict):

    # USER QUESTION
    question: str

    # QUESTION TYPE
    question_type: str

    # RETRIEVED DOCUMENTS
    documents: List[Document]

    # FINAL ANSWER
    answer: str