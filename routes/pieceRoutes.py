# routes/pieceRoutes.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase

from models.piece import Piece, PieceUpdate, PieceModel
from models.response import ApiResponse
from services.pieceService import get_pieces, add_piece, update_piece
from dataBase.DBConfing import get_db

router = APIRouter()
COLLECTION_PIECES = "pieces"


# 🔹 GET – lista de piezas
@router.get(
    "/pieces",
    response_model=List[PieceModel]
)
async def get_all_pieces(
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    return await get_pieces(db)


# 🔹 POST – crear pieza
@router.post(
    "/addPiece",
    response_model=ApiResponse[PieceModel],
    status_code=201
)
async def add_piece_route(
    piece: Piece,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    existing = await db[COLLECTION_PIECES].find_one({
        "name": {"$regex": f"^{piece.name}$", "$options": "i"}
    })

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una pieza con ese nombre"
        )

    created = await add_piece(piece, db)

    return {
        "message": "Pieza agregada correctamente",
        "data": created
    }


# 🔹 PUT – actualizar pieza
@router.put(
    "/updatePiece/{code}",
    response_model=ApiResponse[PieceModel]
)
async def modify_piece(
    code: str,
    piece: PieceUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if piece.name:
        duplicate = await db[COLLECTION_PIECES].find_one({
            "name": {"$regex": f"^{piece.name}$", "$options": "i"},
            "code": {"$ne": code}
        })

        if duplicate:
            raise HTTPException(
                status_code=400,
                detail="Ya existe otra pieza con ese nombre"
            )

    updated = await update_piece(code, piece, db)

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="No se encontró la pieza a actualizar"
        )

    return {
        "message": "Pieza actualizada correctamente",
        "data": updated
    }
