import pandas, pathlib, io, pytest
from unittest.mock import MagicMock
from unittest import mock
from constant import constants_dev as cons_dev
from main import DataFilter

patcher = mock.patch

@patcher()