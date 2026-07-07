from fastapi import FastAPI, Response, status, Request, Depends
from pydantic import BaseModel
from typing import List, Optional
from fastapi.params import Body
from random import randint
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
import time
from sqlalchemy.orm import Session
from . import models
from .databases import engine, SessionLocal

load_dotenv()

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal() 
    try:
        yield db
    finally:
        db.close()

class Feed(BaseModel):
    topics: List[str]          
    vibe: str = "casual"       
    max_articles: Optional[int] = None  

while True:

    try:
        conn = psycopg2.connect(host=os.getenv("DB_HOST"), database=os.getenv("DB_NAME"), user=os.getenv("DB_USER"),
                                password=os.getenv("DB_PASSWORD"),port=os.getenv("DB_PORT"), cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was succesfull!")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        time.sleep(2)


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

@app.get("/sqlalchemy")
def get_sqlalchemy(db: Session = Depends(get_db)):
    return {"message": "SQLAlchemy is working!"}

@app.get("/feeds")
def get_posts():
    cursor.execute("SELECT * FROM feed")
    feed = cursor.fetchall()
    print(feed)
    return {"data": feed}

@app.post("/feed", status_code=status.HTTP_201_CREATED)
def create_post(feed: Feed):
    cursor.execute("INSERT INTO feed (topics, vibe, max_articles) VALUES (%s, %s, %s) RETURNING *", 
                   (feed.topics, feed.vibe, feed.max_articles))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}

@app.get("/feed/latest")
def get_latest_post():
    cursor.execute("SELECT * FROM feed ORDER BY id DESC LIMIT 1")
    latest_post = cursor.fetchone()
    return {"data": latest_post}

@app.get("/feed/{id}")
def get_post(id: int, response: Response):
    cursor.execute("SELECT * FROM feed WHERE id = %s", (id,))
    post = cursor.fetchone()
    if not post:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Post not found"}
    return {"data": post}

@app.delete("/feed/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, response: Response):
    cursor.execute("SELECT * FROM feed WHERE id = %s", (id,))
    deleted_post = cursor.fetchone()
    if not deleted_post:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Post not found"}
    cursor.execute("DELETE FROM feed WHERE id = %s", (id,))
    conn.commit()
    return {"message": "Post deleted successfully"}

@app.put("/feed/{id}")
def update_post(id: int, updated_post: Feed, response: Response):   
    cursor.execute("update feed set topics = %s, vibe = %s, max_articles = %s where id = %s RETURNING *", 
                   (updated_post.topics, updated_post.vibe, updated_post.max_articles, str(id)))  
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Post not found"}
    return {"data": updated_post}    
