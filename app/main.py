from fastapi import FastAPI, Response, status, Request
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

load_dotenv()

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

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


my_feed = [{"topic": ["sports", "politics"], "vibe": "casual", "id": 1, "ratings": 5}, 
           {"topic": ["technology", "science"], "vibe": "formal", "id": 2, "ratings": 4}]

#posts: List[Feed] = []

def find_post(id):
    for post in my_feed:
        if post["id"] == id:
            return post
        
def find_post_index(id):
    for index, post in enumerate(my_feed):
        if post["id"] == id:
            return index

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

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
    post = cursor.fetchone()
    return {"data": post}

@app.get("/feed/{id}")
def get_post(id: int, response: Response):
    post = find_post(id)
    print(post)
    if not post:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Post not found"}
    return {"data": post}

@app.delete("/feed/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, response: Response):
    post = find_post(id)
    if not post:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Post not found"}
    my_feed.pop(find_post_index(id))
    return {"message": "Post deleted successfully"}

@app.put("/feed/{id}")
def update_post(id: int, updated_post: Feed, response: Response):   
    post = find_post(id)
    if not post:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Post not found"}
    post_index = find_post_index(id)
    updated_post_dict = updated_post.dict()
    updated_post_dict["id"] = id
    my_feed[post_index] = updated_post_dict
    return {"data": updated_post_dict}      

