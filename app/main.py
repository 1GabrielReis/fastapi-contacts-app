from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from models import users, contacts
from utils import hash_password, verify_password
from database import database

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Rota para registrar um novo usuário
@app.post("/register/")
async def register_user(username: str, password: str, is_admin: bool = False):
    hashed_password = hash_password(password)
    query = users.insert().values(username=username, password=hashed_password, is_admin=is_admin)
    await database.execute(query)
    return {"message": "Usuário registrado com sucesso"}

# Função para autenticar o usuário
async def authenticate_user(username: str, password: str):
    query = select([users]).where(users.c.username == username)
    user = await database.fetch_one(query)
    if user and verify_password(password, user["password"]):
        return user
    raise HTTPException(status_code=400, detail="Credenciais inválidas")

# Rota para a página de login
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Rota para realizar login
@app.post("/login")
async def login(request: Request, username: str, password: str):
    user = await authenticate_user(username, password)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

# Rota para listar contatos do usuário autenticado
@app.get("/contacts/", response_class=HTMLResponse)
async def get_contacts(request: Request, user: dict = Depends(authenticate_user)):
    query = select([contacts]).where(contacts.c.owner_id == user["id"])
    user_contacts = await database.fetch_all(query)
    return templates.TemplateResponse("contacts.html", {"request": request, "contacts": user_contacts})

# Rota para criar um novo contato
@app.post("/contacts/")
async def create_contact(request: Request, name: str, email: str, user: dict = Depends(authenticate_user)):
    query = contacts.insert().values(name=name, email=email, owner_id=user["id"])
    await database.execute(query)
    return {"message": "Contato criado com sucesso"}
