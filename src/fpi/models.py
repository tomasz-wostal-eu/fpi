from sqlalchemy import Column, Integer, String
from .database import Base
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Plant(Base):
    __tablename__ = "plants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    latin_name = Column(String, index=True, nullable=False)