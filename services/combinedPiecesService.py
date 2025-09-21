from typing import Optional, List
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument
from dataBase.DBConfing import get_db
from models.combinedPiece import CombinedPiece, CombinedPieceUpdate, CombinedPieceModel
from motor.motor_asyncio import AsyncIOMotorDatabase
import  string
from random import choices

COLLECTION = "combinedPieces"


def generate_code(length: int = 6) -> str:
    return "".join(choices(string.ascii_uppercase + string.digits, k=length))


async def get_combined_pieces(db):
    docs = await db[COLLECTION].find().to_list(length=100)
    # Convertimos _id a string
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return [CombinedPieceModel(**doc) for doc in docs]

async def add_combined_piece(data: CombinedPiece, db):
    doc = data.model_dump()
    doc["code"] = generate_code()
    doc["state"] = True
    result = await db[COLLECTION].insert_one(doc)
    doc["_id"] = str(result.inserted_id)  # Convertimos _id a string
    return CombinedPieceModel(**doc)

async def update_combined_piece(code: str, data: CombinedPieceUpdate, db):
    existing = await db[COLLECTION].find_one({"code": code})
    if not existing:
        return None

    update_data = {k: v for k, v in data.model_dump(exclude_unset=True).items()}
    if not update_data:
        existing["_id"] = str(existing["_id"])
        return CombinedPieceModel(**existing)

    updated_doc = await db[COLLECTION].find_one_and_update(
        {"code": code},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )
    updated_doc["_id"] = str(updated_doc["_id"])
    return CombinedPieceModel(**updated_doc)