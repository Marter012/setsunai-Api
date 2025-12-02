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


# ---------------- GET TODOS LOS COMBOS CON PIEZAS Y PROTEÍNAS EXPANDIDAS ----------------
async def get_combined_pieces(db: AsyncIOMotorDatabase) -> List[dict]:
    """Obtiene todos los combinados con piecesData y proteinsData"""

    pipeline = [
        {
            "$lookup": {
                "from": "pieces",
                "localField": "typePieces",
                "foreignField": "code",
                "as": "piecesData"
            }
        },
        {
            "$lookup": {
                "from": "proteins",
                "localField": "proteins",
                "foreignField": "code",
                "as": "proteinsData"
            }
        }
    ]

    docs = await db[COLLECTION].aggregate(pipeline).to_list(length=None)
    combined_list = []

    for doc in docs:
        # Convertir _id del combo a string
        doc["_id"] = str(doc["_id"])
        
        # Convertir _id dentro de piecesData
        for piece in doc.get("piecesData", []):
            if "_id" in piece:
                piece["_id"] = str(piece["_id"])

        # Convertir _id dentro de proteinsData
        for prot in doc.get("proteinsData", []):
            if "_id" in prot:
                prot["_id"] = str(prot["_id"])

        combined_list.append({
            "_id": doc["_id"],
            "code": doc.get("code", ""),
            "name": doc.get("name", ""),
            "img": doc.get("img", ""),
            "typePieces": doc.get("typePieces", []),
            "proteins": doc.get("proteins", []),
            "description": doc.get("description", ""),
            "state": doc.get("state", True),
            "piecesData": doc.get("piecesData", []),
            "proteinsData": doc.get("proteinsData", [])
        })

    return combined_list


# ---------------- AGREGAR NUEVO COMBO ----------------
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
        typePieces=doc.get("typePieces", []),
        proteins=doc.get("proteins", []),
        description=doc.get("description", ""),
        state=doc.get("state", True),
        _id=doc.get("_id")
    )


# ---------------- ACTUALIZAR COMBO EXISTENTE ----------------
async def update_combined_piece(code: str, data: CombinedPieceUpdate, db: AsyncIOMotorDatabase) -> Optional[CombinedPieceModel]:
    """Actualiza un combinado existente por su código"""
    existing = await db[COLLECTION].find_one({"code": code})
    if not existing:
        return None

    update_data = data.model_dump(exclude_unset=True)

    # ❌ Nunca permitir modificar estos campos manualmente
    update_data.pop("piecesData", None)
    update_data.pop("proteinsData", None)

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
