from constant import constants as cons

#CI

MOCK_RANDOM_URL= '127.0.0.1:8000'
MOCK_RANDOM_PATH= 'giber/'
MOCK_CONTENT_LENGTH={'Content-Length': '32768'} #dict
MOCK_DATA_COMP_BYTES=[b'compressed', b'']
MOCK_DATA_RESPONSE_BYTES=([b'a' * 8192, b'b' * 8192, b'c' * 8192, b'd' * 8192])
DUMMY_DATAFRAME_COLUMNS_ONE=[cons.IMDB_ID_COLUMN, cons.PRIMARY_TITLE_COLUMN]
DUMMY_DATAFRAME_COLUMNS_TWO=[cons.IMDB_ID_COLUMN, cons.GENRE_COLUMN]
DUMMY_DATAFRAME_DATA=[['4924', 'Shawshank Redemption'], ['2134', 'Rebellion']]
MOCK_DATAFRAME_DATA=['tt1675434', '8.5', '1027907', 'The Intouchables', '2011', 'Comedy,Drama'],['tt7286456', '8.3', '1694585', 'Joker', '2019', 'Crime,Drama,Thriller'] # noqa
DUMMY_PATH="/test/test.py"
DUMMY_DATE="29-05-1823"
DUMMY_FILTER_TOOLS={f'{cons.GENRE_COLUMN}': {'value': ['action', 'horror']}}
DUMMY_SAD_FILTER_TOOLS=[f'{cons.GENRE_COLUMN}',['action','horror']]

#unit_test_bayes
MOCK_DECAY_YEARS_OLD=cons.DECAY_FACTOR_THRESHOLD[0]
MOCK_DECAY_VALUE=cons.DECAY_FACTOR_VALUES[0]

#api
DUMMY_HASHED_PW= b"$2b$12$6Ik6AsvGpf9U3xm8aLhf8eB/fL1.EcgMauA58Mzfz5PbXLhNFmqWC"
USERS={"admin": b'$2b$12$Gy9z3lihHck5fCP4dAJMB.JzryhwuExZgHJ49GgynNW5t88hEuOLa', "robert55": b'$2b$12$AnnHZBLv63cVShZhl2OMjuUJX5fYKX4e23/LB8iWTV7aJzAHj5bxG'} # noqa
FALLBACK_DB_URL="sqlite:///lumen.db"