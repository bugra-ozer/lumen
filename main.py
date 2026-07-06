import bcrypt
import pandas as pd, pathlib as pl, json, logging, functools, enum, sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError, DatabaseError
from validator import validator
from logging import exception
from datetime import datetime, timezone, timedelta
from persister import state_store
from ui import cli as ui
from downloader import downloader as client
from scorer import bayesian_algorithm as scorer
from log import log_handler
from constant import constants as cons
from db.database import db, engine_standalone
from db.models import *

log_handler.LogHandler()
logger=logging.getLogger(__name__)

class DataContainer():
    """Container class own Pipeline and runs end to end until dataset is loaded."""

    def __init__(self, engine):
        self.data=pd.DataFrame()
        self.raw_data=None
        self.condition=None
        usecols=cons.CONTENT_COLUMNS_TO_KEEP_LEGACY
        self.data_pipeline=DataPipeline(engine, usecols=usecols)

    def build_container(self):
        """Orchestrates the flow of code for easy readability."""
        self.data, needs_insert=self.data_pipeline.main()
        self.raw_data=self.data #set raw dataframe before clearing main dataframe
        if needs_insert:
            self._purge_data()
            self.select_columns(*cons.CONTENT_COLUMNS_TO_KEEP)
            self.data_pipeline.insert_update_exp(self.data)

    def select_columns(self, *args:str):
        """Internal limitation the data with given columns.
        Call data to be mutated with given arguments.

        *args: Names of the columns to limit"""
        columns_to_limit=[*args]
        if len(columns_to_limit)>0:self.condition=columns_to_limit
        try:self._apply_column_selection()
        except KeyError as e:raise KeyError(f"With given arguments, column not found: {e}") from e
        return self

    def _apply_column_selection(self):
        """Based on condition, mutate the data to display"""
        if self.data is None:
            raise ValueError(cons.ERROR_APPLY_CON)
        if self and self.condition:
            self.data=self.data[self.condition]
            self.condition=None #Consume condition after applying for predictable code
        return self

    def _filter_rows(self, column:str, mask):
        """Remove unwanted records internally."""
        data:pd.DataFrame
        data=self.data[self.data[column]==mask]
        return data

    def _purge_data(self):
        """Remove excessive items with low votes, empty primary titles and genres."""
        self.data = self._filter_rows(cons.TITLE_TYPE_COLUMN, 'movie')  # remove anything else than movie in records
        self.data = self.data[(self.data[cons.PRIMARY_TITLE_COLUMN].notna()) & (self.data[cons.GENRE_COLUMN].notna()) & (self.data[cons.NUMBER_OF_VOTES_COLUMN] > 25000)]  # Purge unsuitable titles
        self.data.dropna(subset=[cons.PUBLISHED_COLUMN], inplace=True)
        return self

