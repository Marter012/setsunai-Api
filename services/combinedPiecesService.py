from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from models.combinedPiece import CombinedPiece, CombinedPieceUpdate, CombinedPieceModel
import string
from random import choices

COLLECTION = "combinedPieces"
PIECES_COLLECTION = "pieces"

# ---------------- CODE GENERATOR ----------------
def generate_code(length: int = 6) -> str:
    """Genera un código aleatorio para un combinado"""
    return "".join(choices(string.ascii_uppercase + string.digits, k=length))


# ---------------- COMBO SCHEMAS (flexible y escalable) ----------------
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
    Sólo crea una variante si existen al menos `take` piezas que además tengan
    el precio correspondiente (price_{perRoll}p).
    """
    variants = []

    for schema in COMBO_SCHEMAS:
        take = schema.get("take")
        per_roll = schema.get("perRoll")

# Si alguno es None → saltar el schema
        if not isinstance(take, int) or not isinstance(per_roll, int):
            continue
        price_key = f"price_{per_roll}p"

        # Filtrar las piezas que SÍ tienen el price_key
        pieces_with_price = [p for p in pieces_data if price_key in p and p.get(price_key) is not None]

        # Sólo generar la variante si hay al menos `take` piezas con precio
        if len(pieces_with_price) < take:
            # saltar esta variante porque está incompleta
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
    """Obtiene todos los combinados con piecesData expandido (sin proteinsData)."""

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
        doc["_id"] = str(doc["_id"])

        # Convertir IDs internos
        for piece in doc.get("piecesData", []):
            if "_id" in piece:
                piece["_id"] = str(piece["_id"])

        combined_list.append(doc)

    return combined_list


# ---------------- AGREGAR NUEVO COMBO ----------------
async def add_combined_piece(data: CombinedPiece, db: AsyncIOMotorDatabase) -> CombinedPieceModel:
    """Agrega un combinado y genera sus variantes automáticamente."""
    
    doc = data.model_dump()
    doc["code"] = generate_code()
    doc["state"] = True

    # Obtener piezas para generar variantes
    pieces_data = await db[PIECES_COLLECTION].find(
        {"code": {"$in": doc["typePieces"]}}
    ).to_list(length=None)

    # Generar las variantes del combo
    doc["comboVariants"] = generate_combo_variants(pieces_data)

    # Insertar en BD
    result = await db[COLLECTION].insert_one(doc)
    doc["_id"] = str(result.inserted_id)

    return CombinedPieceModel(**doc)


# ---------------- ACTUALIZAR COMBO ----------------
async def update_combined_piece(code: str, data: CombinedPieceUpdate, db: AsyncIOMotorDatabase) -> Optional[CombinedPieceModel]:
    """Actualiza un combinado por código y regenera variantes si cambian las piezas."""

    existing = await db[COLLECTION].find_one({"code": code})
    if not existing:
        return None

    update_data = data.model_dump(exclude_unset=True)

    # Si cambian las piezas → regeneramos variantes
    if "typePieces" in update_data:
        pieces_data = await db[PIECES_COLLECTION].find(
            {"code": {"$in": update_data["typePieces"]}}
        ).to_list(length=None)

        update_data["comboVariants"] = generate_combo_variants(pieces_data)

    updated_doc = await db[COLLECTION].find_one_and_update(
        {"code": code},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

    updated_doc["_id"] = str(updated_doc["_id"])
    return CombinedPieceModel(**updated_doc)
