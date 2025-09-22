from pydantic import BaseModel, Field
from typing import Optional

# Modelo para recibir datos del cliente
class Piece(BaseModel):
    name: str = Field(..., min_length=1)
    description: str
    img: str
    price : str
    category : str 
    
# Modelo para devolver datos desde la DB
class PieceModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")  # ahora puede ser None
    code: str
    name: str
    description: str
    img: str
    price : str
    category : str
    state: bool = True

    class Config:
        allow_population_by_field_name = True


class PieceUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    img: Optional[str]
    price : Optional[str]
    category : Optional[str]
    state: Optional[bool]