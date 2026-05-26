import io, main, pytest, pandas as pd, pathlib as pl
from validator import validator
from unittest import mock
from unittest.mock import MagicMock
from constant import constants_dev as cons_dev, constants as cons

patch=mock.patch

def test_happy_path():
    all_columns=cons.COLUMNS_TO_KEEP+(cons.ADJUSTED_SCORE_COLUMN,)
    fake_df=pd.DataFrame(columns=all_columns, data=[["tt0014358",7.2,6236,"The Pilgrim",1923,"Action, Horror",5]])
    fake_filter_tools={'Genre': {'value': ['action', 'horror']}}
    unit=main.DataFilter(fake_df, fake_filter_tools)
    assert validator.is_ready_structure(fake_df, fake_filter_tools) and len(unit.result)>=1