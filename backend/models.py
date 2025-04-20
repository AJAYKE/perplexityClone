from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import TIMESTAMP, BigInteger, Column, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import TSVECTOR, VARCHAR
from sqlalchemy.orm import relationship

# Initialize the SQLAlchemy db instance
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    user_name = Column(VARCHAR(500), nullable=True)
    email_id = Column(VARCHAR(500), unique=True, index=True, nullable=True)
    created_on = Column(TIMESTAMP(timezone=True), nullable=True)

    sessions = relationship("Session", back_populates="user")


class Session(db.Model):
    __tablename__ = "sessions"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True, nullable=True)
    timestamp = Column(TIMESTAMP, nullable=False)

    user = relationship("User", back_populates="sessions")
    chats = relationship("Chat", back_populates="session")


class Model(db.Model):
    __tablename__ = "models"
    id = Column(Integer, primary_key=True)
    model_name = Column(VARCHAR, nullable=False)

    chats = relationship("Chat", back_populates="model")


class Chat(db.Model):
    __tablename__ = "chats"
    id = Column(BigInteger, primary_key=True)
    session_id = Column(
        BigInteger, ForeignKey("sessions.id"), index=True, nullable=True
    )
    question_text = Column(Text, nullable=False)
    llm_result_text = Column(Text, nullable=True)
    llm_model_id = Column(Integer, ForeignKey("models.id"), nullable=True)
    asked_at = Column(TIMESTAMP, nullable=True)
    answered_at = Column(TIMESTAMP, nullable=True)
    question_tsv = Column(TSVECTOR)
    llm_result_tsv = Column(TSVECTOR)

    session = relationship("Session", back_populates="chats")
    model = relationship("Model", back_populates="chats")
    search_results = relationship("SearchResult", back_populates="chat")


class SearchResult(db.Model):
    __tablename__ = "search_results"
    id = Column(BigInteger, primary_key=True)
    chat_id = Column(BigInteger, ForeignKey("chats.id"), index=True, nullable=False)
    search_result = Column(Text, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=True)

    chat = relationship("Chat", back_populates="search_results")
