from sqlalchemy import Column, Integer, String, ARRAY, DateTime
from sqlalchemy.sql import func
from .databases import Base

class Feed(Base):
    __tablename__ = "feed"
    
    id = Column(Integer, primary_key=True, index=True, nullable=False)  
    topics = Column(ARRAY(String), nullable=False)
    vibe = Column(String, server_default="casual")
    max_articles = Column(Integer, server_default='10')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())