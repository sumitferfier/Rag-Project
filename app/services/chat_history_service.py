# from datetime import datetime

# from sqlalchemy.orm import Session

# from app.auth.chat_models import (
#     ChatConversation,
#     ChatMessage
# )


# class ChatHistoryService:

#     # ============================================================
#     # CREATE CONVERSATION
#     # ============================================================

#     def create_conversation(
#         self,
#         db: Session,
#         user_id: int,
#         title: str
#     ) -> ChatConversation:

#         conversation = ChatConversation(
#             user_id=user_id,
#             title=title
#         )

#         db.add(conversation)

#         db.commit()

#         db.refresh(conversation)

#         return conversation


#     # ============================================================
#     # GET USER CONVERSATIONS
#     # ============================================================

#     def get_user_conversations(
#         self,
#         db: Session,
#         user_id: int
#     ) -> list[ChatConversation]:

#         return (
#             db.query(ChatConversation)
#             .filter(
#                 ChatConversation.user_id == user_id
#             )
#             .order_by(
#                 ChatConversation.updated_at.desc()
#             )
#             .all()
#         )


#     # ============================================================
#     # GET ONE CONVERSATION
#     #
#     # Only return the conversation if it belongs
#     # to the logged-in user.
#     # ============================================================

#     def get_conversation(
#         self,
#         db: Session,
#         conversation_id: int,
#         user_id: int
#     ) -> ChatConversation | None:

#         return (
#             db.query(ChatConversation)
#             .filter(
#                 ChatConversation.id == conversation_id,
#                 ChatConversation.user_id == user_id
#             )
#             .first()
#         )


#     # ============================================================
#     # SAVE MESSAGE
#     # ============================================================

#     def save_message(
#         self,
#         db: Session,
#         conversation_id: int,
#         role: str,
#         content: str
#     ) -> ChatMessage:

#         message = ChatMessage(
#             conversation_id=conversation_id,
#             role=role,
#             content=content
#         )

#         db.add(message)

#         # Update conversation timestamp so that
#         # recently used conversations appear first.
#         conversation = (
#             db.query(ChatConversation)
#             .filter(
#                 ChatConversation.id == conversation_id
#             )
#             .first()
#         )

#         if conversation:

#             conversation.updated_at = (
#                 datetime.utcnow()
#             )

#         db.commit()

#         db.refresh(message)

#         return message


#     # ============================================================
#     # SAVE USER MESSAGE
#     # ============================================================

#     def save_user_message(
#         self,
#         db: Session,
#         conversation_id: int,
#         content: str
#     ) -> ChatMessage:

#         return self.save_message(
#             db=db,
#             conversation_id=conversation_id,
#             role="user",
#             content=content
#         )


#     # ============================================================
#     # SAVE ASSISTANT MESSAGE
#     # ============================================================

#     def save_assistant_message(
#         self,
#         db: Session,
#         conversation_id: int,
#         content: str
#     ) -> ChatMessage:

#         return self.save_message(
#             db=db,
#             conversation_id=conversation_id,
#             role="assistant",
#             content=content
#         )


#     # ============================================================
#     # UPDATE TITLE
#     # ============================================================

#     def update_title(
#         self,
#         db: Session,
#         conversation_id: int,
#         user_id: int,
#         title: str
#     ) -> ChatConversation | None:

#         conversation = self.get_conversation(
#             db=db,
#             conversation_id=conversation_id,
#             user_id=user_id
#         )

#         if conversation is None:
#             return None

#         conversation.title = title

#         conversation.updated_at = (
#             datetime.utcnow()
#         )

#         db.commit()

#         db.refresh(conversation)

#         return conversation


#     # ============================================================
#     # DELETE CONVERSATION
#     # ============================================================

#     def delete_conversation(
#         self,
#         db: Session,
#         conversation_id: int,
#         user_id: int
#     ) -> bool:

#         conversation = self.get_conversation(
#             db=db,
#             conversation_id=conversation_id,
#             user_id=user_id
#         )

#         if conversation is None:
#             return False

#         db.delete(conversation)

#         db.commit()

#         return True


# # ================================================================
# # SINGLE SERVICE INSTANCE
# # ================================================================

# chat_history_service = ChatHistoryService()