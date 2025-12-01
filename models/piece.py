from pydantic import BaseModel, Field
from typing import Optional


# Modelo que recibe el cliente
class Piece(BaseModel):
    name: str = Field(..., min_length=1)
    description: str
    img: str
    costRoll: float
    category: str
    protein : str


# Modelo que devuelve la DB
class PieceModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    code: str
    name: str
    description: str
    img: str
    price_3p: int
    price_4p: int
    price_5p: int
    price_8p: int
    price_16p: int
    category: str
    protein : str
    state: bool = True

    class Config:
        allow_population_by_field_name = True


# Modelo para actualizar
class PieceUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    img: Optional[str]
    costRoll: Optional[float]
    category: Optional[str]
    protein : Optional[str]
    state: Optional[bool]
