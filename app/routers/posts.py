
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import func
from fastapi import Depends, Response, status, HTTPException, APIRouter
from typing import List, Optional

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


@router.get("/", response_model=List[schemas.PostOut])
# def get_posts():
def get_posts(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    """ Return all records from the posts table """
    # cursor.execute("""SELECT * FROM posts """)
    # posts = cursor.fetchall()
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts

# @router.get("/ormposts")
# def get_orm_posts(db: Session = Depends(get_db)):
#     """ Return all records from the posts table via ORM (test) """
#     posts = db.query(models.Post).all()
#     return posts

@router.get("/{id}", response_model=schemas.PostOut)
# def get_post(id: int, response: Response):
def get_post(id: int, response: Response, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    """ Return a single record from the posts table """
    # cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id),))
    # post = cursor.fetchone()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"ID {id} was not found")
    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
# def create_posts(payload: Post):
def create_post(payload: schemas.PostCreate, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    """ Insert a single record into the posts table """
    # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES(%s, %s, %s) RETURNING * """,
    #     (payload.title, payload.content, payload.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    # new_post = models.Post(title=payload.title, content=payload.content, published=payload.published)
    new_post = models.Post(owner_id=current_user.id, **payload.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.put("/{id}", status_code=status.HTTP_201_CREATED)
# def update_posts(id: int, payload: Post):
def update_post(id: int, payload: schemas.PostCreate, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    """ Update a single record from the posts table """
    # cursor.execute("""UPDATE posts SET (title, content, published) = (%s, %s, %s) WHERE id = %s RETURNING * """, 
    #     (payload.title, payload.content, payload.published, str(id),))
    # post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)    
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"ID {id} was not found")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = f"Not authorised to perform requested action")
    post_query.update(payload.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_post(id: int, response: Response):
def delete_post(id: int, response: Response, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    """ Remove a single record from the posts table """
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNIKNG * """, (str(id),))
    # post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)    
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"ID {id} was not found")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = f"Not authorised to perform requested action")
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
