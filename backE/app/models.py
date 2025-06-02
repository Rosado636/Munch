from sqlmodel import SQLModel, Field
from typing import Optional

class Restaurant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    address: str
    rating: Optional[float] = 0.0