from sqlalchemy import (
    DDL,
    TIMESTAMP,
    BigInteger,
    Column,
    ForeignKey,
    Integer,
    Text,
    create_engine,
)
from sqlalchemy.dialects.postgresql import TSVECTOR, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# 1. CREATE DATABASE IF NOT EXISTS
TARGET_DB_NAME = "perplexity"
TARGET_DB_URL = f"postgresql://postgres:password@localhost:5432/{TARGET_DB_NAME}"

# createdb -h localhost -U ajay perplexity


# 2. DEFINE MODELS & METADATA
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    user_name = Column(VARCHAR(500))
    email_id = Column(VARCHAR(500), unique=True, index=True)
    created_on = Column(TIMESTAMP(timezone=True))

    sessions = relationship("Session", back_populates="user")


class Session(Base):
    __tablename__ = "sessions"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    timestamp = Column(TIMESTAMP, nullable=False)

    user = relationship("User", back_populates="sessions")
    chats = relationship("Chat", back_populates="session")


class Chat(Base):
    __tablename__ = "chats"
    id = Column(BigInteger, primary_key=True)
    session_id = Column(BigInteger, ForeignKey("sessions.id"), index=True)
    question_text = Column(Text, nullable=False)
    llm_result_text = Column(Text)
    llm_model_id = Column(Integer, ForeignKey("models.id"), nullable=True)
    asked_at = Column(TIMESTAMP)
    answered_at = Column(TIMESTAMP)
    question_tsv = Column(TSVECTOR)
    llm_result_tsv = Column(TSVECTOR)

    session = relationship("Session", back_populates="chats")
    parent = relationship("Chat", remote_side=[id], backref="replies")
    search_results = relationship("SearchResult", back_populates="chat")


class SearchResult(Base):
    __tablename__ = "search_results"
    id = Column(BigInteger, primary_key=True)
    chat_id = Column(BigInteger, ForeignKey("chats.id"), index=True)
    search_result = Column(Text)
    timestamp = Column(TIMESTAMP)

    chat = relationship("Chat", back_populates="search_results")


class Model(Base):
    __tablename__ = "models"
    id = Column(Integer, primary_key=True)
    model_name = Column(VARCHAR)


# 3. CONNECT & CREATE ALL TABLES
engine = create_engine(TARGET_DB_URL, echo=True)
Base.metadata.create_all(engine)


# 4. CREATE TRIGGERS & INDEXES FOR FULL‑TEXT
triggers_and_indexes = [
    DDL(
        """
    CREATE FUNCTION chats_tsv_update() RETURNS trigger AS $$
    BEGIN
      NEW.question_tsv   := to_tsvector('english', NEW.question_text);
      NEW.llm_result_tsv := to_tsvector('english', coalesce(NEW.llm_result_text,''));
      RETURN NEW;
    END
    $$ LANGUAGE plpgsql;
    """
    ),
    DDL(
        """
    CREATE TRIGGER trg_chats_tsv
      BEFORE INSERT OR UPDATE ON chats
      FOR EACH ROW EXECUTE FUNCTION chats_tsv_update();
    """
    ),
    DDL("CREATE INDEX idx_chats_question_tsv ON chats USING GIN (question_tsv);"),
    DDL("CREATE INDEX idx_chats_result_tsv   ON chats USING GIN (llm_result_tsv);"),
]

with engine.connect() as conn:
    for stmt in triggers_and_indexes:
        conn.execute(stmt)

print("Database and tables created successfully.")