class DataPipeline():
    """Orchestrator class owns loader and downloader classes for external pandas dataframe operations."""

    def __init__(self, engine, usecols=None, json_cfg:tuple=(cons.DATASET_JSON,)):
        self.json_cfg=json_cfg
        self.config_dict={}
        self.engine=engine
        self.tsv_configs=[]
        self.data_loader=DataLoader(usecols)
        self.dataset_downloader=client.DatasetDownloader()

    def main(self):
        """Load file data from config and build or load the dataset."""
        self.config_dict=self.data_loader.load_config(self.json_cfg, self.config_dict)
        self._fetch_paths()
        self._convert_config_pl()
        self._setup_schema()
        db_count=self.data_loader.count_query_db(cons.TABLE_NAME_CONTENT, self.engine)
        self._download_dataset(db_count)
        return self.build_data(db_count)

    def _convert_config_pl(self):
        """Convert string paths to pathlib.Path objects."""
        for key, value in self.config_dict.items():
            if isinstance(value, dict):
                try:
                    value[cons.PATH_KEY] = pl.Path(__file__).parent / value[cons.PATH_KEY]
                except KeyError:
                    raise ValueError(f'Failed to find path for {key}')

    def _fetch_paths(self):
        """Fetch tsv file and base file paths"""
        for key, value in self.config_dict.items():
            if 'imdb' in str(key):
                self.tsv_configs.append(value)
        return self

    def _is_data_stale(self):
        """Check if base data is stale or not."""
        if pl.Path.exists((pl.Path(__file__).parent / cons.CONFIG_DIR / cons.DB_EXP_FILE)):  # check config file
            db_exp = json.load(open((pl.Path(__file__).parent / cons.CONFIG_DIR / cons.DB_EXP_FILE)))
            return datetime.now(timezone.utc)-datetime.fromisoformat(db_exp[cons.DB_EXP_JSON]) > timedelta(weeks=2)  # return boolean
        else:
            self._create_base_data_exp() # noqa
            return False

    @staticmethod
    def _update_db_exp():
        """Update base data expiry date."""
        if pl.Path.exists((pl.Path(__file__).parent / cons.CONFIG_DIR / cons.DB_EXP_FILE)):  # check config file
            base_data_exp = json.load(open((pl.Path(__file__).parent / cons.CONFIG_DIR / cons.DB_EXP_FILE), mode='r'))
            update_exp = datetime.now(timezone.utc).isoformat()
            base_data_exp[cons.DB_EXP_JSON] = update_exp
            json.dump(base_data_exp, open((pl.Path(__file__).parent / cons.CONFIG_DIR / cons.DB_EXP_FILE), 'w'))

    @staticmethod
    def _create_base_data_exp():
        """Case handling when exp file is corrupted, deleted or missing; write expiry date for consistency."""
        base_data_exp = dict()
        update_exp = datetime.now(timezone.utc).isoformat()
        base_data_exp[cons.DB_EXP_JSON] = update_exp
        json.dump(base_data_exp, open((pl.Path(__file__).parent / cons.CONFIG_DIR / cons.DB_EXP_FILE), 'w'))

    def _download_dataset(self, db_count=0):
        """Instruct DatasetDownloader to download TSVs."""
        if self.engine is None:
            raise Exception(cons.ERROR_LOAD_DB)
        elif not self.tsv_configs:
            raise Exception(cons.ERROR_LOAD_TSV_PATH)
        if db_count==0 or self._is_data_stale(): #check for base_data, if it exists and not stale skip all download dataset operation.
            if any(tsv for tsv in [*self.tsv_configs] if not pl.Path(tsv[cons.PATH_COLUMN]).exists()): #if file paths are empty orchestrate http request for dataset download.
                self.dataset_downloader.run()

    def _setup_schema(self):
        """Setup schema with given ORM architecture."""
        db.Model.metadata.create_all(self.engine)
        with self.engine.connect() as conn:
            result = conn.execute(sqlalchemy.text(f'SELECT "{cons.COLUMN_USERNAME}" FROM "{cons.TABLE_NAME_USERS}" WHERE "{cons.COLUMN_USERNAME}"=:local'), {"local": cons.USERS_LOCAL_USER}).fetchone()
            if result is None:
                conn.execute(sqlalchemy.text(f'INSERT INTO "{cons.TABLE_NAME_USERS}" ("{cons.COLUMN_USERNAME}", '
                                             f'"{cons.COLUMN_PW_HASH}", "{cons.COLUMN_ROLE}", "{cons.COLUMN_CREATED_AT}")'
                                             f' VALUES (:val1, :val2, :val3, :val4)'),
                                            {"val1": cons.USERS_LOCAL_USER, "val2": cons.PW_HASH_LOCAL_USER,
                                             "val3": cons.USER_DEFAULT_ROLE, "val4": "NOW()"})
                conn.commit()
        return self

    def build_data(self, db_count):
        """Read if processed file exists, else run operations to initiate one."""
        data_frames=[]
        if db_count != 0: #content table has data
            data,needs_insert=self.read_ready_db()
        else:
            needs_insert = True
            for tsv in self.tsv_configs:
                self._load_tsv_to_memory(data_frames, tsv)
            data=self.data_loader.merge_dataframes(*data_frames, on=cons.IMDB_ID_COLUMN_LEGACY)
            data=self.data_loader.rename_columns(data, cons.COLUMN_RENAME_DICT)
        return data, needs_insert

    def read_ready_db(self):
        """Instruct data_loader to read SQL and append to data variable."""
        needs_insert = False
        try:
            with self.engine.connect():
                logger.info(cons.INFO_LOAD_DB)
                data = self.data_loader.read_file(cons.TABLE_NAME_CONTENT, cons.STR_SQL, self.engine)
        except OperationalError:
            logger.exception(cons.ERROR_CONNECT_DB)
            raise Exception(cons.ERROR_CONNECT_DB)
        return data, needs_insert

    def _load_tsv_to_memory(self, data_frames, tsv):
        """Instruct data_loader to read TSV and append to data_frames variable."""
        logger.info(cons.INFO_MERGE_TSV)
        data_frames.append(self.data_loader.read_file(str(tsv[cons.PATH_COLUMN]), cons.STR_TSV, self.engine, usecols=tsv['usecols']))
        self.data_loader.delete_file(tsv[cons.PATH_COLUMN])
        return data_frames

    def insert_update_exp(self, data):
        """Insert to SQL engine and update exp date."""
        self.data_loader.save_file(data, cons.TABLE_NAME_CONTENT, self.engine, cons.STR_SQL)
        self._update_db_exp()

