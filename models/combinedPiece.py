# models/combinedPiece.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class CombinedPiece(BaseModel):
    name: str
    img: str
    typePieces: List[str]
    proteins: List[str]
    description: str


class CombinedPieceModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    code: str
    name: str
    img: str
    typePieces: List[str]
    proteins: List[str]
    description: str
    # las variantes no se guardan dentro del doc principal
    comboVariants: Optional[List[Dict[str, Any]]] = None
    state: bool = True

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class CombinedPieceUpdate(BaseModel):
    name: Optional[str] = None
    img: Optional[str] = None
    typePieces: Optional[List[str]] = None
    proteins: Optional[List[str]] = None
    description: Optional[str] = None
    comboVariants: Optional[List[dict]] = None
    state: Optional[bool] = None
