# models/bonusProduct.py
from pydantic import BaseModel, Field
from typing import Optional

class BonusProduct(BaseModel):
    name: str = Field(..., min_length=1)
    description: str
    img: str
    type: str
    price: int = Field(..., ge=0)


class BonusProductModel(BonusProduct):
    id: Optional[str] = Field(default=None, alias="_id")
    code: str
    state: bool = True

    model_config = {
        "populate_by_name": True,
        "validate_by_name": True
    }


class BonusProductUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    img: Optional[str]
    type: Optional[str]
    price: Optional[int]
    state: Optional[bool]
