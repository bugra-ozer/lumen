import sqlalchemy, os
from constant import constants as cons
from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()
db_engine=sqlalchemy.create_engine(os.environ.get("DATABASE_URL"))