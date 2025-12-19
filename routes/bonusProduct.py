from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.bonusProduct import BonusProductModel,BonusProduct,BonusProductUpdate
from models.response import ApiResponse
from services.bonusProduct import  get_bonusProduct,add_bonusProduct,update_BonusProduct
from motor.motor_asyncio import AsyncIOMotorDatabase
from dataBase.DBConfing import get_db

router = APIRouter()
COLLECTION_BONUS_PRODUCT = "bonusProduct"
@router.get(
    "/bonusProduct",
    response_model=List[BonusProductModel]
)
async def get_all_bonusProduct(
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    return await get_bonusProduct(db)


@router.post(
    "/addBonusProduct",
    response_model=ApiResponse[BonusProductModel],
    status_code=201
)
async def add_bonusProduct_route(
    bonusProduct: BonusProduct,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    existing = await db[COLLECTION_BONUS_PRODUCT].find_one({
        "name": {"$regex": f"^{bonusProduct.name}$", "$options": "i"}
    })
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un producto extra con ese nombre"
        )

    created = await add_bonusProduct(bonusProduct, db)

    return {
        "message": "Producto extra creado correctamente",
        "data": created
    }


@router.put(
    "/updateBonusProduct/{code}",
    response_model=ApiResponse[BonusProductModel]
)
async def modify_bonusProduct(
    code: str,
    bonusProductUpdate: BonusProductUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    updated = await update_BonusProduct(code, bonusProductUpdate, db)

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="No se encontró ningún producto extra con ese código"
        )

    return {
        "message": "Producto extra actualizado correctamente",
        "data": updated
    }
