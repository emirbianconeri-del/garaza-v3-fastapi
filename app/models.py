from sqlalchemy import Column, Integer, String
from .database import Base

class VoziloDB(Base):
    __tablename__ = "vozila"

    id = Column(Integer, primary_key=True, index=True)
    marka = Column(String, nullable=False, index=True)
    model = Column(String, nullable=False)
    godiste = Column(Integer, nullable=False, index=True)
    tablice = Column(String, nullable=False, unique=True, index=True)
