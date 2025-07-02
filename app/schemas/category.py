from pydantic import BaseModel, ConfigDict
from typing import Optional


class CategoryCreate(BaseModel):
    name: str
    color: Optional[str]  # Default white color


class CategoryResponse(BaseModel):
    id: int
    name: str
    color: Optional[str]

    model_config = ConfigDict(from_attributes=True)
