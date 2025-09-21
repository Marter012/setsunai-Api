from pydantic import BaseModel, Field
from typing import Optional

# Para recibir datos del cliente
class CombinedPiece(BaseModel):
    name: str
    img: str
    typePieces: str  # siempre string

# Para devolver datos desde la DB
class CombinedPieceModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    code: str
    name: str
    img: str
    typePieces: str
    state: bool = True

    class Config:
        allow_population_by_field_name = True

# Para actualizar
class CombinedPieceUpdate(BaseModel):
    name: Optional[str]
    img: Optional[str]
    typePieces: Optional[str]
    state: Optional[bool]