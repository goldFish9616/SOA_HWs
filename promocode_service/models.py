from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Promo(Base):
    __tablename__ = "promocode"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(String)
    creator_id = Column(String, nullable=False)
    discount = Column(Float, nullable=False)
    code = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    comments = relationship("Comment", back_populates="promo_code", cascade="all, delete")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    promo_code_id = Column(String, ForeignKey("promocode.id"), nullable=False)  # <-- fixed type
    client_id = Column(String, nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    promo_code = relationship("Promo", back_populates="comments")


