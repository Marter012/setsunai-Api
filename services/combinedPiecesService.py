# services/combinedPiecesService.py
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from models.combinedPiece import CombinedPiece, CombinedPieceUpdate, CombinedPieceModel
from services.comboVariantService import save_combo_variants, delete_variants_by_combo
import string
from random import choices

COLLECTION = "combinedPieces"
PIECES_COLLECTION = "pieces"
COMBO_VARIANTS_COLLECTION = "comboVariants"  # referencia clara, aunque usamos servicio


# ---------------- CODE GENERATOR ----------------
def generate_code(length: int = 6) -> str:
    """Genera un código aleatorio para un combinado"""
    return "".join(choices(string.ascii_uppercase + string.digits, k=length))


# ---------------- COMBO SCHEMAS ----------------
COMBO_SCHEMAS = [
    {"take": 3, "perRoll": 4},
    {"take": 4, "perRoll": 4},
    {"take": 5, "perRoll": 4},
    {"take": 4, "perRoll": 8},
    {"take": 5, "perRoll": 8}
]


# ---------------- GENERADOR DE VARIANTES ----------------
def generate_combo_variants(pieces_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Genera variantes a partir de COMBO_SCHEMAS.
    Sólo crea una variante si existen al menos `take` piezas que tengan price_{perRoll}p.
    """
    variants = []

    for schema in COMBO_SCHEMAS:
        take = schema.get("take")
        per_roll = schema.get("perRoll")

        if not isinstance(take, int) or not isinstance(per_roll, int):
            continue

        price_key = f"price_{per_roll}p"

        # piezas que pueden entrar en este esquema
        pieces_with_price = [p for p in pieces_data if p.get(price_key) is not None]

        if len(pieces_with_price) < take:
            continue

        selected = pieces_with_price[:take]
        pieces_list = []
        total_price = 0

        for piece in selected:
            price = piece.get(price_key, 0)
            pieces_list.append({
                "pieceCode": piece.get("code"),
                "pieceName": piece.get("name"),
                "pieceCount": take,
                "price": price
            })
            total_price += price

        variants.append({
            "take": take,
            "perRoll": per_roll,
            "pieces": pieces_list,
            "totalPieces": per_roll * len(selected),
            "finalPrice": total_price
        })

    return variants


# ---------------- GET TODOS LOS COMBOS ----------------
async def get_combined_pieces(db: AsyncIOMotorDatabase) -> List[dict]:
    """Obtiene todos los combinados con piecesData expandido."""
    pipeline = [
        {
            "$lookup": {
                "from": PIECES_COLLECTION,
                "localField": "typePieces",
                "foreignField": "code",
                "as": "piecesData"
            }
        }
    ]

    docs = await db[COLLECTION].aggregate(pipeline).to_list(length=None)
    combined_list = []

    for doc in docs:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])

        for piece in doc.get("piecesData", []):
            if "_id" in piece:
                piece["_id"] = str(piece["_id"])

        doc.pop("comboVariants", None)

        combined_list.append(doc)

    return combined_list


# ---------------- AGREGAR NUEVO COMBO ----------------
async def add_combined_piece(data: CombinedPiece, db: AsyncIOMotorDatabase) -> CombinedPieceModel:
    """
    Agrega un combinado (solo doc base) y genera sus variantes automáticamente 
    guardándolas en la colección comboVariants.
    """
    doc = data.model_dump()
    doc["code"] = generate_code()
    doc["state"] = True

    # obtener todas las piezas para generar variantes
    pieces_data = await db[PIECES_COLLECTION].find(
        {"code": {"$in": doc["typePieces"]}}
    ).to_list(length=None)

    variants = generate_combo_variants(pieces_data)

    # guardar doc base
    result = await db[COLLECTION].insert_one(doc)
    doc["_id"] = str(result.inserted_id)

    # guardar variantes
    await save_combo_variants(doc["code"], variants, db)

    return CombinedPieceModel(**doc)


# ---------------- ACTUALIZAR COMBO ----------------
async def update_combined_piece(code: str, data: CombinedPieceUpdate, db: AsyncIOMotorDatabase) -> Optional[CombinedPieceModel]:
    """
    Actualiza un combinado por código y, si cambian typePieces, regenera variantes.
    """
    existing = await db[COLLECTION].find_one({"code": code})
    if not existing:
        return None

    update_data = data.model_dump(exclude_unset=True)

    # si cambian las piezas, regeneramos variantes
    if "typePieces" in update_data:
        pieces_data = await db[PIECES_COLLECTION].find(
            {"code": {"$in": update_data["typePieces"]}}
        ).to_list(length=None)

        new_variants = generate_combo_variants(pieces_data)

        await delete_variants_by_combo(code, db)
        await save_combo_variants(code, new_variants, db)

    updated_doc = await db[COLLECTION].find_one_and_update(
        {"code": code},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

    if updated_doc:
        updated_doc["_id"] = str(updated_doc["_id"])
        updated_doc.pop("comboVariants", None)
        return CombinedPieceModel(**updated_doc)

    return None
