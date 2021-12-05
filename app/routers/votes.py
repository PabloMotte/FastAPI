from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, Response, status, HTTPException, APIRouter

router = APIRouter(
    prefix="/vote",
    tags=['Vote']
)

@router.post("/", status_code=status.HTTP_201_CREATED) 
def create_vote(payload: schemas.Vote, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    """ Insert or remove a single record in the votes table """

    found_post = db.query(models.Post).filter(models.Post.id == payload.post).first()
    if not found_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post {payload.post} does not exist")

    vote_query = db.query(models.Vote).filter(models.Vote.post_id == payload.post, models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()
    if (payload.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user {current_user.id} has already voted for post {payload.post}")
        new_vote = models.Vote(user_id = current_user.id, post_id = payload.post)
        db.add(new_vote)
        db.commit()
        return {"message": "Vote added"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user {current_user.id} has not voted for post {payload.post}")
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "Vote removed"}
        
    return {"message": "something went wrong"}


