#CI

MOCK_RANDOM_URL= '127.0.0.1:8000'
MOCK_RANDOM_PATH= 'giber/'
MOCK_CONTENT_LENGTH={'Content-Length': '32768'} #dict
MOCK_DATA_COMP_BYTES=[b'compressed', b'']
MOCK_DATA_RESPONSE_BYTES=([b'a' * 8192, b'b' * 8192, b'c' * 8192, b'd' * 8192])
DUMMY_DATAFRAME_COLUMNS_ONE=['IMDBid', 'Title']
DUMMY_DATAFRAME_COLUMNS_TWO=['IMDBid', 'Genre']
DUMMY_DATAFRAME_DATA=[['4924', 'Shawshank Redemption'], ['2134', 'Rebellion']]
MOCK_DATAFRAME_DATA=['tt1675434', '8.5', '1027907', 'The Intouchables', '2011', 'Comedy,Drama'],['tt7286456', '8.3', '1694585', 'Joker', '2019', 'Crime,Drama,Thriller'] # noqa
DUMMY_PATH="/test/test.py"
DUMMY_DATE="29-05-1823"
DUMMY_FILTER_TOOLS={'Genre': {'value': ['action', 'horror']}}
DUMMY_SAD_FILTER_TOOLS=['Genre',['action','horror']]