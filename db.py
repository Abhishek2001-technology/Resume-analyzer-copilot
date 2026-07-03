from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from urllib.parse import quote_plus
import pymysql
import os
from dotenv import load_dotenv
load_dotenv()
pymysql.install_as_MySQLdb()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "ssl": {
            "fake_flag_to_enable_tls": True
        }
    }
)

Session_local = sessionmaker(bind=engine)
Base = declarative_base()

print("DB engine created!")

