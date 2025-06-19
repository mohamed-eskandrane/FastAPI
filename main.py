from fastapi import FastAPI, Depends,HTTPException,Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from typing import List
from datetime import date
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.requests import Request
import os
from sqlalchemy import or_
from datetime import datetime
from database import SessionLocal, engine
from models import Base, PersonModel

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class Person(BaseModel):
    name: str
    gender: str
    birth_date: date
    nationality: str
    current_address: str
    notes: Optional[str] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/submit")
def submit_person(person: Person, db: Session = Depends(get_db)):
    person_db = PersonModel(
        name=person.name,
        gender=person.gender,
        birth_date=person.birth_date,
        nationality=person.nationality,
        current_address=person.current_address,
        notes=person.notes
    )
    db.add(person_db)
    db.commit()
    db.refresh(person_db)
    return {"message": "تم حفظ البيانات بنجاح", "id": person_db.id}


# حذف شخص بناءً على ID
@app.delete("/delete/{person_id}")
def delete_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(PersonModel).filter(PersonModel.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="الشخص غير موجود")
    db.delete(person)
    db.commit()
    return {"message": f"تم حذف الشخص بالرقم {person_id} بنجاح"}


# تعديل بيانات شخص باستخدام ID
@app.put("/update/{person_id}")
def update_person(person_id: int, updated_data: Person, db: Session = Depends(get_db)):
    person = db.query(PersonModel).filter(PersonModel.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="الشخص غير موجود")

    # تحديث الحقول
    person.name = updated_data.name
    person.gender = updated_data.gender
    person.birth_date = updated_data.birth_date
    person.nationality = updated_data.nationality
    person.current_address = updated_data.current_address
    person.notes = updated_data.notes

    db.commit()
    db.refresh(person)

    return {"message": f"تم تحديث بيانات الشخص بالرقم {person_id}", "updated": person}




# حذف عبر form (post)
@app.post("/delete/{person_id}")
def delete_person_html(person_id: int, db: Session = Depends(get_db)):
    person = db.query(PersonModel).filter(PersonModel.id == person_id).first()
    if person:
        db.delete(person)
        db.commit()
    return RedirectResponse(url="/people-table", status_code=303)

# عرض صفحة التعديل
@app.get("/edit/{person_id}", response_class=HTMLResponse)
def edit_person_form(person_id: int, request: Request, db: Session = Depends(get_db)):
    person = db.query(PersonModel).filter(PersonModel.id == person_id).first()
    if not person:
        return HTMLResponse(content="الشخص غير موجود", status_code=404)
    return templates.TemplateResponse("edit_person.html", {"request": request, "person": person})

# استلام التعديل
@app.post("/edit/{person_id}")
def update_person_form(
    person_id: int,
    name: str = Form(...),
    gender: str = Form(...),
    birth_date: str = Form(...),
    nationality: str = Form(...),
    current_address: str = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db)
):
    person = db.query(PersonModel).filter(PersonModel.id == person_id).first()
    if not person:
        return HTMLResponse(content="الشخص غير موجود", status_code=404)

    person.name = name
    person.gender = gender
    person.birth_date = birth_date
    person.nationality = nationality
    person.current_address = current_address
    person.notes = notes

    db.commit()
    return RedirectResponse(url="/people-table", status_code=303)

# عرض صفحة إضافة شخص
@app.get("/add", response_class=HTMLResponse)
def add_person_form(request: Request):
    return templates.TemplateResponse("add_person.html", {"request": request})

# استلام البيانات من نموذج الإضافة
@app.post("/add")
def add_person(
    name: str = Form(...),
    gender: str = Form(...),
    birth_date: str = Form(...),
    nationality: str = Form(...),
    current_address: str = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db)
):
    try:
        birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="صيغة التاريخ غير صحيحة")

    person = PersonModel(
        name=name,
        gender=gender,
        birth_date=birth_date,
        nationality=nationality,
        current_address=current_address,
        notes=notes
    )
    db.add(person)
    db.commit()
    return RedirectResponse(url="/people-table", status_code=303)

@app.get("/people-table", response_class=HTMLResponse)
def show_people_table(request: Request, search: str = "", db: Session = Depends(get_db)):
    if search:
        people = db.query(PersonModel).filter(
            or_(
                PersonModel.name.ilike(f"%{search}%"),
                PersonModel.gender.ilike(f"%{search}%"),
                PersonModel.notes.ilike(f"%{search}%"),
                PersonModel.nationality.ilike(f"%{search}%"),
                PersonModel.current_address.ilike(f"%{search}%")
            )
        ).all()
    else:
        people = db.query(PersonModel).all()

    return templates.TemplateResponse("people.html", {
        "request": request,
        "people": people,
        "search": search
    })

@app.get("/", response_class=RedirectResponse)
def root():
    return RedirectResponse(url="/people-table")

