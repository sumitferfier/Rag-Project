import os
import shutil
import json

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends
)

from fastapi.responses import StreamingResponse
from app.config.settings import settings
from app.schemas.rag_schema import AskRequest
from app.services.rag_service import RagService

# JWT AUTHENTICATION
from app.auth.dependencies import get_current_user
from app.auth.models import User

# CREATE ROUTER
router = APIRouter(
    prefix="/api/v1/rag",
    tags=["RAG"]
)

# CREATE RAG SERVICE
rag_service = RagService()

# UPLOAD PDF
@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),

    # JWT authentication
    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE PDF
    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # CREATE PDF DIRECTORY
    os.makedirs(
        settings.pdf_directory,
        exist_ok=True
    )

    # CREATE FILE PATH
    file_path = os.path.join(
        settings.pdf_directory,
        file.filename
    )

    # SAVE PDF
    try:

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save PDF: {str(e)}"
        )

    # PROCESS PDF
    try:

        result = rag_service.process_pdf(
            file_path
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process PDF: {str(e)}"
        )

    # RESPONSE
    return {

        "message":
            "PDF uploaded and indexed successfully.",

        "filename":
            file.filename,

        "pages":
            result["pages"],

        "chunks":
            result["chunks"]

    }

# ASK QUESTION
@router.post("/ask")
async def ask_question(
    request: AskRequest,

    # JWT authentication
    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE QUESTION
    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # EXECUTE RAG GRAPH
    try:

        result = rag_service.ask_question(
            request.question
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate answer: {str(e)}"
        )

    # RESPONSE
    return result

# STREAMING ASK QUESTION
# This endpoint sends the Gemini response chunk-by-chunk.
@router.post("/ask/stream")
async def ask_question_stream(
    request: AskRequest,

    # JWT authentication
    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE QUESTION
    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )


    # SSE EVENT GENERATOR
    # This function produces events continuously.
    # FastAPI sends each yielded event to the frontend.
    async def event_generator():

        try:

            # Start RAG streaming
            for event in rag_service.stream_question(
                request.question
            ):

                # Convert Python dictionary → JSON
                data = json.dumps(
                    event,
                    ensure_ascii=False
                )

                # SSE FORMAT
                # data: {...}
                # Blank line indicates end of event.
                yield (
                    f"data: {data}\n\n"
                )
        except Exception as e:

            # Log backend error
            print(
                "Streaming error:",
                str(e)
            )

            # Send error to frontend
            error_data = json.dumps(

                {
                    "type": "error",
                    "message": str(e)
                },
                ensure_ascii=False

            )

            yield (
                f"data: {error_data}\n\n"
            )

    # RETURN STREAMING RESPONSE
    return StreamingResponse(

        event_generator(),

        # Tell client this is Server-Sent Events.
        media_type="text/event-stream",
        headers={

            # Prevent caching.
            "Cache-Control":
                "no-cache",

            # Keep connection alive.
            "Connection":
                "keep-alive",

            # Prevent proxy buffering.
            "X-Accel-Buffering":
                "no"

        }

    )