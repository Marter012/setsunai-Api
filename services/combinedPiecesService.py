from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from models.combinedPiece import CombinedPiece, CombinedPieceUpdate, CombinedPieceModel
import string
from random import choices

COLLECTION = "combinedPieces"

def generate_code(length: int = 6) -> str:
    """Genera un código aleatorio para un combinado"""
    return "".join(choices(string.ascii_uppercase + string.digits, k=length))


async def get_combined_pieces(db: AsyncIOMotorDatabase) -> List[CombinedPieceModel]:
    """Obtiene todos los combinados de piezas"""
    docs = await db[COLLECTION].find().to_list(length=100)
    combined_list = []

    for doc in docs:
        doc["_id"] = str(doc["_id"])
        combined_list.append(CombinedPieceModel(
            code=doc.get("code", ""),
            name=doc.get("name", ""),
            img=doc.get("img", ""),
            typePieces=doc.get("typePieces", ""),
            price=doc.get("price", ""),
            state=doc.get("state", True),
            _id=doc.get("_id")
        ))

    return combined_list


async def add_combined_piece(data: CombinedPiece, db: AsyncIOMotorDatabase) -> CombinedPieceModel:
    """Agrega un nuevo combinado de piezas"""
    doc = data.model_dump()
    doc["code"] = generate_code()
    doc["state"] = True
    result = await db[COLLECTION].insert_one(doc)
    doc["_id"] = str(result.inserted_id)

    return CombinedPieceModel(
        code=doc.get("code", ""),
        name=doc.get("name", ""),
        img=doc.get("img", ""),
        typePieces=doc.get("typePieces", ""),
        price=doc.get("price", ""),
        state=doc.get("state", True),
        _id=doc.get("_id")
    )


async def update_combined_piece(code: str, data: CombinedPieceUpdate, db: AsyncIOMotorDatabase) -> Optional[CombinedPieceModel]:
    """Actualiza un combinado existente por su código"""
    existing = await db[COLLECTION].find_one({"code": code})
    if not existing:
        return None

    update_data = {k: v for k, v in data.model_dump(exclude_unset=True).items()}
    if not update_data:
        # No hay cambios, devolvemos el existente
        existing["_id"] = str(existing["_id"])
        return CombinedPieceModel(
            code=existing.get("code", ""),
            name=existing.get("name", ""),
            img=existing.get("img", ""),
            typePieces=existing.get("typePieces", ""),
            price=existing.get("price", ""),
            state=existing.get("state", True),
            _id=existing.get("_id")
        )

    updated_doc = await db[COLLECTION].find_one_and_update(
        {"code": code},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )
    updated_doc["_id"] = str(updated_doc["_id"])
    return CombinedPieceModel(
        code=updated_doc.get("code", ""),
        name=updated_doc.get("name", ""),
        img=updated_doc.get("img", ""),
        typePieces=updated_doc.get("typePieces", ""),
        price=updated_doc.get("price", ""),
        state=updated_doc.get("state", True),
        _id=updated_doc.get("_id")
    )
