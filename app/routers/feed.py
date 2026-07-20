from fastapi import FastAPI, Response, status, Request, Depends, HTTPException, APIRouter
from typing import List
from sqlalchemy.orm import Session
from .. import models, schemas
from ..schemas import Feed, FeedCreate, FeedBase
from ..databases import engine, SessionLocal, get_db

router = APIRouter()

@router.get("/feeds", response_model=List[schemas.FeedBase])
def get_sqlalchemy(db: Session = Depends(get_db)):
    feeds = db.query(models.Feed).all()
    print(feeds)
    return feeds

@router.post("/feed", status_code=status.HTTP_201_CREATED, response_model=schemas.FeedBase)
def create_post(feed: FeedCreate,db: Session = Depends(get_db)):
    '''cursor.execute("INSERT INTO feed (topics, vibe, max_articles) VALUES (%s, %s, %s) RETURNING *", 
                   (feed.topics, feed.vibe, feed.max_articles))
    new_post = cursor.fetchone()
    conn.commit()'''
    new_feed = models.Feed(topics=feed.topics, vibe=feed.vibe, max_articles=feed.max_articles)
    db.add(new_feed)
    db.commit()
    db.refresh(new_feed)
    return new_feed

@router.get("/feed/latest")
def get_latest_post(db: Session = Depends(get_db)):
    latest_feed = db.query(models.Feed).order_by(models.Feed.id.desc()).first()
    return latest_feed

@router.get("/feed/{id}", response_model=schemas.FeedBase)
def get_post(id: int, response: Response, db: Session = Depends(get_db)):
    '''cursor.execute("SELECT * FROM feed WHERE id = %s", (id,))
    post = cursor.fetchone()
    if not post:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Post not found"}'''
    post = db.query(models.Feed).filter(models.Feed.id == id).all()
    if not post:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Post not found"}
    return post

@router.delete("/feed/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, response: Response, db: Session = Depends(get_db)):
    '''cursor.execute("SELECT * FROM feed WHERE id = %s", (id,))
    deleted_post = cursor.fetchone()
    if not deleted_post:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Post not found"}
    cursor.execute("DELETE FROM feed WHERE id = %s", (id,))
    conn.commit()'''
    deleted_feed = db.query(models.Feed).filter(models.Feed.id == id).first()
    
    if deleted_feed is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Post with id {id} not found"
        )    
    db.delete(deleted_feed)
    db.commit()
    return None

@router.put("/feed/{id}", response_model=schemas.FeedBase)
def update_post(id: int, updated_post: FeedCreate, response: Response, db: Session = Depends(get_db)):   
    '''cursor.execute("update feed set topics = %s, vibe = %s, max_articles = %s where id = %s RETURNING *", 
                   (updated_post.topics, updated_post.vibe, updated_post.max_articles, str(id)))  
    updated_post = cursor.fetchone()
    conn.commit()'''
    post_query = db.query(models.Feed).filter(models.Feed.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Post with id {id} not found"
        )
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()   
    
from fastapi import HTTPException
