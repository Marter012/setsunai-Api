from pydantic import BaseModel, Field
from typing import Optional, List

# Para recibir datos del cliente
class CombinedPiece(BaseModel):
    name: str
    img: str
    typePieces: List[str]    # Lista de códigos de piezas
    proteins: List[str]    # Lista de códigos de proteínas
    description: str
    

# Para devolver datos desde la DB
class CombinedPieceModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    code: str
    name: str
    img: str
    typePieces: List[str]
    proteins: List[str]  
    description: str
    state: bool = True

    class Config:
        allow_population_by_field_name = True

# Para actualizar
class CombinedPieceUpdate(BaseModel):
    name: Optional[str]
    img: Optional[str]
    typePieces: Optional[List[str]]
    proteins: Optional[List[str]]   
    description: Optional[str]
    state: Optional[bool]
