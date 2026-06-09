import sqlalchemy, os, logging
from pathlib import Path
from flask.cli import load_dotenv
from constant import constants as cons
from constant import constants_dev as cons_dev
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

logger = logging.getLogger(__name__)

db=SQLAlchemy()
load_dotenv(Path(__file__).parent.parent / cons.FILE_NAME_ENV)
DATABASE_URL=os.environ.get('DATABASE_URL')
db_engine_local=sqlalchemy.create_engine(DATABASE_URL)