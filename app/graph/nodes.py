from langchain_core.prompts import ChatPromptTemplate

from google import genai
from google.genai import types

from app.graph.state import RAGState
from app.services.vector_service import VectorService
from app.config.settings import settings

# SERVICES
# VectorService is responsible for:
# 1. Query embeddings
# 2. Chroma search
# 3. Existing document embeddings
vector_service = VectorService()

# Used for generating answers.
gemini_client = genai.Client(
    api_key=settings.gemini_api_key
)

# NORMAL CHAT PROMPT
normal_chat_prompt = ChatPromptTemplate.from_template(
    """
You are a friendly and helpful AI assistant.
The user is having a normal conversation with you.
Respond naturally and conversationally.

User message:
{question}
"""
)

# PDF RAG PROMPT
pdf_prompt = ChatPromptTemplate.from_template(
    """
You are a helpful document assistant.
Answer the user's question using ONLY the
provided document context.
Do not use outside knowledge for the
document-related answer.
If the answer cannot be found in the
provided document context, say:
"The information is not available in
the provided document."

Question:
{question}

Document context:
{text_context}
"""
)

# CLASSIFY QUESTION
def classify_question(
    state: RAGState
):
    """
    Decide whether the user is:

    1. Having normal conversation
    2. Asking something that requires the PDF
    For simple conversational messages we do NOT
    perform a vector search.
    This means we also avoid creating a query
    embedding for messages like:
    Hi
    Hello
    How are you?
    Thanks
    Good morning
    """

    question = state["question"].strip()
    # Convert to lowercase so that:
    #
    # "Hi"
    # "HI"
    # "hi"
    #
    # are treated the same.
    question_lower = question.lower()

    # Common normal conversation
    normal_messages = {

    # Greetings
    "hi",
    "hello",
    "hey",
    "hii",
    "hiii",
    "heyy",
    "good morning",
    "good afternoon",
    "good evening",
    "good night",
    "morning",
    "hey there",
    "hello there",

    # How are you
    "how are you",
    "how are you?",
    "how r u",
    "how r u?",
    "how are things",
    "how is it going",
    "how's it going",
    "how have you been",
    "are you okay",

    # Thanks
    "thanks",
    "thanks!",
    "thank you",
    "thank you!",
    "thx",
    "thank u",
    "thanks a lot",
    "many thanks",
    "appreciate it",

    # Goodbye
    "bye",
    "bye!",
    "goodbye",
    "goodbye!",
    "see you",
    "see you later",
    "see ya",
    "talk to you later",
    "have a good day",
    "have a nice day",
    "How you feel today buddy",

    # Confirmation / acknowledgement
    "ok",
    "okay",
    "ok!",
    "okay!",
    "alright",
    "all right",
    "sure",
    "yes",
    "yeah",
    "yep",
    "yup",
    "fine",
    "great",
    "nice",
    "cool",
    "perfect",
    "awesome",
    "got it",
    "understood",

    # About the assistant
    "who are you",
    "who are you?",
    "what are you",
    "what are you?",
    "what is your name",
    "what's your name",
    "tell me about yourself",
    "introduce yourself",

    # Help
    "help",
    "help me",
    "can you help me",
    "can you help me?",
    "i need help",
    "what can you do",
    "what can you do?",
    "how can you help me",
    "thank you very much",
    "tell me a joke",
    "how are you doing today?",
    "thank you so much",

    # Casual conversation
    "nice to meet you",
    "good to meet you",
    "what's up",
    "whats up",
    "what are you doing",
    "are you there",
    "are you online",
    "hello again",

    # Simple compliments
    "you are great",
    "you're great",
    "you are helpful",
    "you're helpful",
    "good job",
    "well done",
    "that's great",
    "that's nice",

    # Simple conversational responses
    "really",
    "really?",
    "okay thanks",
    "ok thanks",
    "thanks for helping",
    "thank you for helping",
    "no problem",
    "never mind",
    "no worries",
    "that's okay"
}

    # Check whether this is a normal message
    if question_lower in normal_messages:

        print(
            f"Question classified as NORMAL: "
            f"{question}"
        )
        return {
            "question_type": "normal"
        }

    # Otherwise treat it as a PDF question
    print(
        f"Question classified as PDF: "
        f"{question}"
    )
    return {
        "question_type": "pdf"
    }

# RETRIEVE NODE
def retrieve(
    state: RAGState
):
    """
    Retrieve relevant chunks from Chroma.
    IMPORTANT:
    This is only executed for PDF questions.
    It creates ONE embedding for the user's
    question using embed_query().
    It does NOT regenerate document embeddings.
    """
    question = state["question"]

    print(
        "Retrieving relevant document chunks..."
    )

    # Search Chroma
    documents = vector_service.search(
        question,
        k=10
    )

    print(
        f"Retrieved {len(documents)} "
        f"document chunks."
    )

    return {
        "documents": documents
    }

# GENERATE NORMAL CHAT RESPONSE
def generate_chat(
    state: RAGState
):
    """
    Generate a normal conversational response.
    Example:
    User:
        Hi
    Response:
        Hello! How can I help you?
    No Chroma search is performed.
    No query embedding is generated.
    """

    question = state["question"]

    # Create prompt
    prompt_value = normal_chat_prompt.invoke(
        {
            "question": question
        }
    )

    prompt_text = prompt_value.to_string()

    # Send prompt to Gemini
    contents = [
        types.Content(
            parts=[
                types.Part.from_text(
                    text=prompt_text
                )
            ]
        )
    ]

    response = (
        gemini_client
        .models
        .generate_content(
            model=settings.gemini_llm_model,
            contents=contents
        )
    )

    return {
        "answer": response.text,
        "documents": []
    }

# GENERATE PDF RESPONSE
def generate(
    state: RAGState
):
    """
    Generate an answer using retrieved PDF chunks.
    This node is used only for PDF questions.
    """

    question = state["question"]
    documents = state["documents"]

    # Build document context
    text_context = []

    for document in documents:

        text_context.append(
            document.page_content
        )

    # Create final prompt
    prompt_value = pdf_prompt.invoke(
        {
            "question": question,

            "text_context": (
                "\n\n".join(
                    text_context
                )
            )
        }
    )

    prompt_text = prompt_value.to_string()

    # Send prompt to Gemini
    contents = [
        types.Content(
            parts=[
                types.Part.from_text(
                    text=prompt_text
                )
            ]
        )
    ]

    response = (
        gemini_client
        .models
        .generate_content(
            model=settings.gemini_llm_model,
            contents=contents
        )
    )

    return {
        "answer": response.text
    }