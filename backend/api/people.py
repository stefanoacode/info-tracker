from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.category import Category
from backend.models.person import Person

router = APIRouter()

class PersonCreate(BaseModel):
    name: str
    bio: str = ""
    category_name: str
    platform_handles: dict = {}

class PersonResponse(BaseModel):
    id: int
    name: str
    bio: str | None
    avatar_url: str | None
    category_name: str
    platform_handles: dict
    is_custom: bool
    model_config = {"from_attributes": True}

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    is_custom: bool
    sort_order: int
    model_config = {"from_attributes": True}

@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.sort_order).all()

@router.get("/people", response_model=list[PersonResponse])
def list_people(category: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Person)
    if category:
        query = query.join(Category).filter(Category.name == category)
    people = query.all()
    return [PersonResponse(id=p.id, name=p.name, bio=p.bio, avatar_url=p.avatar_url, category_name=p.category.name, platform_handles=p.platform_handles, is_custom=p.is_custom) for p in people]

@router.post("/people", response_model=PersonResponse, status_code=201)
def add_person(data: PersonCreate, db: Session = Depends(get_db)):
    category = db.query(Category).filter_by(name=data.category_name).first()
    if not category:
        raise HTTPException(status_code=404, detail=f"Category '{data.category_name}' not found")
    person = Person(name=data.name, bio=data.bio, category_id=category.id, platform_handles=data.platform_handles, is_custom=True)
    db.add(person)
    db.commit()
    db.refresh(person)
    return PersonResponse(id=person.id, name=person.name, bio=person.bio, avatar_url=person.avatar_url, category_name=category.name, platform_handles=person.platform_handles, is_custom=person.is_custom)

@router.delete("/people/{person_id}", status_code=204)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(Person).get(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    db.delete(person)
    db.commit()
