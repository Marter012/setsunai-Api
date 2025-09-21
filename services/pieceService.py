from dataBase.DBConfing import get_db
import  string
from motor.motor_asyncio import AsyncIOMotorDatabase
from random import choices
from typing import Optional
from models.piece import Piece,PieceUpdate, PieceModel


async def get_pieces(db):
    pieces_cursor = db["pieces"].find()
    pieces_list = []

    async for piece in pieces_cursor:
        # Convertimos _id de ObjectId a str
        piece["_id"] = str(piece["_id"])
        pieces_list.append(PieceModel(**piece))
    
    return pieces_list

def generate_code(length: int = 6) -> str:
    return "".join(choices(string.ascii_uppercase + string.digits, k=length))

async def add_piece(piece: Piece, db: AsyncIOMotorDatabase):
    piece_dict = piece.model_dump()
    piece_dict["code"] = generate_code()
    piece_dict["state"] = True
    result = await db["pieces"].insert_one(piece_dict)
    piece_dict["_id"] = str(result.inserted_id)
    return PieceModel(**piece_dict)

async def update_piece(code: str, piece_update: PieceUpdate, db: AsyncIOMotorDatabase) -> Optional[PieceModel]:
    """
    Actualiza los campos de una pieza, incluido 'state'.
    Solo se actualizan los campos que se envían.
    Devuelve el documento actualizado como PieceModel.
    """
    # Convertimos a dict y eliminamos los campos que no se enviaron
    update_data = piece_update.dict(exclude_unset=True)

    if not update_data:
        return None  # no hay nada para actualizar

    # Actualizamos en la DB y devolvemos el documento actualizado
    result = await db["pieces"].find_one_and_update(
        {"code": code},
        {"$set": update_data},
        return_document=True  # devuelve el documento después del update
    )

    if result:
        # Convertimos ObjectId a string para Pydantic
        result["_id"] = str(result["_id"])
        return PieceModel(**result)

    return None  # si no encontró la pieza