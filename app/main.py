from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from . import schemas, crud, auth, database, dependencies
from redis import Redis
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
redis = Redis.from_url(os.getenv("REDIS_URL"))


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


@app.post("/shorten", response_model=schemas.URLOut)
def shorten_url(
        url: schemas.URLCreate,
        db: Session = Depends(database.get_db),
        current_user: schemas.UserOut = Depends(dependencies.get_current_user)
):
    return crud.create_url(db, url, user_id=current_user.id)


@app.get("/{short_code}")
async def redirect_url(short_code: str, db: Session = Depends(database.get_db)):
    db_url = crud.get_url_by_short_code(db, short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")

    # Log click to Redis (basic counter)
    redis.incr(f"clicks:{short_code}")

    return RedirectResponse(url=db_url.original_url)