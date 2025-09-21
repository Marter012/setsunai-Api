# dataBase/DBConfig.py
import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "SETSUNAI")

client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None

async def connect_to_db() -> AsyncIOMotorDatabase:
    """
    Conecta a la base de datos y retorna la instancia de DB.
    """
    global client, db
    if client is None:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        print(f"✅ Conectado a MongoDB: {DB_NAME}")
    assert db is not None  # Pylance entiende que db no puede ser None aquí
    return db

async def close_db():
    """
    Cierra la conexión a MongoDB.
    """
    global client
    if client:
        client.close()
        client = None
        print("❌ Conexión a MongoDB cerrada")

# Dependencia para FastAPI
async def get_db() -> AsyncIOMotorDatabase:
    """
    Devuelve la base de datos, levantando un error si no está inicializada.
    """
    if db is None:
        raise RuntimeError("DB no inicializada. Llama a connect_to_db primero.")
    return db
