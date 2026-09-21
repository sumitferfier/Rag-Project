from pathlib import Path

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)
from google.genai import types

from app.services.pdf_service import PdfService
from app.services.vector_service import VectorService
from app.services.chunk_service import ChunkService

from app.graph.rag_graph import (
    rag_graph,
    stream_graph
)

from app.graph.nodes import (
    gemini_client,
    normal_chat_prompt,
    pdf_prompt
)
from app.config.settings import settings
class RagService:
    def __init__(self):

        self.pdf_service = PdfService()
        self.vector_service = VectorService()
        self.chunk_service = ChunkService()
        self.text_splitter = (
            RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=50
            )
        )

    # PROCESS PDF
    def process_pdf(
        self,
        pdf_path: str
    ):

        pdf_name = Path(pdf_path).name

        # STEP 1: Load PDF text
        documents = (
            self.pdf_service.load_pdf(
                pdf_path
            )
        )

        # STEP 2: Split PDF into chunks
        chunks = (
            self.text_splitter
            .split_documents(
                documents
            )
        )

        # STEP 3: Save chunks locally
        chunk_file = (
            self.chunk_service.save_chunks(
                pdf_path,
                chunks
            )
        )

        # STEP 4: Check whether PDF is already indexed
        text_already_exists = (
            self.vector_service
            .has_text_for_pdf(
                pdf_name
            )
        )

        # STEP 5: Generate embeddings and store chunks
        if text_already_exists:
            print(
                f"Text already indexed for {pdf_name}"
            )
        else:

            self.vector_service.add_documents(
                chunks,
                pdf_name
            )

        return {
            "pages": len(documents),
            "chunks": len(chunks),
            "chunk_file": chunk_file,
            "text_indexed": True

        }

    # NORMAL ASK QUESTION
    # This is your existing /ask functionality.
    # We are NOT changing it.
    def ask_question(
        self,
        question: str
    ):
        # Initial LangGraph state
        initial_state = {
            "question": question,
            "question_type": "",
            "documents": [],
            "answer": ""

        }

        # Run existing LangGraph
        result = rag_graph.invoke(
            initial_state
        )

        # Extract sources
        sources = [
            document.metadata
            for document in result["documents"]

        ]
        return {
            "answer": result["answer"],
            "sources": sources
        }

    # STREAM QUESTION
    # This method is used by:
    # POST /api/v1/rag/ask/stream
    # It performs:
    # LangGraph
    #     ↓
    # classify question
    #     ↓
    # retrieve PDF chunks
    #     ↓
    # Gemini streaming
    def stream_question(
        self,
        question: str
    ):

        # STEP 1: Initial LangGraph state
        initial_state = {
            "question": question,
            "question_type": "",
            "documents": [],
            "answer": ""
        }

        # STEP 2: Run streaming preparation graph
        # This graph performs:
        # 1. Question classification
        # 2. PDF retrieval
        result = stream_graph.invoke(
            initial_state
        )

        # STEP 3: Get question type
        question_type = result.get(
            "question_type",
            "pdf"
        )

        # NORMAL CHAT
        # Example:
        # Hello
        # How are you?
        # Thank you
        # No PDF retrieval is required.
        if question_type == "normal":

            # Build normal conversation prompt
            prompt_value = normal_chat_prompt.invoke(
                {
                    "question": question
                }

            )

            # Convert prompt to string.
            prompt_text = (prompt_value.to_string())

            # Gemini content
            contents = [
                types.Content(
                    parts=[
                        types.Part.from_text(
                            text=prompt_text
                        )

                    ]

                )

            ]

            # REAL GEMINI STREAMING
            response_stream = (
                gemini_client
                .models
                .generate_content_stream(
                    model=settings.gemini_llm_model,
                    contents=contents
                )
            )

            # Send Gemini chunks
            for chunk in response_stream:

                # Some Gemini chunks may not contain text.
                if not chunk.text:
                    continue

                # Send one chunk to the FastAPI route.
                yield {
                    "type": "chunk",
                    "content": chunk.text

                }

            # Tell frontend generation is complete.
            yield {
                "type": "done"
            }
            return

        # PDF QUESTION
        documents = result.get(
            "documents",
            []
        )

        # STEP 4: Build document context
        text_context = []

        for document in documents:

            text_context.append(
                document.page_content
            )

        # STEP 5: Build PDF prompt
        prompt_value = pdf_prompt.invoke(
            {

                "question": question,
                "text_context":
                    "\n\n".join(
                        text_context
                    )
            }
        )

        # Convert prompt to string.
        prompt_text = (
            prompt_value.to_string()
        )

        # STEP 6: Create Gemini content
        contents = [
            types.Content(
                parts=[
                    types.Part.from_text(
                        text=prompt_text
                    )
                ]
            )
        ]

        # STEP 7: Start Gemini streaming
        response_stream = (
            gemini_client
            .models
            .generate_content_stream(
                model=settings.gemini_llm_model,
                contents=contents
            )
        )

        # STEP 8: Send every Gemini chunk
        for chunk in response_stream:
            # Ignore chunks without text.
            if not chunk.text:
                continue

            # Send chunk to FastAPI.
            yield {
                "type": "chunk",
                "content": chunk.text
            }

        # STEP 9: Send sources
        # Sources are sent AFTER Gemini finishes generating.
        sources = [
            document.metadata
            for document in documents
        ]

        yield {
            "type": "sources",
            "sources": sources
        }

        # STEP 10: Tell frontend streaming is complete.
        yield {
            "type": "done"
        }