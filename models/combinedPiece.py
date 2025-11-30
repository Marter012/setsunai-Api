from pydantic import BaseModel, Field
from typing import Optional, List

# Para recibir datos del cliente
class CombinedPiece(BaseModel):
    name: str
    img: str
    typePieces: List[str]    # Lista de códigos de piezas
    price: float             # Precio como número

# Para devolver datos desde la DB
class CombinedPieceModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    code: str
    name: str
    img: str
    typePieces: List[str]
    price: float
    state: bool = True

    class Config:
        allow_population_by_field_name = True

# Para actualizar
class CombinedPieceUpdate(BaseModel):
    name: Optional[str]
    img: Optional[str]
    typePieces: Optional[List[str]]
    price: Optional[float]
    state: Optional[bool]
