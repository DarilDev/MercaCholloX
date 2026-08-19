from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import CurrentUser
from app.models import UserProfile
from app.schemas import UserProfileIn, UserProfileOut

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=UserProfileOut)
def get_profile(user: CurrentUser, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if profile is None:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.put("", response_model=UserProfileOut)
def update_profile(payload: UserProfileIn, user: CurrentUser, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if profile is None:
        profile = UserProfile(user_id=user.id)
        db.add(profile)

    for field, value in payload.model_dump().items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile
