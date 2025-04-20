from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from . import schemas, crud, auth, database, dependencies
# Remove redis import
# from redis import Redis
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

# Allowing all origins (replace with specific origins for production)
app.add_middleware(
    CORSMiddleware,  # CORSMiddleware is the middleware to be added
    allow_origins=["*"],  # or list the specific domains like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Remove redis initialization and usage
# redis = Redis.from_url(os.getenv("REDIS_URL"))

@app.on_event("startup")
def startup():
    database.Base.metadata.create_all(bind=database.engine)

@app.post("/shorten", response_model=schemas.URLOut)
def shorten_url(
    url: schemas.URLCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.UserOut = Depends(dependencies.get_current_user)
):
    return crud.create_url(db, url, user_id=current_user.id)

@app.post("/auth/login")
def login(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = auth.create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/{short_code}")
async def redirect_url(short_code: str, db: Session = Depends(database.get_db)):
    db_url = crud.get_url_by_short_code(db, short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")

    # Remove Redis log click functionality
    # redis.incr(f"clicks:{short_code}")

    return RedirectResponse(url=db_url.original_url)

@app.post("/auth/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.create_user(db, user)
    return {"message": "User created successfully", "user": db_user}
