from pydantic import BaseModel
from datetime import datetime


class PenisDataBase(BaseModel):
    username: str
    length: float


class PenisDataResponse(PenisDataBase):
    id: int
    last_updated: datetime

    class Config:
        orm_mode = True
