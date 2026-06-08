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
from db.database import db, db_engine_local

log_handler.LogHandler()
logger=logging.getLogger(__name__)

class DataContainer():
    """Container class own Pipeline and runs end to end until dataset is loaded."""

    def __init__(self):
        self.data=pd.DataFrame()
        self.raw_data=None
        self.condition=None
        usecols=cons.CONTENT_COLUMNS_TO_KEEP_LEGACY
        self.data_pipeline=DataPipeline(usecols=usecols)

    def build_container(self):
        """Orchestrates the flow of code for easy readability."""
        self.data=self.data_pipeline.main()
        self.raw_data=self.data #set raw dataframe before clearing main dataframe
        self._purge_data()
        self.select_columns(*cons.CONTENT_COLUMNS_TO_KEEP)

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

    def __init__(self, usecols=None, json_cfg:tuple=(cons.DATASET_JSON,)):
        self.config_dir=cons.CONFIG_DIR
        self.json_cfg=json_cfg
        self.config_dict={}
        self.base_data_path=None
        self.tsv_configs=[]
        self.data_loader=DataLoader(usecols)
        self.dataset_downloader=client.DatasetDownloader()

    def main(self):
        """Load file data from config and build or load the dataset."""
        self._load_config()
        self._fetch_paths()
        self._convert_config_pl()
        db_count=self._count_query_db(cons.TABLE_NAME_CONTENT)
        self._download_dataset(db_count)
        return self.build_data(db_count)

    def _load_config(self):
        """Load configuration file for file operations."""
        for config_file in self.json_cfg:
            try:
                with open(pl.Path(__file__).parent / self.config_dir / config_file, "r") as f:
                    self.config_dict.update(json.load(f))
            except ValueError:
                raise Exception('Failed to open .json config.')
            except FileNotFoundError:
                raise Exception('Failed to find .json config.')
        return self

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

    @staticmethod
    def rename_columns(data, columns:dict):
        """Make columns in imdb .tsv files more readable and intuitive"""
        try:
            return data.rename(columns=columns)
        except KeyError as e:
            logger.exception(cons.ERROR_COLUMN_NOT_FOUND)
            raise KeyError(f"{cons.ERROR_COLUMN_NOT_FOUND} {e}") from e

    def _is_data_stale(self):
        """Check if base data is stale or not."""
        if pl.Path.exists((pl.Path(__file__).parent / cons.CONFIG_DIR / cons.DB_EXP_FILE)):  # check config file
            db_exp = json.load(open((pl.Path(__file__).parent / cons.CONFIG_DIR / cons.DB_EXP_FILE)))
            return datetime.now(timezone.utc)-datetime.fromisoformat(db_exp[cons.DB_EXP_JSON]) > timedelta(weeks=2)  # return boolean
        else:
            self._create_base_data_exp() # noqa

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
        if db_engine_local is None:
            raise Exception(cons.ERROR_LOAD_DB)
        elif not self.tsv_configs:
            raise Exception(cons.ERROR_LOAD_TSV_PATH)
        if db_count==0 or self._is_data_stale(): #check for base_data, if it exists and not stale skip all download dataset operation.
            if any(tsv for tsv in [*self.tsv_configs] if not pl.Path(tsv[cons.PATH_COLUMN]).exists()): #if file paths are empty orchestrate http request for dataset download.
                self.dataset_downloader.run()

    @staticmethod
    def _count_query_db(table_name):
        try: count=pd.read_sql(sqlalchemy.text(f'SELECT COUNT(*) FROM {table_name}'), db_engine_local).iloc[0, 0] #grab row 0 col 0
        except (DatabaseError, pd.errors.DatabaseError): count=0
        return count

    def build_data(self, db_count):
        """Read if processed file exists, else run operations to initiate one."""
        data_frames=[]
        if db_count != 0: #content table has data
            try:
                with db_engine_local.connect():
                    logger.info(cons.INFO_LOAD_DB)
                    data=self.data_loader.read_file(cons.TABLE_NAME_CONTENT, cons.STR_SQL)
            except OperationalError:
                logger.exception(cons.ERROR_CONNECT_DB)
                raise Exception(cons.ERROR_CONNECT_DB)
        else:
            for tsv in self.tsv_configs:
                logger.info(cons.INFO_MERGE_TSV)
                data_frames.append(self.data_loader.read_file(str(tsv[cons.PATH_COLUMN]), 'tsv', usecols=tsv['usecols']))
                self.data_loader.delete_file(tsv[cons.PATH_COLUMN])
            data=self.data_loader.merge_dataframes(*data_frames, on=cons.IMDB_ID_COLUMN_LEGACY)
            data=self.rename_columns(data, cons.COLUMN_RENAME_DICT)
            self.data_loader.save_file(data, cons.TABLE_NAME_CONTENT, cons.STR_SQL)
            self._update_db_exp()
        logger.info(cons.INFO_LOAD_DONE)
        return data

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
    def read_file(name:str, file_type:str, usecols=None):
        """Read TSV file from given path

        Args:
            name: for TSV/Parquet; file path, for SQL; table name
            file_type: parquet, tsv or SQL
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
                file = pd.read_sql(sqlalchemy.text(f'SELECT * FROM {path}'), db_engine_local)  # Read file
            except Exception as e:
                raise IOError(f"Failed to read {cons.STR_SQL}: {e}") from e
        else:
            raise ValueError(f"Failed to read file: {path}")
        return file

    def save_file(self, file:pd.DataFrame, table_name, file_type:str=cons.STR_SQL):
        """Save file to given path."""
        if file_type.strip().lower() == cons.STR_SQL:
            try:
                file.to_sql(table_name, db_engine_local, if_exists='append', index=False)
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

    def get_movies(self, filter_tools:dict[str,dict], sort_column=cons.ADJUSTED_SCORE_COLUMN):
        """Retrieve list of movies with user filter applied.
        filter_tools: Filter params: column_name, operator, value
        """
        if filter_tools is None:
            self._configure_sort(sort_column, ascend=False),
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
        operatr=None
        for column, val_type in filter_tools.items():
                if column == cons.GENRE_COLUMN:
                    value=val_type[cons.FILTER_VALUE]
                    yield column, operatr, value
                elif column == cons.AVERAGE_RATING_COLUMN:
                    value=val_type[cons.FILTER_VALUE]
                    operatr=val_type[cons.FILTER_OPERATOR]
                    yield column, operatr, value
                else:
                    raise ValueError

    def apply_each_filter(self, filter_tools:dict[str,dict]):
        """Unpacks filter tools and applies each filter in it manually."""
        candidates=self.df
        for column_name, operatr, value in self._parse_filter_tools(filter_tools):
            candidates=self._apply_one_filter(candidates, column_name, operatr, value)
        return candidates

    def _apply_one_filter(self, candidates, column_name:str, operatr:str, value):
        """Apply appropriate value as filter to column_name."""
        value=self._convert_value(candidates, column_name, value)
        condition=self._build_filter(candidates, column_name, operatr, value)
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

    def __init__(self):
        self.picks=None
        self.state_store = state_store.StateStore(cons.TABLE_NAME_PREVIOUS_DATA,db_engine_local)  #For caching
        self.state_store.load_all_files()
        self.container = DataContainer()
        self.container.build_container()
        self.previous_ids = set(self.state_store.previous_data[cons.IMDB_ID_COLUMN])
        self.bayes=scorer.BayesianScorer(self.container.data)
        self.bayes.score()
        self.data=self.bayes.data
        
    def run(self, filter_tools:dict[str, dict]):
        """
        :param filter_tools: nested list of filters or empty list(s)
        :return: list of picked movies
        """
        candidates=self.decide_candidates(filter_tools)
        self.picks=self._pick_top(candidates, cons.M_POOL, cons.N_POP)
        self.state_store.concat_file(pd.DataFrame(self.picks[[cons.IMDB_ID_COLUMN, cons.DATE_COLUMN]]))
        self.state_store.save_file()
        self.picks=self.picks.drop(columns=[cons.DECAY_FACTOR_COLUMN, cons.BAYES_SCORE_COLUMN, cons.DATE_COLUMN, cons.ADJUSTED_SCORE_COLUMN]) # noqa
        print(self.picks.to_string())
        return self.picks.to_dict(orient='records')

    def _pick_top(self, pool:pd.DataFrame, m:int, n:int):
        """
        Args:
            pool: Main subpool of movies
            m: subpool from pool
            n: amount of movies picked at random from subpool m
        Returns:
             DataFrame
        """
        if n > m > 0 >= n:
            return ValueError('Pool can not be larger than population.')
        else:
            pool = self._drop_previous(self.previous_ids, pool, cons.IMDB_ID_COLUMN)
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

class AppManager():
    """Main orchestrator that assembles pre-requirements for service."""
    
    def __init__(self):
        try:
            self.app_service=AppService()
            self.cli=ui.CommandLineInterface()
            self._main()
        except Exception as e: # noqa
            logger.exception(f'Unhandled exception.')

    def _main(self):
        """Run app locally."""
        self.cli.run()
        self.filter_tools:dict[str,dict]=self.cli.all_filter_tools
        self.app_service.run(self.filter_tools)

if __name__ == '__main__':
    AppManager()