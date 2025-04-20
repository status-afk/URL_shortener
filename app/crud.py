from sqlalchemy.orm import Session
from . import models, schemas
from .auth import get_password_hash
import hashlib
from fastapi import HTTPException

def get_url_by_short_code(db: Session, short_code: str):
    return db.query(models.URL).filter(models.URL.short_code == short_code).first()

def base62_encode(num: int) -> str:
    """Convert an integer to a base62 string."""
    if num == 0:
        return "0"
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    result = ""
    while num:
        num, rem = divmod(num, 62)
        result = chars[rem] + result
    return result


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_url(db: Session, url: schemas.URLCreate, user_id: int = None):
    # Generate short code
    short_code = url.custom_alias
    if not short_code:
        # Convert Url object to string before encoding
        hash_obj = hashlib.md5(str(url.original_url).encode())
        short_code = base62_encode(int(hash_obj.hexdigest(), 16))[:7]

    # If custom alias isn't provided, handle collision by regenerating short code
    if not url.custom_alias:
        existing = db.query(models.URL).filter(models.URL.short_code == short_code).first()
        while existing:
            # Generate a new short code if the current one is already in use
            hash_obj = hashlib.md5(str(url.original_url + str(existing.id)).encode())
            short_code = base62_encode(int(hash_obj.hexdigest(), 16))[:7]
            existing = db.query(models.URL).filter(models.URL.short_code == short_code).first()

    db_url = models.URL(
        original_url=str(url.original_url),  # Convert to string for storage
        short_code=short_code,
        user_id=user_id
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


