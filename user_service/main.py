from fastapi import FastAPI, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from models import Base
from schemas import User, UserCreate, UserUpdate, UserAuthenticate, UserBase
from crud import get_user_by_login, create_user, update_user
from auth import get_password_hash, verify_password, create_access_token, get_current_user_id

from database import SessionLocal, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    hashed_pw = get_password_hash(user.password)
    user.password = hashed_pw
    return create_user(db=db, user=user)

# @app.post("/api/users/authenticate")
# def authenticate_user(credentials: UserAuthenticate, db: Session = Depends(get_db)):
#     db_user = get_user_by_login(db, login=credentials.login)
#     if not db_user or not verify_password(credentials.password, db_user.password):
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#     token = create_access_token(data={"sub": str(db_user.id)})
#     return {"access_token": token, "token_type": "bearer"}

@app.post("/api/users/authenticate")
def authenticate_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = get_user_by_login(db, login=form_data.username)
    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=400, detail="Incorrect login or password")
    token = create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": token, "token_type": "bearer"}

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

@app.get("/api/users/me")
def read_users_me(user_id: str = Depends(get_current_user_id)):
    return {"user_id": user_id}