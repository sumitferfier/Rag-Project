from typing import List
import requests
from app.config.settings import settings
class EmbeddingService:
    def __init__(self):

        # Jina Embeddings API endpoint
        self.api_url = "https://api.jina.ai/v1/embeddings"
        self.api_key = settings.jina_api_key
        self.model = settings.jina_embedding_model
        self.output_dimension = 768

        # Number of texts sent in one API request
        self.batch_size = 20

    # Common method used for document and query embeddings
    def _embed(
        self,
        texts: List[str],
        task: str
    ) -> List[List[float]]:

        if not texts:
            return []

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        all_embeddings = []
        for start_index in range(
            0,
            len(texts),
            self.batch_size
        ):

            end_index = (
                start_index
                + self.batch_size
            )

            batch = texts[
                start_index:end_index
            ]

            print(
                f"Jina embedding batch: "
                f"{start_index + 1}-"
                f"{min(end_index, len(texts))} "
                f"of {len(texts)} chunks"
            )

            # Request body sent to Jina
            payload = {
                "model": self.model,

                # retrieval.passage -> PDF chunks
                # retrieval.query   -> user question
                "task": task,

                # Vector dimension
                "dimensions": self.output_dimension,

                # Texts to embed
                "input": batch
            }

            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=120
                )

                # Raise an exception if Jina returns
                # an HTTP error such as 401, 429, 500, etc.
                response.raise_for_status()
            except requests.exceptions.RequestException as e:

                raise RuntimeError(
                    f"Jina embedding API request failed: {e}"
                ) from e

            result = response.json()
            data = result.get("data", [])

            # Make sure Jina returned one embedding
            # for every input text.
            if len(data) != len(batch):

                raise ValueError(
                    "Jina embedding count mismatch. "
                    f"Expected {len(batch)} embeddings "
                    f"but received {len(data)}."
                )

            # Jina returns an index for every embedding.
            # Sorting guarantees that the embeddings
            # stay in the same order as the input texts.
            data = sorted(
                data,
                key=lambda item: item["index"]
            )

            batch_embeddings = [
                item["embedding"]
                for item in data
            ]

            all_embeddings.extend(
                batch_embeddings
            )

        # Final safety check
        if len(all_embeddings) != len(texts):

            raise ValueError(
                "Final Jina embedding count mismatch. "
                f"Texts: {len(texts)}, "
                f"Embeddings: {len(all_embeddings)}"
            )
        return all_embeddings

    # PDF document embeddings
    def embed_documents(
        self,
        texts: List[str]
    ) -> List[List[float]]:

        """
        Creates embeddings for PDF chunks.

        We use retrieval.passage because these
        texts are documents/passages that will
        later be searched.
        """

        return self._embed(
            texts=texts,
            task="retrieval.passage"
        )

    # User question embedding
    def embed_query(
        self,
        question: str
    ) -> List[float]:

        """
        Creates an embedding for the user's question.

        We use retrieval.query because this text
        is used as a search query.
        """

        embeddings = self._embed(
            texts=[question],
            task="retrieval.query"
        )

        if not embeddings:

            raise ValueError(
                "Jina returned no embedding for the question."
            )
        return embeddings[0]

    # Generic text embedding
    def embed_text(
        self,
        text: str
    ) -> List[float]:

        """
        Creates a passage/document embedding
        for a single piece of text.
        """

        embeddings = self._embed(
            texts=[text],
            task="retrieval.passage"
        )
        if not embeddings:
            raise ValueError(
                "Jina returned no embedding for the text."
            )
        return embeddings[0]