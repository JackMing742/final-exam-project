from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import List
import sqlite3

app = FastAPI()


# ----------------------------------------------------
# Pydantic models
class PostCreate(BaseModel):
    text: str
    author: str
    tags: List[str]


class PostResponse(PostCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------


# 連線資料庫
def get_db_connection():
    conn = sqlite3.connect("quotes.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    return conn, cursor


# ----------------------------------------------------
# api根目錄訊息
@app.get("/", response_model=dict, status_code=200)
def root():
    return {"message": "quotes system"}


# ----------------------------------------------------
# CRUD 操作
@app.get("/quotes", response_model=List[PostResponse], status_code=200)
def get_quotes():
    conn, cursor = get_db_connection()
    try:
        cursor.execute("SELECT * FROM quotes")
        rows = cursor.fetchall()
        results = []
        for row in rows:
            data = dict(row)
            if data["tags"]:
                data["tags"] = [t.strip() for t in data["tags"].split(",")]
            else:
                data["tags"] = []

            results.append(data)
        return results
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="伺服器內部錯誤")
    finally:
        conn.close()


# ----------------------------------------------------
@app.post("/quotes", response_model=PostResponse, status_code=200)
def add_quote(post: PostCreate):
    conn, cursor = get_db_connection()
    try:
        tags_str = ", ".join(post.tags)
        cursor.execute(
            "INSERT INTO quotes (text, author, tags) VALUES (?, ?, ?)",
            (post.text, post.author, tags_str),
        )
        conn.commit()
        post_id = cursor.lastrowid
        return PostResponse(id=post_id, **post.model_dump())
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="伺服器內部錯誤")
    finally:
        conn.close()


@app.put("/quotes/{quote_id}", response_model=PostResponse, status_code=200)
def update_quote(quote_id: int, post: PostCreate):
    conn, cursor = get_db_connection()
    try:
        tags_str = ", ".join(post.tags)
        cursor.execute(
            "UPDATE quotes SET text = ?, author = ?, tags = ? WHERE id = ?",
            (post.text, post.author, tags_str, quote_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="找不到引用")
        return PostResponse(id=quote_id, **post.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail="伺服器內部錯誤")
    finally:
        conn.close()


@app.delete("/quotes/{quote_id}", response_model=dict, status_code=200)
def delete_quote(quote_id: int):
    conn, cursor = get_db_connection()
    try:
        cursor.execute("DELETE FROM quotes WHERE id = ?", (quote_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="找不到名言")
        return {"message": "名言已刪除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="伺服器內部錯誤")
    finally:
        conn.close()
