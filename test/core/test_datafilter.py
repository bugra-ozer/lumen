import io, main, pytest, pandas as pd, pathlib as pl, logging
from validator import validator
from unittest import mock
from unittest.mock import MagicMock
from constant import constants_dev as cons_dev, constants as cons

logger = logging.getLogger(__name__)
patch = mock.patch

def test_happy_path():
    """Test valid filter_tools, valid DataFrame is producing consistent results."""
    all_columns= cons.CONTENT_COLUMNS_TO_KEEP + (cons.ADJUSTED_SCORE_COLUMN,)
    fake_df=pd.DataFrame(columns=all_columns, data=[["tt0014358",7.2,6236,"The Pilgrim",1923,"Action, Horror",5]])
    fake_filter_tools=cons_dev.DUMMY_FILTER_TOOLS
    unit=main.DataFilter(fake_df, fake_filter_tools)
    assert validator.is_ready_structure(fake_df, fake_filter_tools) and len(unit.result)>=1

def test_sad_df_path():
    """Test invalid DataFrame insertions raise correct error."""
    fake_df=pd.DataFrame(columns=[cons.PATH_COLUMN,cons.DATE_COLUMN], data=[[cons_dev.DUMMY_PATH,cons_dev.DUMMY_DATE]])
    fake_filter_tools=cons_dev.DUMMY_FILTER_TOOLS
    with pytest.raises(KeyError):
        main.DataFilter(fake_df, fake_filter_tools)

def test_sad_filter_path():
    """Test invalid filter_tools raise correct error."""
    all_columns = cons.CONTENT_COLUMNS_TO_KEEP + (cons.ADJUSTED_SCORE_COLUMN,)
    fake_df = pd.DataFrame(columns=all_columns,
                           data=[["tt0014358", 7.2, 6236, "The Pilgrim", 1923, "Action, Horror", 5]])
    fake_filter_tools = cons_dev.DUMMY_SAD_FILTER_TOOLS
    with pytest.raises(ValueError):
        main.DataFilter(fake_df, fake_filter_tools)

def test_df_sort():
    fake_df=cons_dev.DUMMY_DATAFRAME_CONTENT_BAYES #with bayesian columns included
    sorted_fake_df=fake_df.sort_values(by=[cons.ADJUSTED_SCORE_COLUMN], ascending=False)
    result_df=main.DataFilter(fake_df).result
    pd.testing.assert_frame_equal(result_df, sorted_fake_df)