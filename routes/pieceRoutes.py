from fastapi import APIRouter,Depends,HTTPException
from models.piece import Piece,PieceUpdate
from services.pieceService import get_pieces, add_piece, update_piece
from dataBase.DBConfing import get_db
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

router = APIRouter()

COLLECTION_PIECES = "pieces"

@router.get("/pieces")
async def get_all_pieces(db: AsyncIOMotorDatabase = Depends(get_db)):
    pieces = await get_pieces(db)
    return pieces  # FastAPI ya serializa Pydantic a JSON

@router.post("/addPiece")
async def add_piece_route(piece: Piece, db: AsyncIOMotorDatabase = Depends(get_db)):
    existing = await db[COLLECTION_PIECES].find_one({
        "name": {"$regex": f"^{piece.name}$", "$options": "i"}
    })
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una pieza con ese nombre")

    new_piece = await add_piece(piece, db)
    return {"message": "Pieza agregada correctamente", "piece": new_piece}

@router.put("/updatePieces/{code}")
async def modify_piece(code: str, piece: PieceUpdate, db: AsyncIOMotorDatabase = Depends(get_db)):
    # 1️⃣ Validar que el código exista
    existing_piece = await db[COLLECTION_PIECES].find_one({"code": code})
    if not existing_piece:
        raise HTTPException(status_code=404, detail="No se encontró ninguna pieza con ese código")

    # 2️⃣ Validar nombre duplicado (si se envía)
    if piece.name:
        duplicate = await db[COLLECTION_PIECES].find_one({
            "name": {"$regex": f"^{piece.name}$", "$options": "i"},
            "code": {"$ne": code}
        })
        if duplicate:
            raise HTTPException(status_code=400, detail="Ya existe otra pieza con ese nombre")

    # 3️⃣ Hacer el update
    updated = await update_piece(code, piece, db)
    return {"message": "Pieza actualizada con éxito", "piece": updated}