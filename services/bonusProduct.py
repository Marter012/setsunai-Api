from motor.motor_asyncio import AsyncIOMotorDatabase
from models.bonusProduct import BonusProductModel,BonusProduct,BonusProductUpdate
from fastapi import HTTPException
from random import choices
import string
from pymongo import ReturnDocument
from typing import Optional
from pymongo.errors import DuplicateKeyError
# -------------------------
# Helpers
# -------------------------

def generate_code(length: int = 6) -> str:
    return "".join(choices(string.ascii_uppercase + string.digits, k=length))



# -------------------------
# CRUD
# -------------------------

async def get_bonusProduct(db: AsyncIOMotorDatabase):
    products = await db["bonusProduct"].find().to_list(length=None)

    if not products:
        raise HTTPException(status_code=404, detail="No hay productos extras.")

    return [
        BonusProductModel(
            **{**p, "_id": str(p["_id"])}
        )
        for p in products
    ]


async def add_bonusProduct(bonusProduct : BonusProduct,db : AsyncIOMotorDatabase):
    
    # 1. Convertir el modelo a dict
    bonusProduct_dict = bonusProduct.model_dump()
    
  # 3. Insert con reintentos por code duplicado
    for _ in range(5):
        bonusProduct_dict["code"] = generate_code()
        try:
            result = await db["bonusProduct"].insert_one(bonusProduct_dict)

            if not result.inserted_id:
                raise HTTPException(
                    status_code=500,
                    detail="No se pudo crear el producto extra."
                )

            # 4. Armar respuesta
            bonusProduct_dict["_id"] = str(result.inserted_id)
            return BonusProductModel(**bonusProduct_dict)

        except DuplicateKeyError:
            continue
         # 5. Fallo definitivo
    raise HTTPException(
        status_code=500,
        detail="No se pudo generar un código único"
    )

async def update_BonusProduct(code : str, bonusProductUpdate : BonusProductUpdate, db : AsyncIOMotorDatabase ) -> Optional[BonusProductModel]:
    updateData = bonusProductUpdate.model_dump(exclude_unset=True)
    
    current = await db["bonusProduct"].find_one({"code": code})
    if not current:
        return None
    
    if "name" in updateData:
        existing = await db["bonusProduct"].find_one({
            "name": {"$regex": f"^{updateData['name']}$", "$options": "i"},
            "code": {"$ne": code}  # 🔑 excluye el actual
        })

        if existing:
            raise HTTPException(
                status_code=400,
                detail="No se puede actualizar: ya existe otro producto con ese nombre"
            )
    # UPDATE BASE DEL PRODUCTO EXTRA
    
    result = await db["bonusProduct"].find_one_and_update(
        {"code" : code} ,
        {"$set": updateData},
        return_document=ReturnDocument.AFTER
    )
    
    if not result:
        return None
    
    # Convertir ID
    result["_id"] = str(result["_id"])
    
    return BonusProductModel(**result)
    
    