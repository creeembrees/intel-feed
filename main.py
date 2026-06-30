from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from typing import List, Optional
from fastapi.params import Body
from random import randint
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

class post(BaseModel):
    topic: List[str]
    vibe: str = "casual"
    published: bool = True
    ratings: Optional[int] = None

my_feed = [{"topic": ["sports", "politics"], "vibe": "casual", "id": "1", "ratings": 5}, 
           {"topic": ["technology", "science"], "vibe": "formal", "id": "2", "ratings": 4}]

#posts: List[post] = []

def find_post(id):
    for post in my_feed:
        if post["id"] == id:
            return post

@app.get("/")
def root():  
    return {"message": "Welcome to the API Testing !!"}

@app.get("/feeds")
def get_posts():
    return {"data": my_feed}

@app.post("/feed")
def create_post(post: post):
    post_dict = post.dict()
    post_dict["id"] = str(randint(0, 10000000))  
    my_feed.append(post_dict)
    return {"data": post_dict}

@app.get("/feed/latest")
def get_latest_post():
    post=my_feed[len(my_feed)-1]
    return {"data": post}

@app.get("/feed/{id}")
def get_post(id: int, response: Response):
    post = find_post(id)
    print(post)
    if not post:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Post not found"}
    return {"data": post}

@app.get("/feed/latest")
def get_latest_post():
    post=my_feed[len(my_feed)-1]
    return {"data": post}