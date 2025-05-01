from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from models.item import Base, Item

# データベース接続設定
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/fastapi_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# テーブル作成
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI with PostgreSQL")

# DBセッションの依存関係
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ルート
@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI with PostgreSQL"}


# アイテム一覧取得
@app.get("/items/")
def read_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return items


# アイテム作成
@app.post("/items/")
def create_item(name: str, description: str = None, db: Session = Depends(get_db)):
    item = Item(name=name, description=description)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# 特定のアイテム取得
@app.get("/items/{item_id}")
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item