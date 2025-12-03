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
    comboVariants: Optional[List[Dict[str, Any]]] = []
    state: bool = True

    class Config:
        allow_population_by_field_name = True

class CombinedPieceUpdate(BaseModel):
    name: Optional[str]
    img: Optional[str]
    typePieces: Optional[List[str]]
    proteins: Optional[List[str]]
    description: Optional[str]
    comboVariants: Optional[List[dict]]   # NUEVO PERMITIDO PERO NO OBLIGATORIO
    state: Optional[bool]