class DataLoader():
    """Pandas Dataframe and file I/O operations class without business knowledge."""

    def __init__(self, usecols=None):
        self.data=None
        self.usecols=usecols

    @staticmethod
    def merge_dataframes(*args: pd.DataFrame, on=None):
        """Merge pandas Dataframe objects.

        Args:
            *args: pandas Dataframe objects
            on: specific column to merge on"""
        if on is None:
            raise ValueError('on is required')
        result = args[0]
        if len(args) > 1:
            for i in range(1, len(args)):
                result = result.merge(args[i], on=on)
        return result

    @staticmethod
    def rename_columns(data, columns:dict):
        """Make columns in imdb .tsv files more readable and intuitive"""
        try:
            return data.rename(columns=columns)
        except KeyError as e:
            logger.exception(cons.ERROR_COLUMN_NOT_FOUND)
            raise KeyError(f"{cons.ERROR_COLUMN_NOT_FOUND} {e}") from e

    @staticmethod
    def load_config(json_cfg:tuple, config_dict:dict):
        """Load configuration file for file operations."""
        for config_file in json_cfg:
            try:
                with open(pl.Path(__file__).parent / cons.CONFIG_DIR / config_file, "r") as f:
                    config_dict.update(json.load(f))
            except ValueError:
                raise Exception('Failed to open .json config.')
            except FileNotFoundError:
                raise Exception('Failed to find .json config.')
        return config_dict

    @staticmethod
    def count_query_db(table_name, engine):
        """Check if record(s) exists in database."""
        # grab row 0 col 0, warning is for iterator type, without chunk size arg read_SQL only returns df
        try: count=pd.read_sql(sqlalchemy.text(f'SELECT COUNT(*) FROM "{table_name}"'), engine).iloc[0, 0] # noqa
        except (DatabaseError, pd.errors.DatabaseError):count=0
        return count

    @staticmethod
    def read_file(name:str, file_type:str, engine, usecols=None):
        """Read TSV file from given path

        Args:
            name: for TSV/Parquet; file path, for SQL; table name
            file_type: parquet, tsv or SQL
            engine: required for SQL reads
            usecols: columns to retain, configured in .json"""
        path=name.strip()
        if file_type != cons.STR_SQL: path=pl.Path(name)
        if file_type.strip().lower() == cons.STR_TSV:
            try:
                file = pd.read_csv(path, delimiter='\t', encoding='latin-1', on_bad_lines='skip', na_values='\\N', usecols=usecols)  # Read file
            except Exception as e:
                raise IOError(f"Failed to read {cons.STR_TSV}: {e}") from e
        elif file_type.strip().lower() == cons.STR_PARQUET:
            try:
                file = pd.read_parquet(path)  # Read file
            except Exception as e:
                raise IOError(f"Failed to read {cons.STR_PARQUET}: {e}") from e
        elif file_type.strip().lower() == cons.STR_SQL:
            try:
                file = pd.read_sql(sqlalchemy.text(f'SELECT * FROM "{path}"'), engine)  # language=SQL
            except Exception as e:
                raise IOError(f"Failed to read {cons.STR_SQL}: {e}") from e
        else:
            raise ValueError(f"Failed to read file: {path}")
        return file

    def save_file(self, file:pd.DataFrame, table_name, engine, file_type:str=cons.STR_SQL):
        """Save file to given path."""
        if file_type.strip().lower() == cons.STR_SQL:
            try:
                file.to_sql(table_name, engine, if_exists='append', index=False)
            except Exception as e:
                logger.exception(cons.ERROR_CONNECT_DB)
                raise IOError(f"{cons.ERROR_SAVE}: {e}") from e
        return self

    def delete_file(self, path):
        """Delete file with given absolute path"""
        if path.exists():
            pl.Path(path).unlink()
        return self

