import pytest, unittest.mock as mock, sqlalchemy, pandas as pd, constant.constants_dev as cons_dev
from main import AppService

@pytest.fixture
def config():
    uri = cons_dev.DUMMY_DB_URI
    engine = sqlalchemy.create_engine(uri)
    unit=AppService(engine)
    unit.container=mock.Mock()
    unit.bayes=mock.Mock()
    return unit