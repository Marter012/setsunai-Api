# services/comboVariantService.py
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any
from random import choices
import string

COLLECTION = "comboVariants"


def generate_variant_id(length: int = 12) -> str:
    return "".join(choices(string.ascii_uppercase + string.digits, k=length))


async def save_combo_variants(
    combo_code: str,
    variants: List[Dict[str, Any]],
    db: AsyncIOMotorDatabase
) -> List[Dict[str, Any]]:

    if not variants:
        return []

    docs = []
    for v in variants:
        doc = v.copy()
        doc["_id"] = generate_variant_id()
        doc["comboCode"] = combo_code
        docs.append(doc)

    await db[COLLECTION].insert_many(docs)
    return docs


async def get_variants_by_combo(
    combo_code: str,
    db: AsyncIOMotorDatabase
) -> List[Dict[str, Any]]:

    variants = await db[COLLECTION].find(
        {"comboCode": combo_code}
    ).to_list(length=None)

    return variants

async def get_all_variants(
    db: AsyncIOMotorDatabase
) -> List[Dict[str, Any]]:
    variants = await db[COLLECTION].find().to_list(length=None)

    if not variants:
        return []

    return variants

async def delete_variants_by_combo(
    combo_code: str,
    db: AsyncIOMotorDatabase
) -> int:

    result = await db[COLLECTION].delete_many(
        {"comboCode": combo_code}
    )
    return result.deleted_count
