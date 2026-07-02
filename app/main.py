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

class Feed(BaseModel):
    topic: List[str]
    vibe: str = "casual"
    ratings: Optional[int] = None

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

@app.get("/")
def root():  
    return {"message": "Welcome to the API Testing !!"}

@app.get("/feeds")
def get_posts():
    return {"data": my_feed}

@app.post("/feed")
def create_post(post: Feed):
    post_dict = post.dict()
    post_dict["id"] = randint(0, 10000000) 
    post_dict["summary"]="Ai summary will go here"
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

