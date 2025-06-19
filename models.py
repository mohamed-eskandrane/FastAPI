from sqlalchemy import Column, Integer, String, Date
from database import Base

class PersonModel(Base):
    __tablename__ = "people"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    nationality = Column(String, nullable=False)
    current_address = Column(String, nullable=False)
    notes = Column(String, nullable=True)
