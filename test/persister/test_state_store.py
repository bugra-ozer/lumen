import pandas as pd, pathlib as pl, logging, sqlalchemy, pytest
from sqlalchemy.exc import OperationalError, DatabaseError
from constant import constants as cons
from constant import constants_dev as cons_dev
from db.models import PreviousData
from persister import state_store

logger = logging.getLogger(__name__)

def test_load_file_missing_table():
    uri=cons_dev.DUMMY_DB_URI
    engine=sqlalchemy.create_engine(uri)
    unit=state_store.StateStore(table_name=cons.TABLE_NAME_PREVIOUS_DATA, engine=engine)
    unit.manage_files()
    assert unit.data.empty == True
    assert list(unit.data.columns) == list(cons.TABLE_COLUMNS_PREVIOUS)

def test_load_memory():
    uri=cons_dev.DUMMY_DB_URI
    engine=sqlalchemy.create_engine(uri)
    dummy_df=cons_dev.DUMMY_DATAFRAME_PREVIOUS
    dummy_df.to_sql(cons.TABLE_NAME_PREVIOUS_DATA, engine, index=False)
    unit=state_store.StateStore(table_name=cons.TABLE_NAME_PREVIOUS_DATA, engine=engine)
    unit.manage_files()
    pd.testing.assert_frame_equal(unit.data, dummy_df) #add check_dtype parameter as False if test becomes too sensitive
