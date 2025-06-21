from sqlalchemy import Column, Integer, String, Date
from database import Base

class PersonModel(Base):
    __tablename__ = "people"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    gender = Column(String)
    birth_date = Column(Date)
    nationality = Column(String)
    current_address = Column(String)
    notes = Column(String, nullable=True)
