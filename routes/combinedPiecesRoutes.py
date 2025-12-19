# routes/combinedPieceRoutes.py
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict

from services.combinedPiecesService import (
    get_combined_pieces,
    add_combined_piece,
    update_combined_piece
)
from services.comboVariantService import (
    get_variants_by_combo,
    get_all_variants
)

from models.combinedPiece import (
    CombinedPiece,
    CombinedPieceUpdate,
    CombinedPieceModel
)
from models.response import ApiResponse
from dataBase.DBConfing import get_db

router = APIRouter()
COLLECTION_COMBINED = "combinedPieces"


# 🔹 GET – lista de combinados
@router.get(
    "/combinedPieces",
    response_model=List[CombinedPieceModel]
)
async def list_combined_pieces(
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    combined = await get_combined_pieces(db)

    if not combined:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron combinados de piezas"
        )

    return combined


# 🔹 GET – variantes por combo
@router.get(
    "/combinedPieces/variants/{comboCode}",
    response_model=List[Dict]
)
async def list_combo_variants(
    comboCode: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    variants = await get_variants_by_combo(comboCode, db)

    if not variants:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron variantes para ese combinado"
        )

    return variants


# 🔹 GET – todas las variantes
@router.get(
    "/comboVariants",
    response_model=List[Dict]
)
async def read_all_variants(
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    return await get_all_variants(db)


# 🔹 POST – crear combinado
@router.post(
    "/addCombinedPieces",
    response_model=ApiResponse[CombinedPieceModel],
    status_code=201
)
async def create_combined_piece(
    payload: CombinedPiece,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    existing = await db[COLLECTION_COMBINED].find_one({
        "name": {"$regex": f"^{payload.name}$", "$options": "i"}
    })

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un combinado con ese nombre"
        )

    created = await add_combined_piece(payload, db)

    return {
        "message": "Combinado agregado correctamente",
        "data": created
    }


# 🔹 PUT – actualizar combinado
@router.put(
    "/updateCombinedPieces/{code}",
    response_model=ApiResponse[CombinedPieceModel]
)
async def modify_combined_piece(
    code: str,
    payload: CombinedPieceUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if payload.name:
        existing = await db[COLLECTION_COMBINED].find_one({
            "name": {"$regex": f"^{payload.name}$", "$options": "i"},
            "code": {"$ne": code}
        })

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Ya existe un combinado con ese nombre"
            )

    updated = await update_combined_piece(code, payload, db)

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el combinado a actualizar"
        )

    return {
        "message": "Combinado actualizado correctamente",
        "data": updated
    }
