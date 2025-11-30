from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from services.combinedPiecesService import get_combined_pieces, add_combined_piece, update_combined_piece
from models.combinedPiece import CombinedPiece, CombinedPieceUpdate
from dataBase.DBConfing import get_db

router = APIRouter()
COLLECTION_COMBINED = "combinedPieces"

@router.get("/combinedPieces")
async def list_combined_pieces(db: AsyncIOMotorDatabase = Depends(get_db)):
    combined = await get_combined_pieces(db)
    if not combined:
        raise HTTPException(status_code=404, detail="No se encontraron combinados de piezas.")
    return combined

@router.post("/addCombinedPieces")
async def create_combined_piece(payload: CombinedPiece, db: AsyncIOMotorDatabase = Depends(get_db)):
    existing = await db[COLLECTION_COMBINED].find_one({
        "name": {"$regex": f"^{payload.name}$", "$options": "i"}
    })
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un combinado con ese nombre")
    try:
        new_doc = await add_combined_piece(payload, db)
        return {"message": "Combinado agregado correctamente", "combinedPiece": new_doc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar el combinado: {str(e)}")

@router.put("/updateCombinedPieces/{code}")
async def modify_combined_piece(
    code: str,
    payload: CombinedPieceUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    # Validar duplicado de nombre si se envía
    if payload.name:
        existing = await db[COLLECTION_COMBINED].find_one({
            "name": {"$regex": f"^{payload.name}$", "$options": "i"},
            "code": {"$ne": code}
        })
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Ya existe un combinado con ese nombre, elige otro."
            )

    updated = await update_combined_piece(code, payload, db)
    return {"message": "Combinado actualizado correctamente", "combinedPiece": updated}
