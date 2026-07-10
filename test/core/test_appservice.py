import pytest, unittest.mock as mock, sqlalchemy, pandas as pd, constant.constants as cons, constant.constants_dev as cons_dev, main
from main import AppService, AppManager

patcher = mock.patch

@pytest.fixture
@patcher('main.DataContainer')
@patcher('main.BayesianScorer')
def config(scorer, container):
    uri = cons_dev.DUMMY_DB_URI
    engine = sqlalchemy.create_engine(uri)
    unit=AppService(engine)
    local_user_id=1
    return unit, local_user_id

@patcher('main.DataFilter')
def test_none_filter_tools(data_filter:mock.Mock, config):
    unit, local_user_id = config
    unit.run(None, local_user_id)
    data_filter.assert_called_once_with(unit.data)

@patcher('main.DataFilter')
def test_empty_dict_filter_tools(data_filter:mock.Mock, config):
    unit, local_user_id = config
    unit.run({}, local_user_id)
    data_filter.assert_called_once_with(unit.data)

@patcher('main.DataFilter')
def test_valid_filter_tools(data_filter:mock.Mock, config):
    unit, local_user_id = config
    filter_tools=cons_dev.TEST_VALID_FILTER_TOOLS
    unit.run(filter_tools, local_user_id)
    data_filter.assert_called_once_with(unit.data, filter_tools)
