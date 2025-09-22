from dataBase.DBConfing import get_db
import  string
from motor.motor_asyncio import AsyncIOMotorDatabase
from random import choices
from typing import Optional
from models.piece import Piece,PieceUpdate, PieceModel
from pymongo import ReturnDocument
from fastapi import HTTPException 

async def get_pieces(db):
    pieces_cursor = db["pieces"].find()
    pieces_list = []

    async for piece in pieces_cursor:
        piece["_id"] = str(piece["_id"])
        pieces_list.append(PieceModel(**piece))
    
    if not pieces_list:
        raise HTTPException(status_code=404, detail="No hay piezas disponibles")
    
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
    update_data = piece_update.model_dump(exclude_defaults=True)

    if not update_data:
        return None 

    result = await db["pieces"].find_one_and_update(
    {"code": code},
    {"$set": update_data},
    return_document=ReturnDocument.AFTER 
)

    if result:
        result["_id"] = str(result["_id"])
        return PieceModel(**result)

    return None