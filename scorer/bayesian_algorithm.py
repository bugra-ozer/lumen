import datetime, pandas as pd, logging, numpy as np
from persister import state_store
from constant import constants as cons

logger=logging.getLogger(__name__)

class BayesianScorer():
    """Algorithmic class that takes transformed data, adds calculated Bayesian statistics as new columns."""
    def __init__(self, candidates:pd.DataFrame):
        self.raw_data=candidates.copy()
        self.data=candidates.copy()
        self.date=datetime.date.today()
        self._convert_dtypes()

    def score(self):
        self._build_score() #modifies self.data and adds scores as new columns
        return self

    def _convert_dtypes(self):
        """For numerical operations, convert columns to appropriate primitive type."""
        self.data[cons.NUMBER_OF_VOTES_COLUMN]=self.data[cons.NUMBER_OF_VOTES_COLUMN].astype(int)
        self.data[cons.AVERAGE_RATING_COLUMN]=self.data[cons.AVERAGE_RATING_COLUMN].astype(float)
        self.data[cons.PUBLISHED_COLUMN]=self.data[cons.PUBLISHED_COLUMN].astype(int)

    def _build_score(self):
        """Builds bayesian algorithm taking release year, number of votes and average rating into account."""
        m=self.data[cons.NUMBER_OF_VOTES_COLUMN].mean()
        c=self.data[cons.AVERAGE_RATING_COLUMN].mean()
        v=self.data[cons.NUMBER_OF_VOTES_COLUMN]
        r=self.data[cons.AVERAGE_RATING_COLUMN]
        years_old = datetime.date.today().year - (self.data[cons.PUBLISHED_COLUMN]).astype(int)
        condition_list=[years_old<years for years in cons.DECAY_FACTOR_THRESHOLD]
        choice_list=[decay_value**years_old for decay_value in cons.DECAY_FACTOR_VALUES]
        self.data[cons.BAYES_SCORE_COLUMN] = (v / (v + m)) * r + (m / (v + m) * c)
        self.data[cons.DECAY_FACTOR_COLUMN] = np.select(condition_list, choice_list ,cons.DECAY_FACTOR_THRESHOLD_DEFAULT**years_old)
        self.data[cons.ADJUSTED_SCORE_COLUMN] = self.data[cons.DECAY_FACTOR_COLUMN]*self.data[cons.BAYES_SCORE_COLUMN]
        self.data[cons.DATE_COLUMN] = self.date
        return self