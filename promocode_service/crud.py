from sqlalchemy.orm import Session
from models import Promo, Comment
from datetime import datetime

def create_promo(db: Session, data):
    promo = Promo(**data)
    db.add(promo)
    db.commit()
    db.refresh(promo)
    return promo

def get_promo(db: Session, promo_id: str):
    return db.query(Promo).filter(Promo.id == promo_id).first()

def delete_promo(db: Session, promo_id: str):
    promo = get_promo(db, promo_id)
    if promo:
        db.delete(promo)
        db.commit()
    return promo

def update_promo(db: Session, promo_id: str, data):
    promo = get_promo(db, promo_id)
    if promo:
        for key, value in data.items():
            setattr(promo, key, value)
        promo.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(promo)
    return promo

def list_promos(db: Session, skip: int, limit: int):
    return db.query(Promo).offset(skip).limit(limit).all()

def create_comment(db: Session, promo_id: str, client_id: str, text: str):
    comment = Comment(
        promo_code_id=promo_id,
        client_id=client_id,
        text=text
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

def get_comments_by_promo_code(db: Session, promo_id: str, skip: int = 0, limit: int = 10):
    total = db.query(Comment).filter(Comment.promo_code_id == promo_id).count()
    comments = (
        db.query(Comment)
        .filter(Comment.promo_code_id == promo_id)
        .order_by(Comment.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return comments, total

def count_comments_by_promo_id(db: Session, promo_id: str):
    return db.query(Comment).filter(Comment.promo_code_id == promo_code_id).count()
