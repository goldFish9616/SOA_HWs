from sqlalchemy.orm import Session
from models import User as UserModel 
from schemas import UserCreate, UserUpdate

def get_user_by_login(db: Session, login: str):
    return db.query(UserModel).filter(UserModel.login == login).first()

def create_user(db: Session, user: UserCreate):
    db_user = UserModel(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user: UserUpdate):
    db_user = get_user_by_login(db, login=user.login)
    for key, value in user.dict().items():
        if value is not None:
            setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user