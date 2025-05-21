from sqlalchemy import create_engine, Column, Integer, Float, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class UserData(Base):
    __tablename__ = 'carbon_data'
    id = Column(Integer, primary_key=True)
    car_km = Column(Integer)
    bike_km = Column(Integer)
    bus_km = Column(Integer)
    flight_km = Column(Integer)
    electricity_kwh = Column(Integer)
    lpg_kg = Column(Integer)
    diet_type = Column(String)
    clothes = Column(Integer)
    gadgets = Column(Integer)
    total_emission = Column(Float)
    trees_needed = Column(Float)
    date = Column(Date, default=datetime.date.today)

engine = create_engine('sqlite:///carbon_footprint.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
