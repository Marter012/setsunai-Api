# models/comboVariant.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ComboVariant(BaseModel):
    comboCode: str
    take: int
    perRoll: int
    pieces: List[Dict[str, Any]]
    totalPieces: int
    finalPrice: float


class ComboVariantModel(ComboVariant):
    id: Optional[str] = Field(default=None, alias="_id")

    model_config = {
        "populate_by_name": True,
        "validate_by_name": True
    }
