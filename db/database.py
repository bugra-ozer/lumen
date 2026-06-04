import sqlalchemy, os, logging
from pathlib import Path
from flask.cli import load_dotenv
from constant import constants as cons
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)

db=SQLAlchemy()
load_dotenv(dotenv_path=Path(__file__).parent.parent / cons.FILE_NAME_ENV)
db_engine=sqlalchemy.create_engine(os.environ.get("DATABASE_URL"))