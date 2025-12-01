from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from random import choices
import string
import math
from models.piece import Piece, PieceUpdate, PieceModel
from fastapi import HTTPException
from pymongo import ReturnDocument


# -------------------------
# Helpers
# -------------------------

def generate_code(length: int = 6) -> str:
    return "".join(choices(string.ascii_uppercase + string.digits, k=length))


def round_500(value: float) -> int:
    return int(math.ceil(value / 200) * 200)


def generate_prices(cost: float) -> dict:
    pieceUnit = cost / 8
    return {
        "price_3p": round_500((pieceUnit * 3) * 3.1),
        "price_4p": round_500((pieceUnit * 4) * 3.1),
        "price_5p": round_500((pieceUnit * 5) * 3.1),
        "price_8p": round_500((pieceUnit * 8) * 3),
        "price_16p": round_500((pieceUnit * 16) * 2.5),
    }


# -------------------------
# CRUD
# -------------------------

async def get_pieces(db: AsyncIOMotorDatabase):
    pieces_cursor = db["pieces"].find()
    pieces_list = []

    async for piece in pieces_cursor:
        piece["_id"] = str(piece["_id"])
        pieces_list.append(PieceModel(**piece))

    if not pieces_list:
        raise HTTPException(status_code=404, detail="No hay piezas disponibles")

    return pieces_list


async def add_piece(piece: Piece, db: AsyncIOMotorDatabase):
    piece_dict = piece.model_dump()

    cost = piece_dict["costRoll"]
    prices = generate_prices(cost)

    piece_dict.update(prices)
    piece_dict["code"] = generate_code()
    piece_dict["state"] = True

    result = await db["pieces"].insert_one(piece_dict)
    piece_dict["_id"] = str(result.inserted_id)

    return PieceModel(**piece_dict)


async def update_piece(code: str, piece_update: PieceUpdate, db: AsyncIOMotorDatabase) -> Optional[PieceModel]:
    update_data = piece_update.model_dump(exclude_defaults=True)

    # Si cambia el costo, recalculamos todos los precios
    if "costRoll" in update_data:
        cost = update_data["costRoll"]
        prices = generate_prices(cost)
        update_data.update(prices)

    result = await db["pieces"].find_one_and_update(
        {"code": code},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

    if result:
        result["_id"] = str(result["_id"])
        return PieceModel(**result)

    return None
