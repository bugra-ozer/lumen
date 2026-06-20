import unittest, pytest, sqlalchemy, pandas as pd
from unittest import mock
from main import DataPipeline
from constant import constants_dev as cons_dev, constants as cons

@pytest.fixture
def config():
    uri = cons_dev.DUMMY_DB_URI
    engine = sqlalchemy.create_engine(uri)
    unit=DataPipeline(engine)
    unit.data_loader=mock.Mock()
    unit.dataset_downloader=mock.Mock()
    return unit

def test_load_tsv(config):
    unit=config
    df=cons_dev.DUMMY_DATAFRAME_CONTENT
    dummy_config_dict=cons_dev.DUMMY_DICT_DATASET
    unit.data_loader.load_config.return_value = dummy_config_dict
    unit.data_loader.count_query_db.return_value = 0
    unit.data_loader.read_file.return_value = df
    unit.data_loader.merge_dataframes.return_value = df
    unit.data_loader.rename_columns.return_value = df
    result, needs_assert=unit.main()
    assert needs_assert==True
    pd.testing.assert_frame_equal(result,df)
    unit.data_loader.read_file.assert_called_once_with(mock.ANY, cons.STR_TSV, mock.ANY, usecols=mock.ANY)