from sqlalchemy import (
    Column, Integer, String, Text, DateTime, 
    ForeignKey, Boolean, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(50), unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    conversations = relationship("Conversation", back_populates="user")
    
    # Индексы для быстрого поиска
    __table_args__ = (
        Index('idx_user_telegram_id', 'telegram_id'),
    )

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    context_data = Column(Text)  # JSON с контекстом диалога
    
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    text = Column(Text, nullable=False)
    is_from_user = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    message_metadata = Column(Text)  # Дополнительные данные
    
    conversation = relationship("Conversation", back_populates="messages")

class KnowledgeBase(Base):
    __tablename__ = 'knowledge_base'
    
    id = Column(Integer, primary_key=True)
    url = Column(String(500), unique=True)
    title = Column(String(300))
    content = Column(Text)
    category = Column(String(200))
    tags = Column(String(500))  # Теги через запятую
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_kb_category', 'category'),
        Index('idx_kb_title', 'title'),
    )