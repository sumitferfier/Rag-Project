# from fastapi import (
#     APIRouter,
#     Depends,
#     HTTPException
# )

# from sqlalchemy.orm import Session

# from app.auth.database import get_db
# from app.auth.dependencies import get_current_user
# from app.auth.models import User
# from app.services.chat_history_service import ChatHistoryService


# # ---------------------------------------------------------
# # CREATE ROUTER
# # ---------------------------------------------------------
# router = APIRouter(
#     prefix="/api/v1/chat",
#     tags=["Chat History"]
# )


# # ---------------------------------------------------------
# # CREATE CHAT HISTORY SERVICE
# # ---------------------------------------------------------
# chat_history_service = ChatHistoryService()


# # ---------------------------------------------------------
# # CREATE NEW CONVERSATION
# # ---------------------------------------------------------
# @router.post("/conversations")
# def create_conversation(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     conversation = (
#         chat_history_service.create_conversation(
#             db=db,
#             user_id=current_user.id
#         )
#     )

#     return {
#         "id": conversation.id,
#         "title": conversation.title,
#         "created_at": conversation.created_at,
#         "updated_at": conversation.updated_at
#     }


# # ---------------------------------------------------------
# # GET ALL CONVERSATIONS FOR CURRENT USER
# # ---------------------------------------------------------
# @router.get("/conversations")
# def get_conversations(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     conversations = (
#         chat_history_service.get_user_conversations(
#             db=db,
#             user_id=current_user.id
#         )
#     )

#     return [
#         {
#             "id": conversation.id,
#             "title": conversation.title,
#             "created_at": conversation.created_at,
#             "updated_at": conversation.updated_at
#         }
#         for conversation in conversations
#     ]


# # ---------------------------------------------------------
# # GET ONE CONVERSATION WITH ITS MESSAGES
# # ---------------------------------------------------------
# @router.get("/conversations/{conversation_id}")
# def get_conversation(
#     conversation_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     conversation = (
#         chat_history_service.get_conversation(
#             db=db,
#             conversation_id=conversation_id,
#             user_id=current_user.id
#         )
#     )

#     if conversation is None:
#         raise HTTPException(
#             status_code=404,
#             detail="Conversation not found."
#         )

#     messages = (
#         chat_history_service.get_messages(
#             db=db,
#             conversation_id=conversation.id
#         )
#     )

#     return {
#         "id": conversation.id,
#         "title": conversation.title,
#         "created_at": conversation.created_at,
#         "updated_at": conversation.updated_at,
#         "messages": [
#             {
#                 "id": message.id,
#                 "role": message.role,
#                 "content": message.content,
#                 "created_at": message.created_at
#             }
#             for message in messages
#         ]
#     }


# # ---------------------------------------------------------
# # DELETE CONVERSATION
# # ---------------------------------------------------------
# @router.delete("/conversations/{conversation_id}")
# def delete_conversation(
#     conversation_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     deleted = (
#         chat_history_service.delete_conversation(
#             db=db,
#             conversation_id=conversation_id,
#             user_id=current_user.id
#         )
#     )

#     if not deleted:
#         raise HTTPException(
#             status_code=404,
#             detail="Conversation not found."
#         )

#     return {
#         "message": "Conversation deleted successfully."
#     }