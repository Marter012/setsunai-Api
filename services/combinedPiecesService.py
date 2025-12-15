from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
import string
from random import choices
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


# ---------------- CODE GENERATOR ----------------
def generate_code(length: int = 6) -> str:
    """Genera un código aleatorio para un combinado"""
    return "".join(choices(string.ascii_uppercase + string.digits, k=length))


# ---------------- COMBO SCHEMAS ----------------
COMBO_SCHEMAS = [
    {"take": 3, "perRoll": 4},
    {"take": 4, "perRoll": 4},
    {"take": 4, "perRoll": 8},
]


# ---------------- DISCOUNT RULES ----------------
DISCOUNT_RULES = [
    {"minPieces": 8,  "discount": 0.00},
    {"minPieces": 16, "discount": 0.10},
    {"minPieces": 24, "discount": 0.15},
    {"minPieces": 30, "discount": 0.20},
]


# ---------------- PRICE HELPERS ----------------
def round_up_to_100(value: float) -> int:
    """
    Redondea al múltiplo de 200 inmediato superior.
    """
    return int(math.ceil(value / 100) * 100)


def get_discount_for_pieces(total_pieces: int) -> float:
    """Devuelve el mayor descuento aplicable según cantidad de piezas"""
    applied_discount = 0.0
    for rule in DISCOUNT_RULES:
        if total_pieces >= rule["minPieces"]:
            applied_discount = rule["discount"]
    return applied_discount


def calculate_prices(base_price: float, discount: float) -> tuple[int, int]:
    """
    Calcula basePrice y finalPrice redondeados de 200 en 200.
    """
    rounded_base = round_up_to_100(base_price)
    discounted_price = rounded_base * (1 - discount)
    final_price = round_up_to_100(discounted_price)

    return rounded_base, final_price


# ---------------- VARIANT GENERATOR ----------------
def generate_combo_variants(
    pieces_data: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    variants = []

    for schema in COMBO_SCHEMAS:
        take = schema["take"]
        per_roll = schema["perRoll"]

        price_key = f"price_{per_roll}p"

        pieces_with_price = [
            p for p in pieces_data if p.get(price_key) is not None
        ]

        if len(pieces_with_price) < take:
            continue

        selected = pieces_with_price[:take]
        pieces_list = []
        raw_base_price = 0

        for piece in selected:
            price = piece.get(price_key, 0)
            raw_base_price += price

            pieces_list.append({
                "pieceCode": piece.get("code"),
                "pieceName": piece.get("name"),
                "pieceCount": 1,
                "price": price
            })

        total_pieces = per_roll * len(selected)
        discount = get_discount_for_pieces(total_pieces)

        base_price, final_price = calculate_prices(
            raw_base_price,
            discount
        )

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


# ---------------- GET ALL COMBOS ----------------
async def get_combined_pieces(db: AsyncIOMotorDatabase) -> List[dict]:
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
    result = []

    for doc in docs:
        doc["_id"] = str(doc["_id"])
        doc.pop("comboVariants", None)

        for piece in doc.get("piecesData", []):
            piece["_id"] = str(piece["_id"])

        result.append(doc)

    return result


# ---------------- ADD COMBO ----------------
async def add_combined_piece(
    data: CombinedPiece,
    db: AsyncIOMotorDatabase
) -> CombinedPieceModel:

    doc = data.model_dump()
    doc["code"] = generate_code()
    doc["state"] = True

    pieces_data = await db[PIECES_COLLECTION].find(
        {"code": {"$in": doc["typePieces"]}}
    ).to_list(length=None)

    variants = generate_combo_variants(pieces_data)

    result = await db[COLLECTION].insert_one(doc)
    doc["_id"] = str(result.inserted_id)

    await save_combo_variants(doc["code"], variants, db)

    return CombinedPieceModel(**doc)


# ---------------- UPDATE COMBO ----------------
async def update_combined_piece(
    code: str,
    data: CombinedPieceUpdate,
    db: AsyncIOMotorDatabase
) -> Optional[CombinedPieceModel]:

    existing = await db[COLLECTION].find_one({"code": code})
    if not existing:
        return None

    update_data = data.model_dump(exclude_unset=True)

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

    updated_doc["_id"] = str(updated_doc["_id"])
    updated_doc.pop("comboVariants", None)

    return CombinedPieceModel(**updated_doc)
