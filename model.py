from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PenisData(Base):
    __tablename__ = "penis_data"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(25))
    length = Column(Float, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
