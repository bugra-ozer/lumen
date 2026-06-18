import pandas as pd, pathlib as pl, logging, sqlalchemy, pytest
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError, DatabaseError
from constant import constants as cons
from constant import constants_dev as cons_dev
from constant.constants import TABLE_NAME_PREVIOUS_DATA
from db.models import PreviousData
from persister import state_store
from main import DataPipeline

logger = logging.getLogger(__name__)

#TODO apply missing ORM backtrack or connection and add fixed constants at the start of the program as engine and uri is used across.

@pytest.fixture
def config():
    uri = cons_dev.DUMMY_DB_URI
    engine = sqlalchemy.create_engine(uri)
    unit = state_store.StateStore(table_name=cons.TABLE_NAME_PREVIOUS_DATA, engine=engine)
    pipeline=DataPipeline(engine=engine)
    pipeline._setup_schema() # noqa
    yield unit, engine

def test_load_file_missing_table(config):
    unit, engine = config
    unit.manage_files()
    assert unit.data.empty == True
    assert list(unit.data.columns) == list(cons.TABLE_COLUMNS_PREVIOUS)

def test_load_memory(config):
    unit, engine = config
    dummy_df = cons_dev.DUMMY_DATAFRAME_PREVIOUS
    dummy_df.to_sql(cons.TABLE_NAME_PREVIOUS_DATA, engine, index=False, if_exists='append')
    unit.manage_files()
    pd.testing.assert_frame_equal(unit.data,dummy_df, check_dtype=False)  # add check_dtype parameter as False if test becomes too sensitive

def test_save_file(config):
    unit, engine = config
    unit.data=cons_dev.DUMMY_DATAFRAME_MIXED_PREVIOUS
    unit.save_file()
    returned_df=pd.read_sql(sqlalchemy.text(f'SELECT * FROM {TABLE_NAME_PREVIOUS_DATA}'), engine)
    returned_df=returned_df.drop(columns=[cons.TABLE_ID_PREVIOUS_DATA, cons.TABLE_ID_DATE], inplace=False)
    comparison_df=cons_dev.DUMMY_DATAFRAME_PREVIOUS.drop(columns=[cons.TABLE_ID_PREVIOUS_DATA, cons.TABLE_ID_DATE], inplace=False)
    pd.testing.assert_frame_equal(returned_df, comparison_df, check_dtype=False)