from typing import List
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.config.settings import settings
from app.services.embedding_service import EmbeddingService

class VectorService:
    def __init__(self):

        # GEMINI EMBEDDING SERVICE
        self.embedding_service = EmbeddingService()

        # CHROMA VECTOR DATABASE
        self.vector_store = Chroma(
            collection_name="rag_documents",
            embedding_function=self.embedding_service,
            persist_directory=settings.chroma_persist_directory
        )

        # Print current number of stored records
        print(
            "Chroma records:",
            self.vector_store._collection.count()
        )

    # CHECK WHETHER PDF IS ALREADY INDEXED
    def has_text_for_pdf(
        self,
        pdf_name: str
    ) -> bool:

        """
        Check whether text chunks from this PDF
        already exist in Chroma.
        We use the pdf_name stored in metadata.
        """

        try:
            result = self.vector_store._collection.get(
                where={
                    "pdf_name": pdf_name
                },
                limit=1
            )
            documents = result.get(
                "documents",
                []
            )
            return len(documents) > 0
        except Exception as e:
            print(
                f"Error checking indexed PDF: {e}"
            )
            return False

    # ADD DOCUMENTS TO CHROMA
    def add_documents(
        self,
        documents: List[Document],
        pdf_name: str
    ):

        """
        Generate embeddings for the PDF chunks
        and store them in Chroma.

        This method should ONLY be called when
        the PDF has not already been indexed.
        """

        # Nothing to add
        if not documents:
            print(
                f"No documents to add for {pdf_name}"
            )
            return

        # Double-check duplicate indexing
        if self.has_text_for_pdf(pdf_name):

            print(
                f"Text already indexed for {pdf_name}"
            )
            return

        # STEP 1: EXTRACT TEXT
        texts = [
            document.page_content
            for document in documents
        ]

        # STEP 2: GENERATE DOCUMENT EMBEDDINGS
        print(
            f"Generating embeddings for "
            f"{len(texts)} chunks of {pdf_name}..."
        )

        embeddings = (
            self.embedding_service
            .embed_documents(
                texts
            )
        )

        # STEP 3: CREATE UNIQUE IDS
        ids = []
        metadatas = []
        pdf_stem = Path(pdf_name).stem
        for index, document in enumerate(
            documents
        ):

            document_id = (
                f"{pdf_stem}_text_{index}"
            )

            ids.append(
                document_id
            )

            # Copy existing metadata
            metadata = dict(
                document.metadata
            )

            # Store PDF name
            metadata["pdf_name"] = pdf_name

            # Identify document type
            metadata["type"] = "text"

            # Store chunk number
            metadata["chunk_index"] = index

            metadatas.append(
                metadata
            )

        # STEP 4: STORE IN CHROMA
        self.vector_store._collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

        # STEP 5: LOG RESULT
        print(
            f"Added {len(documents)} "
            f"text chunks from {pdf_name} "
            f"to Chroma."
        )

        print(
            "Total Chroma records:",
            self.vector_store._collection.count()
        )

    # SEARCH EXISTING EMBEDDINGS
    def search(
        self,
        question: str,
        k: int = 4
    ) -> List[Document]:

        """
        Search Chroma for the chunks most relevant
        to the user's question.
        IMPORTANT:
        This does NOT generate document embeddings again.
        It only generates ONE embedding for the question
        using embed_query().
        """

        # STEP 1: CREATE QUERY EMBEDDING
        query_embedding = (
            self.embedding_service
            .embed_query(
                question
            )
        )

        # STEP 2: SEARCH EXISTING CHROMA VECTORS
        result = (
            self.vector_store._collection
            .query(
                query_embeddings=[
                    query_embedding
                ],
                n_results=k
            )
        )

        # STEP 3: CONVERT RESULTS TO DOCUMENT OBJECTS
        documents = []
        result_documents = result.get(
            "documents",
            [[]]
        )[0]

        result_metadatas = result.get(
            "metadatas",
            [[]]
        )[0]

        for index, text in enumerate(
            result_documents
        ):

            metadata = {}
            if index < len(result_metadatas):
                metadata = (
                    result_metadatas[index]
                    or {}
                )

            document = Document(
                page_content=text,
                metadata=metadata
            )

            documents.append(
                document
            )

        print(
            f"Retrieved {len(documents)} "
            f"relevant chunks."
        )

        return documents

    # GET RETRIEVER
    def get_retriever(self):

        """
        Return a LangChain retriever.
        This uses the existing vectors stored
        inside Chroma.
        """
        retriever = (
            self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": 4
                }
            )
        )
        return retriever

    # QUERY EMBEDDING
    def get_query_embedding(
        self,
        question: str
    ):
        """
        Generate an embedding for the question.
        This is used for querying.
        It does NOT embed the PDF documents again.
        """
        return (
            self.embedding_service
            .embed_query(
                question
            )
        )

    # GET INDEXED PDF NAMES
    def get_indexed_pdfs(self) -> List[str]:

        """
        Return a list of PDFs currently indexed
        in Chroma.
        """

        result = (
            self.vector_store._collection.get()
        )

        metadatas = result.get(
            "metadatas",
            []
        )

        pdf_names = set()

        for metadata in metadatas:

            if not metadata:
                continue

            pdf_name = metadata.get(
                "pdf_name"
            )

            if pdf_name:
                pdf_names.add(
                    pdf_name
                )

        return sorted(
            pdf_names
        )