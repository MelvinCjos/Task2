from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, User, Profile
from pydantic import BaseModel, EmailStr
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Melvin%40123@localhost/task_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register/")
async def register_user(full_name: str = Form(...), email: str = Form(...), 
                        password: str = Form(...), phone: str = Form(...),
                        profile_picture: UploadFile = File(...), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(email=email, password=password, full_name=full_name, phone=phone)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Handle profile picture here (save the file and store its path in the database)

    return {"user_id": new_user.id, "message": "User registered successfully"}



# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/user/{user_id}", response_class=HTMLResponse)
async def get_user_details(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = {
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "profile_picture": user.profile.profile_picture if user.profile else None
    }
    return templates.TemplateResponse("user_details.html", {"request": Request, "user": user_data})
