# models/combinedPiece.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class CombinedPiece(BaseModel):
    name: str = Field(..., min_length=1)
    img: str
    typePieces: List[str]
    proteins: List[str]
    description: str


class CombinedPieceModel(CombinedPiece):
    id: Optional[str] = Field(default=None, alias="_id")
    code: str
    # las variantes NO se guardan en el doc principal
    comboVariants: Optional[List[Dict[str, Any]]] = None
    state: bool = True

    model_config = {
        "populate_by_name": True,
        "validate_by_name": True
    }


class CombinedPieceUpdate(BaseModel):
    name: Optional[str]
    img: Optional[str]
    typePieces: Optional[List[str]]
    proteins: Optional[List[str]]
    description: Optional[str]
    state: Optional[bool]
