from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config


SQLALCHEMY_DATABASE_URL = "mysql://root:eJNSpIFuKbxqUxFoXyTFDLxrKBaFndgd@autorack.proxy.rlwy.net:25532/railway"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

