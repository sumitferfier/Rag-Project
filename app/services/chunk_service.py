from pathlib import Path
from typing import List

from langchain_core.documents import Document

class ChunkService:

    def __init__(self):
        self.chunk_directory = Path("data/chunks")
        self.chunk_directory.mkdir(
            parents=True,
            exist_ok=True
        )

    def save_chunks(
        self,
        pdf_name: str,
        chunks: List[Document]
    ) -> str:

        pdf_stem = Path(pdf_name).stem

        chunk_file = (
            self.chunk_directory
            / f"{pdf_stem}_chunks.txt"
        )

        with open(
            chunk_file,
            "w",
            encoding="utf-8"
        ) as file:

            for index, chunk in enumerate(
                chunks,
                start=1
            ):

                source = chunk.metadata.get(
                    "source",
                    pdf_name
                )

                page = chunk.metadata.get(
                    "page",
                    "unknown"
                )

                file.write(
                    "\n"
                    + "=" * 70
                    + "\n"
                )

                file.write(
                    f"CHUNK_ID: {index}\n"
                )

                file.write(
                    f"SOURCE: {source}\n"
                )

                file.write(
                    f"PAGE: {page}\n"
                )

                file.write(
                    "=" * 70
                    + "\n\n"
                )

                file.write(
                    chunk.page_content
                )

                file.write("\n\n")

        return str(chunk_file)