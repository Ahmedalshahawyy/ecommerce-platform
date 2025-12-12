from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

load_dotenv()

from .db import SessionLocal, engine, Base
from . import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ecommerce Platform API",
    description="A simple ecommerce API with products, authentication, and shopping cart.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Load CORS origins from env or use defaults
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class Product(BaseModel):
    id: int | None = None
    name: str
    price: float
    description: str | None = None


class UserIn(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CartItemIn(BaseModel):
    product_id: int
    quantity: int = 1


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/products", response_model=List[Product])
def list_products(db=Depends(get_db)):
    items = db.query(models.Product).all()
    return [Product(id=i.id, name=i.name, price=i.price, description=i.description) for i in items]


@app.post("/products", response_model=Product)
def create_product(p: Product, db=Depends(get_db)):
    dbp = models.Product(name=p.name, price=p.price, description=p.description)
    db.add(dbp)
    db.commit()
    db.refresh(dbp)
    return Product(id=dbp.id, name=dbp.name, price=dbp.price, description=dbp.description)


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int, db=Depends(get_db)):
    prod = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(id=prod.id, name=prod.name, price=prod.price, description=prod.description)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user_by_username(db, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db, username: str, password: str):
    hashed = get_password_hash(password)
    user = models.User(username=username, hashed_password=hashed)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        return None
    return user


def authenticate_user(db, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Use integer timestamp for JWT exp claim (timezone-aware)
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user


@app.post("/auth/register", status_code=201)
def register(u: UserIn, db=Depends(get_db)):
    created = create_user(db, u.username, u.password)
    if not created:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"id": created.id, "username": created.username}


@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, p: Product, db=Depends(get_db), current_user=Depends(get_current_user)):
    prod = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    prod.name = p.name
    prod.price = p.price
    prod.description = p.description
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return Product(id=prod.id, name=prod.name, price=prod.price, description=prod.description)


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    prod = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(prod)
    db.commit()
    return {"status": "deleted"}


@app.get("/cart")
def get_cart(current_user=Depends(get_current_user), db=Depends(get_db)):
    items = (
        db.query(models.CartItem, models.Product)
        .join(models.Product, models.CartItem.product_id == models.Product.id)
        .filter(models.CartItem.user_id == current_user.id)
        .all()
    )
    result = []
    for cart_item, prod in items:
        result.append({"product_id": prod.id, "quantity": cart_item.quantity, "name": prod.name, "price": prod.price})
    return result


@app.post("/cart/add")
def add_to_cart(item: CartItemIn, current_user=Depends(get_current_user), db=Depends(get_db)):
    existing = (
        db.query(models.CartItem)
        .filter(models.CartItem.user_id == current_user.id, models.CartItem.product_id == item.product_id)
        .first()
    )
    if existing:
        existing.quantity = existing.quantity + item.quantity
        db.add(existing)
    else:
        ci = models.CartItem(user_id=current_user.id, product_id=item.product_id, quantity=item.quantity)
        db.add(ci)
    db.commit()
    return {"status": "ok"}


@app.post("/cart/remove")
def remove_from_cart(item: CartItemIn, current_user=Depends(get_current_user), db=Depends(get_db)):
    db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id, models.CartItem.product_id == item.product_id).delete()
    db.commit()
    return {"status": "ok"}
    conn = sqlite3.connect(DB)
