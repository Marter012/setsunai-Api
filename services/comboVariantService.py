# services/comboVariantService.py
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any
from models.comboVariant import ComboVariantModel
from random import choices
import string

COLLECTION = "comboVariants"

def _generate_variant_id(length: int = 12) -> str:
    return "".join(choices(string.ascii_uppercase + string.digits, k=length))

async def save_combo_variants(combo_code: str, variants: List[Dict[str, Any]], db: AsyncIOMotorDatabase) -> List[Dict[str, Any]]:
    """
    Guarda una lista de variantes en la colección comboVariants, asociadas a combo_code.
    Cada variante recibida se le agrega comboCode y _id.
    Devuelve la lista de variantes insertadas (en formato dict).
    """
    if not variants:
        return []

    docs = []
    for v in variants:
        doc = v.copy()
        doc["comboCode"] = combo_code
        # generar id local, para consistencia
        doc["_id"] = _generate_variant_id()
        docs.append(doc)

    if docs:
        await db[COLLECTION].insert_many(docs)

    # convertir _id a str si hace falta (ya es string generado)
    return docs

async def get_variants_by_combo(combo_code: str, db: AsyncIOMotorDatabase) -> List[Dict[str, Any]]:
    """Devuelve las variantes asociadas a un comboCode."""
    cursor = db[COLLECTION].find({"comboCode": combo_code})
    variants = await cursor.to_list(length=None)
    # si viniesen ObjectId, los convertiríamos a str; aquí _id ya es string
    for v in variants:
        if "_id" in v:
            v["_id"] = str(v["_id"])
    return variants

async def get_all_variants(db: AsyncIOMotorDatabase) -> List[Dict[str, Any]]:
    """
    Retorna todas las variantes de comboVariants.
    """
    cursor = db[COLLECTION].find({})
    variants = await cursor.to_list(length=None)

    if not variants:
        return []  # o lanzar HTTPException si querés

    # convertir _id a string por consistencia
    for v in variants:
        if "_id" in v:
            v["_id"] = str(v["_id"])

    return variants


async def delete_variants_by_combo(combo_code: str, db: AsyncIOMotorDatabase) -> int:
    """Elimina todas las variantes asociadas a combo_code. Retorna count eliminados."""
    result = await db[COLLECTION].delete_many({"comboCode": combo_code})
    return result.deleted_count
