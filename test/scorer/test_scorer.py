import io, pytest, logging, pandas as pd
from unittest.mock import MagicMock
from constant import constants as cons
from constant import constants_dev as cons_dev
from unittest import mock
from scorer import bayesian_algorithm as bayes

logger = logging.getLogger(__name__)

def test_build_score_validify():
    """Test Bayesian scores are following business rules."""
    mock_record = cons_dev.MOCK_CONTENT_DATA[0][:5]
    mock_record.pop(3)
    mock_record[1]=float(mock_record[1])
    mock_record[2]=float(mock_record[2])
    mock_record[3]=int(mock_record[3])
    df=pd.DataFrame(data=[mock_record],columns=[cons.IMDB_ID_COLUMN, cons.AVERAGE_RATING_COLUMN, cons.NUMBER_OF_VOTES_COLUMN, cons.PUBLISHED_COLUMN])
    unit=bayes.BayesianScorer(df)
    unit.score()
    assert 0<unit.data[cons.DECAY_FACTOR_COLUMN][0]<1
    assert unit.data[cons.BAYES_SCORE_COLUMN][0]==pytest.approx(mock_record[1])
    assert unit.data[cons.ADJUSTED_SCORE_COLUMN][0]==unit.data[cons.DECAY_FACTOR_COLUMN][0]*unit.data[cons.BAYES_SCORE_COLUMN][0]