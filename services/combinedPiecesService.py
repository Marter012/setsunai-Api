# services/combinedPiecesService.py
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from fastapi import HTTPException
from random import choices
import string
import math

from models.combinedPiece import (
    CombinedPiece,
    CombinedPieceUpdate,
    CombinedPieceModel
)

from services.comboVariantService import (
    save_combo_variants,
    delete_variants_by_combo
)

COLLECTION = "combinedPieces"
PIECES_COLLECTION = "pieces"


# -------------------------
# Helpers
# -------------------------

def generate_code(length: int = 6) -> str:
    return "".join(choices(string.ascii_uppercase + string.digits, k=length))


ROLL_SIZES = [4, 8]
TAKES = [3, 4, 5]

COMBO_SCHEMAS = [
    {"take": t, "perRoll": r}
    for r in ROLL_SIZES
    for t in TAKES
    if not (t == 3 and r == 8)
]

DISCOUNT_RULES = [
    {"minPieces": 8,  "discount": 0.00},
    {"minPieces": 16, "discount": 0.10},
    {"minPieces": 24, "discount": 0.15},
    {"minPieces": 30, "discount": 0.20},
]


def round_up_to_100(value: float) -> int:
    return int(math.ceil(value / 100) * 100)


def get_discount_for_pieces(total_pieces: int) -> float:
    discount = 0.0
    for rule in DISCOUNT_RULES:
        if total_pieces >= rule["minPieces"]:
            discount = rule["discount"]
    return discount


def calculate_prices(base_price: float, discount: float) -> tuple[int, int]:
    rounded_base = round_up_to_100(base_price)
    final_price = round_up_to_100(rounded_base * (1 - discount))
    return rounded_base, final_price


def generate_combo_variants(
    pieces_data: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    variants = []

    for schema in COMBO_SCHEMAS:
        take = schema["take"]
        per_roll = schema["perRoll"]
        price_key = f"price_{per_roll}p"

        available = [p for p in pieces_data if p.get(price_key) is not None]
        if len(available) < take:
            continue

        selected = available[:take]
        pieces_list = []
        raw_price = 0

        for piece in selected:
            price = piece[price_key]
            raw_price += price
            pieces_list.append({
                "pieceCode": piece["code"],
                "pieceName": piece["name"],
                "pieceCount": 1,
                "price": price
            })

        total_pieces = per_roll * take
        discount = get_discount_for_pieces(total_pieces)
        base_price, final_price = calculate_prices(raw_price, discount)

        variants.append({
            "take": take,
            "perRoll": per_roll,
            "pieces": pieces_list,
            "totalPieces": total_pieces,
            "basePrice": base_price,
            "finalPrice": final_price,
            "discounted": discount > 0,
            "discountPercent": int(discount * 100)
        })

    return variants


# -------------------------
# CRUD
# -------------------------

async def get_combined_pieces(db: AsyncIOMotorDatabase) -> List[CombinedPieceModel]:
    docs = await db[COLLECTION].find().to_list(length=None)

    if not docs:
        raise HTTPException(404, "No hay combinados disponibles")

    result = []
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        result.append(CombinedPieceModel(**doc))

    return result


async def add_combined_piece(
    data: CombinedPiece,
    db: AsyncIOMotorDatabase
) -> CombinedPieceModel:

    doc = data.model_dump()
    doc["state"] = True

    for _ in range(5):
        doc["code"] = generate_code()
        try:
            pieces_data = await db[PIECES_COLLECTION].find(
                {"code": {"$in": doc["typePieces"]}}
            ).to_list(length=None)

            variants = generate_combo_variants(pieces_data)

            result = await db[COLLECTION].insert_one(doc)
            doc["_id"] = str(result.inserted_id)

            await save_combo_variants(doc["code"], variants, db)

            return CombinedPieceModel(**doc)

        except DuplicateKeyError:
            continue

    raise HTTPException(500, "No se pudo generar un código único")


async def update_combined_piece(
    code: str,
    data: CombinedPieceUpdate,
    db: AsyncIOMotorDatabase
) -> Optional[CombinedPieceModel]:

    update_data = data.model_dump(exclude_unset=True)

    current = await db[COLLECTION].find_one({"code": code})
    if not current:
        return None

    if "name" in update_data:
        duplicate = await db[COLLECTION].find_one({
            "name": {"$regex": f"^{update_data['name']}$", "$options": "i"},
            "code": {"$ne": code}
        })
        if duplicate:
            raise HTTPException(
                400,
                "Ya existe otro combinado con ese nombre"
            )

    if "typePieces" in update_data:
        pieces_data = await db[PIECES_COLLECTION].find(
            {"code": {"$in": update_data["typePieces"]}}
        ).to_list(length=None)

        variants = generate_combo_variants(pieces_data)
        await delete_variants_by_combo(code, db)
        await save_combo_variants(code, variants, db)

    updated = await db[COLLECTION].find_one_and_update(
        {"code": code},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

    updated["_id"] = str(updated["_id"])
    return CombinedPieceModel(**updated)
