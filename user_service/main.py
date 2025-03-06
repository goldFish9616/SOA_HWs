from fastapi import FastAPI, Query, HTTPException, Depends
from sqlalchemy.orm import Session

from models import Base
from schemas import User, UserCreate, UserUpdate, UserAuthenticate, UserBase
from crud import get_user_by_login, create_user, update_user

from database import SessionLocal, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/users/register", response_model=User)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_login(db, login=user.login)
    if db_user:
        raise HTTPException(status_code=400, detail="Login already registered")
    return create_user(db=db, user=user)

@app.post("/api/users/authenticate")
def authenticate_user(credentials: UserAuthenticate, db: Session = Depends(get_db)):
    db_user = get_user_by_login(db, login=credentials.login)
    if db_user is None or db_user.password != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid login or password")
    return {"message": "Authenticated successfully"}

@app.put("/api/users/profile", response_model=User)
def update_profile(profile: UserUpdate, db: Session = Depends(get_db)):
    db_user = get_user_by_login(db, login=profile.login)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return update_user(db=db, user=profile)

@app.get("/api/users/profile", response_model=User)
def get_profile(login: str, db: Session = Depends(get_db)):
    db_user = get_user_by_login(db, login=login)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user