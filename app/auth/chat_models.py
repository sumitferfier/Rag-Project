# from datetime import datetime

# from sqlalchemy import (
#     Column,
#     Integer,
#     String,
#     Text,
#     DateTime,
#     ForeignKey
# )

# from sqlalchemy.orm import relationship

# from app.auth.database import Base


# # =========================================================
# # CHAT CONVERSATION MODEL
# # =========================================================
# #
# # Represents one complete chat/conversation.
# #
# # Example:
# #
# # User
# #   ↓
# # Conversation: "Leave Policy"
# #   ↓
# # Messages
# #
# #   User: What is the leave policy?
# #   AI:   According to the PDF...
# #
# #   User: How many leaves can I take?
# #   AI:   You can take...
# #
# # =========================================================

# class ChatConversation(Base):

#     # Database table name
#     __tablename__ = "chat_conversations"


#     # -----------------------------------------------------
#     # PRIMARY KEY
#     # -----------------------------------------------------

#     id = Column(
#         Integer,
#         primary_key=True,
#         index=True
#     )


#     # -----------------------------------------------------
#     # USER ID
#     # -----------------------------------------------------
#     #
#     # Connects the conversation to the logged-in user.
#     #
#     # users.id → chat_conversations.user_id
#     #
#     # This allows us to show only the current user's
#     # conversations.
#     # -----------------------------------------------------

#     user_id = Column(
#         Integer,
#         ForeignKey("users.id"),
#         nullable=False,
#         index=True
#     )


#     # -----------------------------------------------------
#     # CONVERSATION TITLE
#     # -----------------------------------------------------
#     #
#     # Example:
#     #
#     # "Leave Policy"
#     # "Attendance Rules"
#     # "Employee Benefits"
#     #
#     # Initially this can be based on the first question.
#     # -----------------------------------------------------

#     title = Column(
#         String(255),
#         nullable=False
#     )


#     # -----------------------------------------------------
#     # CREATED AT
#     # -----------------------------------------------------

#     created_at = Column(
#         DateTime,
#         default=datetime.utcnow,
#         nullable=False
#     )


#     # -----------------------------------------------------
#     # UPDATED AT
#     # -----------------------------------------------------
#     #
#     # This will later allow us to show the most recently
#     # updated conversations first.
#     # -----------------------------------------------------

#     updated_at = Column(
#         DateTime,
#         default=datetime.utcnow,
#         onupdate=datetime.utcnow,
#         nullable=False
#     )


#     # -----------------------------------------------------
#     # RELATIONSHIP WITH MESSAGES
#     # -----------------------------------------------------
#     #
#     # One conversation can contain many messages.
#     #
#     # Example:
#     #
#     # Conversation
#     #      ↓
#     # Message 1
#     # Message 2
#     # Message 3
#     # Message 4
#     #
#     # delete-orphan means that when a conversation is
#     # deleted, its messages are also deleted.
#     # -----------------------------------------------------

#     messages = relationship(
#         "ChatMessage",
#         back_populates="conversation",
#         cascade="all, delete-orphan",
#         order_by="ChatMessage.created_at"
#     )


# # =========================================================
# # CHAT MESSAGE MODEL
# # =========================================================
# #
# # Represents one individual message inside a conversation.
# #
# # Example:
# #
# # role = "user"
# # content = "What is the leave policy?"
# #
# # OR
# #
# # role = "assistant"
# # content = "According to the document..."
# #
# # =========================================================

# class ChatMessage(Base):

#     # Database table name
#     __tablename__ = "chat_messages"


#     # -----------------------------------------------------
#     # PRIMARY KEY
#     # -----------------------------------------------------

#     id = Column(
#         Integer,
#         primary_key=True,
#         index=True
#     )


#     # -----------------------------------------------------
#     # CONVERSATION ID
#     # -----------------------------------------------------
#     #
#     # Connects this message to a conversation.
#     #
#     # chat_conversations.id
#     #          ↓
#     # chat_messages.conversation_id
#     #
#     # -----------------------------------------------------

#     conversation_id = Column(
#         Integer,
#         ForeignKey("chat_conversations.id"),
#         nullable=False,
#         index=True
#     )


#     # -----------------------------------------------------
#     # MESSAGE ROLE
#     # -----------------------------------------------------
#     #
#     # Possible values:
#     #
#     # "user"
#     # "assistant"
#     #
#     # -----------------------------------------------------

#     role = Column(
#         String(20),
#         nullable=False
#     )


#     # -----------------------------------------------------
#     # MESSAGE CONTENT
#     # -----------------------------------------------------
#     #
#     # Text of the actual question or answer.
#     #
#     # Text is used because an answer can be quite long.
#     # -----------------------------------------------------

#     content = Column(
#         Text,
#         nullable=False
#     )


#     # -----------------------------------------------------
#     # CREATED AT
#     # -----------------------------------------------------

#     created_at = Column(
#         DateTime,
#         default=datetime.utcnow,
#         nullable=False
#     )

#     # RELATIONSHIP WITH CONVERSATION
#     conversation = relationship(
#         "ChatConversation",
#         back_populates="messages"
#     )