import pytest, unittest.mock as mock, sqlalchemy, pandas as pd
from constant import constants_dev as cons_dev, constants as cons
from main import DataContainer

@pytest.fixture
def config():
    """Setup prerequisites for DataContainer class"""
    uri = cons_dev.DUMMY_DB_URI
    engine = sqlalchemy.create_engine(uri)
    unit=DataContainer(engine)
    unit.data_pipeline=mock.Mock()
    return unit

def test_db_path(config):
    unit:DataContainer=config
    pipeline_returned_df=cons_dev.DUMMY_DATAFRAME_CONTENT
    unit.data_pipeline.main.return_value=pipeline_returned_df, False
    unit.build_container()
    pd.testing.assert_frame_equal(unit.data, pipeline_returned_df)