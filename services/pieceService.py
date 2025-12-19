# services/pieceService.py
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from random import choices
import string
import math
from pymongo import ReturnDocument
from fastapi import HTTPException

from models.piece import Piece, PieceUpdate, PieceModel
from services.combinedPiecesService import generate_combo_variants
from services.comboVariantService import save_combo_variants, delete_variants_by_combo


# -------------------------
# Helpers
# -------------------------

def generate_code(length: int = 6) -> str:
    return "".join(choices(string.ascii_uppercase + string.digits, k=length))


def round_200(value: float) -> int:
    return int(math.ceil(value / 200) * 200)


def generate_prices(cost: float) -> dict:
    unit = cost / 8
    return {
        "price_3p": round_200(unit * 3 * 3.1),
        "price_4p": round_200(unit * 4 * 3.1),
        "price_5p": round_200(unit * 5 * 3.1),
        "price_8p": round_200(unit * 8 * 3),
        "price_16p": round_200(unit * 16 * 2.5),
    }


# -------------------------
# CRUD
# -------------------------

async def get_pieces(db: AsyncIOMotorDatabase):
    pieces = await db["pieces"].find().to_list(length=None)

    if not pieces:
        raise HTTPException(404, "No hay piezas disponibles")

    return [
        PieceModel(**{**p, "_id": str(p["_id"])})
        for p in pieces
    ]


async def add_piece(piece: Piece, db: AsyncIOMotorDatabase) -> PieceModel:
    doc = piece.model_dump()
    doc.update(generate_prices(doc["costRoll"]))
    doc["state"] = True

    for _ in range(5):
        doc["code"] = generate_code()
        try:
            result = await db["pieces"].insert_one(doc)
            doc["_id"] = str(result.inserted_id)
            return PieceModel(**doc)
        except Exception:
            continue

    raise HTTPException(500, "No se pudo generar un código único")


async def update_piece(
    code: str,
    piece_update: PieceUpdate,
    db: AsyncIOMotorDatabase
) -> Optional[PieceModel]:

    update_data = piece_update.model_dump(exclude_unset=True)

    if "costRoll" in update_data:
        update_data.update(generate_prices(update_data["costRoll"]))

    result = await db["pieces"].find_one_and_update(
        {"code": code},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

    if not result:
        return None

    result["_id"] = str(result["_id"])

    combos = await db["combinedPieces"].find(
        {"typePieces": code}
    ).to_list(length=None)

    for combo in combos:
        pieces_data = await db["pieces"].find(
            {"code": {"$in": combo["typePieces"]}}
        ).to_list(length=None)

        variants = generate_combo_variants(pieces_data)
        await delete_variants_by_combo(combo["code"], db)
        await save_combo_variants(combo["code"], variants, db)

    return PieceModel(**result)
