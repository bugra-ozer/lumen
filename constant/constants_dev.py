from constant import constants as cons
import pandas as pd


#CI

TEST_CONTENT_COLUMNS=cons.CONTENT_COLUMNS_TO_KEEP + (cons.TITLE_TYPE_COLUMN,)
TEST_CONTENT_BAYES_COLUMNS=cons.CONTENT_COLUMNS_TO_KEEP + (cons.BAYES_SCORE_COLUMN,cons.DECAY_FACTOR_COLUMN,cons.ADJUSTED_SCORE_COLUMN,cons.DATE_COLUMN)
TEST_VALID_FILTER_TOOLS={'Genre': {'value': ['action', 'horror']}}
MOCK_RANDOM_URL= '127.0.0.1:8000'
MOCK_RANDOM_PATH= 'giber/'
MOCK_CONTENT_LENGTH={'Content-Length': '32768'} #dict
MOCK_DATA_COMP_BYTES=[b'compressed', b'']
MOCK_DATA_RESPONSE_BYTES=([b'a' * 8192, b'b' * 8192, b'c' * 8192, b'd' * 8192])
DUMMY_DATAFRAME_COLUMNS_ONE=[cons.IMDB_ID_COLUMN, cons.PRIMARY_TITLE_COLUMN]
DUMMY_DATAFRAME_COLUMNS_TWO=[cons.IMDB_ID_COLUMN, cons.GENRE_COLUMN]
DUMMY_DATAFRAME_TWO_COLUMN=[['4924', 'Shawshank Redemption'], ['2134', 'Rebellion']] #ONLY IMDB_ID and PRIMARY_TITLE
MOCK_CONTENT_DATA=['tt1675434', '8.5', '1027907', 'The Intouchables', '2011', 'Comedy,Drama'],['tt7286456', '8.3', '1694585', 'Joker', '2019', 'Crime,Drama,Thriller'] # noqa
DUMMY_DATA_PREVIOUS=[25, 1, 'tt1675412', '2026-05-04']
DUMMY_DATA_EMPTY_PREVIOUS=[None, 1, 'tt1675412', '2026-05-04']
DUMMY_USER_ID_LOCAL=1
DUMMY_RECORD_CONTENT=['tt0004972', 6.1, 28331, 'The Birth of a Nation', 2011 ,'Drama,War']
DUMMY_RECORD_CONTENT_T_TYPE=['tt0004972', 6.1, 28331, 'The Birth of a Nation', 2011 ,'Drama,War', 'movie']
DUMMY_RECORD_CONTENT_LOW_VOTE=['tt0004972', 6.1, 2331, 'The Birth of a Nation', 2011 ,'Drama,War', 'movie']
DUMMY_RECORD_CONTENT_NA_GENRE=['tt0004972', 6.1, 28331, 'The Birth of a Nation', 2011 , None, 'movie']
DUMMY_RECORD_CONTENT_NA_TITLE=['tt0004972', 6.1, 28331, None, 2011 ,'Drama,War', 'movie']
DUMMY_RECORD_CONTENT_NA_PUBLISHED=['tt0004972', 6.1, 28331, 'The Birth of a Nation', None ,'Drama,War', 'movie']
DUMMY_RECORD_CONTENT_NO_MOVIE=['tt0004972', 6.1, 28331, 'The Birth of a Nation', 2011 ,'Drama,War', 'documentary']
DUMMY_RECORD_CONTENT_BAYES_SCORE_MID=['tt0120737', 8.90000, 2214902, 'The Lord of the Rings: The Fellows', 2001, 'Adventure,Drama, Fantasy', 8.76430, 0.98388, 8.62298, '2026-07-10']
DUMMY_RECORD_CONTENT_BAYES_SCORE_LOWEST=['tt0120737', 8.90000, 2214902, 'The Lord of the Rings: The Fellows', 2001, 'Adventure,Drama, Fantasy', 6.76430, 0.98388, 6.65525, '2026-07-10']
DUMMY_RECORD_CONTENT_BAYES_SCORE_HIGHEST=['tt0120735', 8.90000, 2214902, 'The Lord of the Rings: The Fellows', 2001, 'Adventure,Drama, Fantasy', 9.76430, 0.98388, 9.60689, '2026-07-10']
DUMMY_PATH="/test/test.py"
DUMMY_DATE="29-05-1823"
DUMMY_FILTER_TOOLS={f'{cons.GENRE_COLUMN}': {'value': ['action', 'horror']}}
DUMMY_SAD_FILTER_TOOLS=[f'{cons.GENRE_COLUMN}',['action','horror']]
DUMMY_DICT_DATASET={"mock_imdb_tsv_data":{
       "name": "ratings",
       "url": "https://datasets.imdbws.com/title.ratings.tsv.gz",
       "filename": "imdb.title.ratings.tsv.gz",
       "dec_filename": "imdb.title.ratings.tsv",
       "path": "data/imdb.title.ratings.tsv",
       "folder": "data/",
       "usecols": ["tconst", "averageRating", "numVotes"]}}
