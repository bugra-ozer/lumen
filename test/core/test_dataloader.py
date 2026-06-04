import io, pytest, pandas as pd, pathlib as pl
from unittest.mock import MagicMock
from constant import constants_dev as cons_dev
from constant import constants as cons
from unittest import mock
from main import DataLoader

patch = mock.patch

@patch('main.pd.read_parquet')
def test_read_parquet(mock_parquet):
    unit = DataLoader()
    mock_parquet.return_value = pd.DataFrame()
    path=pl.Path(cons_dev.MOCK_RANDOM_PATH)
    read=unit.read_file(cons_dev.MOCK_RANDOM_PATH, cons.STR_PARQUET)
    mock_parquet.assert_called_once_with(path)
    assert isinstance(read,pd.DataFrame)

@patch('main.pd.read_csv')
def test_read_csv(mock_tsv, usecols=None):
    unit = DataLoader()
    mock_tsv.return_value = pd.DataFrame()
    path=pl.Path(cons_dev.MOCK_RANDOM_PATH)
    read=unit.read_file(cons_dev.MOCK_RANDOM_PATH, 'tsv')
    mock_tsv.assert_called_once_with(path, delimiter='\t', encoding='latin-1', on_bad_lines='skip', na_values='\\N', usecols=usecols)
    assert isinstance(read,pd.DataFrame)

@patch('main.pd.DataFrame.to_parquet')
def test_to_parquet(mock_to_parquet):
    unit = DataLoader()
    mock_to_parquet.return_value = None
    path=cons_dev.MOCK_RANDOM_PATH #raw string
    write=unit.save_file(pd.DataFrame(),path)
    mock_to_parquet.assert_called_once_with(path)
    assert isinstance(write,DataLoader)

def test_merge():
    merge_to=pd.DataFrame([cons_dev.DUMMY_DATAFRAME_DATA[0]], columns=cons_dev.DUMMY_DATAFRAME_COLUMNS_ONE)
    merge_from=pd.DataFrame([cons_dev.DUMMY_DATAFRAME_DATA[1]], columns=cons_dev.DUMMY_DATAFRAME_COLUMNS_TWO)
    merge=merge_to.merge(merge_from, on=cons_dev.DUMMY_DATAFRAME_COLUMNS_ONE[0])
    all_columns=set()
    all_columns.update(merge_to.columns, merge_from.columns)
    for column in all_columns:
        assert column in list(merge)