class DataFilter():
    """Internally selects and stores selected movies after user filter is applied."""

    def __init__(self, df:pd.DataFrame, filter_tools:dict[str,dict]=None, sort_column=cons.ADJUSTED_SCORE_COLUMN): # noqa
        self.df=df.copy()
        self.sort_column = None
        self.sort_ascending = True
        self.genres=self.df[cons.GENRE_COLUMN].str.lower().str.split(',').explode().unique()
        self.filter_tools=filter_tools
        if not validator.is_ready_structure(self.df, self.filter_tools): raise ValueError(cons.ERROR_WRONG_FILTER_OR_DF)
        self.result=self.get_movies(self.filter_tools, sort_column=sort_column)

    def get_movies(self, filter_tools, sort_column=cons.ADJUSTED_SCORE_COLUMN):
        """Retrieve list of movies with user filter applied.
        filter_tools: Filter params: column_name, operator, value
        """
        if filter_tools is None:
            self._configure_sort(sort_column, ascend=False)
            result=self._sort_candidates(self.df)
        else:
            candidates=self.apply_each_filter(filter_tools)
            self._configure_sort(sort_column, False)
            result=self._sort_candidates(candidates)
        return result
    
    @staticmethod
    def _parse_filter_tools(filter_tools:dict[str, dict]):
        """Based on the argument length, assign variables to apply filters.
        This is needed for allowing user to type in titles and genres without explicit operations."""
        local_operator=None
        for column, val_type in filter_tools.items():
                if column == cons.GENRE_COLUMN:
                    value=val_type[cons.FILTER_VALUE]
                    yield column, local_operator, value
                elif column == cons.AVERAGE_RATING_COLUMN:
                    value=val_type[cons.FILTER_VALUE]
                    local_operator=val_type[cons.FILTER_OPERATOR]
                    yield column, local_operator, value
                else:
                    raise ValueError

    def apply_each_filter(self, filter_tools:dict[str,dict]):
        """Unpacks filter tools and applies each filter in it manually."""
        candidates=self.df
        for column_name, local_operator, value in self._parse_filter_tools(filter_tools):
            candidates=self._apply_one_filter(candidates, column_name, local_operator, value)
        return candidates

    def _apply_one_filter(self, candidates, column_name:str, local_operator:str, value):
        """Apply appropriate value as filter to column_name."""
        value=self._convert_value(candidates, column_name, value)
        condition=self._build_filter(candidates, column_name, local_operator, value)
        candidates=candidates[condition]
        return candidates

    @staticmethod
    def _convert_value(candidates, column_name:str, value:str):
        """Convert value if applicable to its column's value type."""
        new_value=value
        if column_name is None:
            return value
        if pd.api.types.is_numeric_dtype(candidates[column_name]):
            try: new_value=int(value)
            except ValueError: 
                try: new_value=float(value) 
                except ValueError:
                    raise ValueError
        return new_value

    def _build_filter(self, candidates, column_name:str, operator:str, value):
        """Build pandas condition based on column, operator, and value"""
        if pd.api.types.is_numeric_dtype(candidates[column_name]):
            try:
                condition=self._apply_numeric_filter(candidates, column_name, operator, value)
            except ValueError:
                raise ValueError(f'Filter operation failed. One of the following is invalid: {column_name},{operator},{value}')
        elif value is not None:
            condition=self._apply_string_filter(candidates, column_name, value)
        else: raise ValueError(f'Operation failed. One of the following is invalid: {column_name},{operator},{value}')
        return condition

    @staticmethod
    def _apply_numeric_filter(candidates, column_name:str, operator:str, value:str):
        """Build quantitative filter"""
        condition = candidates[column_name]
        if operator == ">":
            return condition > value
        elif operator == "<":
            return condition < value
        elif operator == "<=":
            return condition <= value
        elif operator == ">=":
            return condition >= value
        elif operator == "==":
            return condition == value
        else:
            return ValueError

    @staticmethod
    def _apply_string_filter(candidates, column_name:str, value):
        """Helper function that checks data for broader string matches, not exact for qualitative filter"""
        boolean_mask=[candidates[column_name].str.lower().str.contains(genre) for genre in value]
        condition=functools.reduce(lambda x,y: x&y, boolean_mask)
        return condition
    
    def _configure_sort(self, column:str, ascend=True):
        """Set sort properties based on column parameter."""
        self.sort_ascending=ascend
        self.sort_column=column

    def _sort_candidates(self, candidates:pd.DataFrame):
        """Apply sorting properties with respect to candidates parameter."""
        if self.sort_column is not None:
            sorted_candidates=candidates.sort_values(self.sort_column, ascending=self.sort_ascending)
        else:
            sorted_candidates=candidates
        return sorted_candidates

