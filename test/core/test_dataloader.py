import io, pytest, pandas as pd, pathlib as pl, logging, sqlalchemy
from unittest.mock import MagicMock
from constant import constants_dev as cons_dev
from constant import constants as cons
from unittest import mock
from db.database import engine_standalone
from main import DataLoader
from db import database as db

logger = logging.getLogger(__name__)
patch = mock.patch

@patch('main.pd.read_sql')
def test_read_sql(mock_sql):
    """Test read SQL method is called once and consistent."""
    unit = DataLoader()
    mock_sql.return_value = pd.DataFrame()
    table_name=cons.TABLE_NAME_CONTENT
    read=unit.read_file(table_name, cons.STR_SQL, engine_standalone)
    mock_sql.assert_called_once_with(mock.ANY, engine_standalone)
    assert isinstance(read,pd.DataFrame)

@patch('main.pd.read_csv')
def test_read_csv(mock_tsv, usecols=None):
    """Test csv/tsv read is called once and consistent."""
    unit = DataLoader()
    mock_tsv.return_value = pd.DataFrame()
    path=pl.Path(cons_dev.MOCK_RANDOM_PATH)
    read=unit.read_file(cons_dev.MOCK_RANDOM_PATH, cons.STR_TSV, engine_standalone)
    mock_tsv.assert_called_once_with(path, delimiter='\t', encoding='latin-1', on_bad_lines='skip', na_values='\\N', usecols=usecols)
    assert isinstance(read,pd.DataFrame)

@patch('main.pd.DataFrame.to_sql')
def test_to_sql(mock_to_sql):
    """Test SQL insertion is called once and consistent."""
    unit = DataLoader()
    mock_to_sql.return_value = None
    table_name=cons.TABLE_NAME_CONTENT #raw string
    write=unit.save_file(pd.DataFrame(), table_name, engine_standalone, cons.STR_SQL)
    mock_to_sql.assert_called_once_with(mock.ANY, engine_standalone, if_exists='append', index=False)
    assert isinstance(write,DataLoader)

def test_merge():
    """Test pandas merge method consistency."""
    merge_to=pd.DataFrame([cons_dev.DUMMY_DATAFRAME_TWO_COLUMN[0]], columns=cons_dev.DUMMY_DATAFRAME_COLUMNS_ONE)
    merge_from=pd.DataFrame([cons_dev.DUMMY_DATAFRAME_TWO_COLUMN[1]], columns=cons_dev.DUMMY_DATAFRAME_COLUMNS_TWO)
    merge=merge_to.merge(merge_from, on=cons_dev.DUMMY_DATAFRAME_COLUMNS_ONE[0])
    all_columns=set()
    all_columns.update(merge_to.columns, merge_from.columns)
    for column in all_columns:
        assert column in list(merge)

