import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey, MetaData
from database import DATABASE_URL

metadata = MetaData()

# Tabela de usuários
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True),
    Column("password", String),
    Column("is_admin", Boolean, default=False)
)

# Tabela de contatos
contacts = Table(
    "contacts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("email", String),
    Column("owner_id", Integer, ForeignKey("users.id"))
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)