class AppService():
    """Recommendation service that runs end to end."""

    def __init__(self, engine):
        self.picks=pd.DataFrame()
        self.engine=engine
        self.container = DataContainer(engine)
        self.container.build_container()
        self.bayes=scorer.BayesianScorer(self.container.data)
        self.bayes.score()
        self.data=self.bayes.data
        
    def run(self, filter_tools:dict[str, dict], user_id:int):
        """
        Args:
        filter_tools: nested list of filters or empty list(s)
        user_id: per session user_id, flat integer
        :return: dict of picked movies
        """
        inner_state_store = self._init_state_store(user_id)
        picks=self._orchestrate_run(inner_state_store, filter_tools, user_id)
        print(picks.to_string())
        return picks.to_dict(orient='records')

    def _pick_top(self, pool:pd.DataFrame, m:int, n:int, previous_ids):
        """
        Args:
            pool: Main subpool of movies
            m: subpool from pool
            n: amount of movies picked at random from subpool m
        Returns:
             subset DataFrame of given DataFrame
        """
        pool = self._drop_previous(previous_ids, pool, cons.IMDB_ID_COLUMN)
        if len(pool) < 1: return pool.iloc[0:0]
        elif n > len(pool): return pool.iloc[:m]
        else:
            subpool=pool.head(m)
            return subpool.sample(n)

    def decide_candidates(self, filter_tools):
        """Decides if candidates are same as df, or reduced."""
        if self._is_filter_empty(filter_tools):
            candidates = DataFilter(self.data).result
        else:
            candidates = DataFilter(self.data, filter_tools).result
        return candidates

    @staticmethod
    def _drop_previous(data, import_data:pd.DataFrame, column:str):
        """Drops previously selected movies from import_data."""
        invert_mask=~import_data[column].isin(data)
        import_data=import_data[invert_mask]
        return import_data

    @staticmethod
    def _is_filter_empty(filter_tools):
        if filter_tools is None or filter_tools == {}:
            return True
        return False

    def _orchestrate_run(self, inner_state_store:state_store.StateStore, filter_tools:dict, user_id):
        """Orchestrate end to end until self.picks is populated."""
        previous_ids = set(inner_state_store.data[cons.IMDB_ID_COLUMN])
        candidates = self.decide_candidates(filter_tools)
        picks = self._pick_top(candidates, cons.M_POOL, cons.N_POP, previous_ids)
        self._seed_state_store(inner_state_store, user_id, picks)
        picks = picks.drop(columns=[cons.DECAY_FACTOR_COLUMN, cons.BAYES_SCORE_COLUMN, cons.DATE_COLUMN, cons.ADJUSTED_SCORE_COLUMN])
        return picks

    @staticmethod
    def _seed_state_store(inner_state_store:state_store.StateStore, user_id: int, picks:pd.DataFrame):
        inner_state_store.data = picks[[cons.IMDB_ID_COLUMN, cons.DATE_COLUMN]]
        inner_state_store.data[cons.TABLE_ID_USERS] = user_id
        inner_state_store.save_to_sql()
        return inner_state_store

    def _init_state_store(self, user_id: int):
        inner_state_store = state_store.StateStore(cons.TABLE_NAME_PREVIOUS_DATA, self.engine, user_id)
        inner_state_store.manage_files()  # Load and seed previous table db
        return inner_state_store

class AppManager():
    """Main orchestrator that assembles pre-requirements for service."""
    
    def __init__(self, engine):
        self.engine=engine
        try:
            self.app_service=AppService(self.engine)
            self.cli=ui.CommandLineInterface()
            self._main()
        except Exception as e: # noqa
            logger.exception(f'Unhandled exception.')

    def _main(self):
        """Run app locally."""
        local_user_id=self.get_local_user()
        self.cli.run()
        self.filter_tools:dict[str,dict]=self.cli.all_filter_tools
        self.app_service.run(self.filter_tools, local_user_id)

    def get_local_user(self):
        with self.engine.connect() as conn:
            result=conn.execute(sqlalchemy.text(f'SELECT "{cons.TABLE_ID_USERS}" FROM "{cons.TABLE_NAME_USERS}" WHERE "{cons.COLUMN_USERNAME}"=:local'),{"local": cons.USERS_LOCAL_USER}).fetchone()
            return result[0]

if __name__ == '__main__':
    AppManager(engine_standalone)