import asyncio

from dataBase.DBConfing import connect_to_db, close_db
from services.combinedPiecesService import generate_combo_variants
from services.comboVariantService import (
    save_combo_variants,
    delete_variants_by_combo
)

COMBOS_COLLECTION = "combinedPieces"
PIECES_COLLECTION = "pieces"


async def rebuild_all_variants():
    db = await connect_to_db()  # 👈 MISMA DB QUE FASTAPI

    combos = await db[COMBOS_COLLECTION].find({}).to_list(length=None)
    print(f"👉 Combos encontrados: {len(combos)}")

    for combo in combos:
        code = combo["code"]

        pieces_data = await db[PIECES_COLLECTION].find(
            {"code": {"$in": combo["typePieces"]}}
        ).to_list(length=None)

        print(f"🔄 Combo {code} → piezas: {len(pieces_data)}")

        new_variants = generate_combo_variants(pieces_data)
        print(f"   variantes nuevas: {len(new_variants)}")

        await delete_variants_by_combo(code, db)
        await save_combo_variants(code, new_variants, db)

        print(f"✔ Variantes regeneradas para {code}")

    await close_db()


if __name__ == "__main__":
    asyncio.run(rebuild_all_variants())
