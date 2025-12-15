# models/comboVariant.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ComboVariantPiece(BaseModel):
    pieceCode: str
    pieceName: str
    pieceCount: int
    price: float

class ComboVariantModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    comboCode: str
    take: int
    perRoll: int
    pieces: List[Dict[str, Any]] 
    totalPieces: int
    finalPrice: float

    class Config:
        allow_population_by_field_name = True