DUMMY_DATAFRAME_CONTENT=pd.DataFrame(columns=cons.CONTENT_COLUMNS_TO_KEEP_LEGACY, data=[DUMMY_RECORD_CONTENT])
DUMMY_DATAFRAME_CONTENT_NEW_COLUMNS=pd.DataFrame(columns=cons.CONTENT_COLUMNS_TO_KEEP, data=[DUMMY_RECORD_CONTENT])
DUMMY_DATAFRAME_CONTENT_FAULTY=pd.DataFrame(columns=TEST_CONTENT_COLUMNS, data=[DUMMY_RECORD_CONTENT_T_TYPE, DUMMY_RECORD_CONTENT_LOW_VOTE, DUMMY_RECORD_CONTENT_NA_GENRE, DUMMY_RECORD_CONTENT_NA_TITLE, DUMMY_RECORD_CONTENT_NA_PUBLISHED, DUMMY_RECORD_CONTENT_NO_MOVIE])
DUMMY_DATAFRAME_CONTENT_BAYES=pd.DataFrame(columns=TEST_CONTENT_BAYES_COLUMNS, data=[DUMMY_RECORD_CONTENT_BAYES_SCORE_MID, DUMMY_RECORD_CONTENT_BAYES_SCORE_LOWEST, DUMMY_RECORD_CONTENT_BAYES_SCORE_HIGHEST])

#unit_test_bayes
MOCK_DECAY_YEARS_OLD=cons.DECAY_FACTOR_THRESHOLD[0]
MOCK_DECAY_VALUE=cons.DECAY_FACTOR_VALUES[0]

#api
DUMMY_HASHED_PW= b"$2b$12$6Ik6AsvGpf9U3xm8aLhf8eB/fL1.EcgMauA58Mzfz5PbXLhNFmqWC"
USERS={"admin": b'$2b$12$Gy9z3lihHck5fCP4dAJMB.JzryhwuExZgHJ49GgynNW5t88hEuOLa', "robert55": b'$2b$12$AnnHZBLv63cVShZhl2OMjuUJX5fYKX4e23/LB8iWTV7aJzAHj5bxG'} # noqa
FALLBACK_DB_URL="sqlite:///lumen.db"

#db
DUMMY_DB_URI="sqlite:///:memory:"
DUMMY_DATAFRAME_PREVIOUS=pd.DataFrame(columns=cons.TABLE_COLUMNS_PREVIOUS, data=[DUMMY_DATA_PREVIOUS])
DUMMY_DATAFRAME_MIXED_PREVIOUS=pd.DataFrame(columns=cons.TABLE_COLUMNS_PREVIOUS, data=[DUMMY_DATA_PREVIOUS, DUMMY_DATA_EMPTY_PREVIOUS])
