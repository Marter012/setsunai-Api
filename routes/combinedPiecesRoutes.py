# routes/combinedPieceRoutes.py
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List,Dict

from services.combinedPiecesService import get_combined_pieces, add_combined_piece, update_combined_piece
from services.comboVariantService import get_variants_by_combo, get_all_variants

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

@router.get("/combinedPieces/variants/{comboCode}")
async def list_combo_variants(comboCode: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    variants = await get_variants_by_combo(comboCode, db)
    if variants is None:
        raise HTTPException(status_code=404, detail="No se encontraron variantes para ese combinado.")
    return variants

@router.get("/comboVariants", response_model=List[Dict])
async def read_all_variants(db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Endpoint para traer todas las variantes de comboVariants
    """
    return await get_all_variants(db)

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
    if not updated:
        raise HTTPException(status_code=404, detail="No se encontró el combinado a actualizar.")
    return {"message": "Combinado actualizado correctamente", "combinedPiece": updated}
