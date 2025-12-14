from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

engine = create_engine("sqlite:///job_logs.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class JobLog(Base):
    __tablename__ = "job_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    step = Column(String(100))
    message = Column(Text)
    keyword = Column(String(100))
    location = Column(String(100))
    success = Column(Integer, default=0)
    source = Column(String(100))
    job_count = Column(Integer, default=0)
    duration = Column(Float, default=0.0)

Base.metadata.create_all(bind=engine)
