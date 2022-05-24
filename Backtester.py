from enum import Enum
from itertools import groupby
from json import dumps
from typing import List, Dict, Set, Union, Iterable, Callable, TypeVar, Type
from functools import wraps
from pandas import Timestamp, Timedelta, read_csv
from datetime import datetime, timezone, timedelta
from statistics import mean
import matplotlib as plt
import numpy as np
import pandas as pd

# Data providers libraries
from geckoclient import CoinGeckoClient # Custom CoinGecko API endpoints Wrapper

#For future integration
import investpy
import yfinance as yf

class BacktestFatalError:
    BE_STRING_TYPED_PATH = "Path should be string typed"
    BE_DICTIONARY_TYPE = "Params Should Be Dictionary Type"
    NOT_ENOUGH_PRICES = "Need to get more than 1 quote to compute returns"
    BE_STRING_TYPED = "Param should be string typed"


class BacktestError:
    pass


class Provider(Enum):
    """
    Enumeration of data provider for config parameters and future dynamic integration
    """
    YAHOO = "YAHOO"
    COINGECKO = "CoinGecko"
    CRYPTOCOMPARE = "CryptoCompare"
    INVESTPY = "InvestPy"
    COINMARKETCAP = "CoinMarketCap"


def super_method(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            target_func = getattr(super(type(self), self), func.__name__)
            if callable(target_func):
                return target_func(*args, **kwargs)
            else:
                raise TypeError(f'{func.__name__} must be callable')
        except AttributeError:
            raise AttributeError(f"{func.__name__} has not been implemented")

    return wrapper


class Frequency(Enum):
    """
    Enumeration of different data aggregation frequency for config parameters
    """
    HOURLY = "HOURLY"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"


class Calendar(object):
    """
    class Calendar to manage time for computation, start and end dates
    """
    def __init__(
            self,
            start_date: Timestamp,
            end_date: Timestamp,
            frequency: Frequency
    ):
        self._start_date = start_date
        self._end_date = end_date
        self._frequency = frequency
        self._time_delta = None

    def compute_calendar(self) -> List[Timestamp]:
        self._compute_time_delta()
        temp = self._start_date
        _calendar = list()
        while temp <= self._end_date:
            _calendar.append(temp)
            temp += self._time_delta
        return _calendar

    def _compute_time_delta(self):
        if self._frequency == Frequency.DAILY:
            self._time_delta = Timedelta(days=1)
        if self._frequency == Frequency.HOURLY:
            self._time_delta = Timedelta(hours=1)
        if self._frequency == Frequency.WEEKLY:
            self._time_delta = Timedelta(days=7)


class CGParams:
    """
    class for CoinGecko parameters
    """
    def __init__(self,
                 id: str = None,
                 vs_currency: str = None,
                 days: int = None
                 ):
        self.id = id
        self.vs_currency = vs_currency
        self.days = days

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return repr(self)


class BacktesterConfig(object):
    """
    class to configurate Backtester before passing it from the __main__
    """
    def __init__(
            self,
            strategy_name: str,
            file_path: CGParams,
            start_date: Timestamp,
            end_date: Timestamp,
            product_codes: List[str],
            frequency: Frequency = Frequency.DAILY
    ):
        self._strategy_name = strategy_name
        self._file_path = file_path
        self._start_date = start_date
        self._end_date = end_date
        self._product_codes = product_codes
        self._frequency = frequency

    @property
    def strategy_name(self):
        """
        :return: strategy name
        """
        return self._strategy_name

    @property
    def file_path(self) -> str:
        return self._file_path

    @property
    def start_date(self) -> Timestamp:
        return self._start_date

    @start_date.setter
    def start_date(self, _start_date: Timestamp):
        self._start_date = _start_date

    @property
    def end_date(self) -> Timestamp:
        return self._end_date

    @end_date.setter
    def end_date(self, _end_date: Timestamp):
        self._end_date = _end_date

    @property
    def frequency(self) -> Frequency:
        return self._frequency

    @property
    def product_code(self) -> List[str]:
        return self._product_codes


class Data:
    def __repr__(self):
        kwargs = [f"{key}={value!r}" for key, value in self.__dict__.items() if key[0] != "_" or key[:2] != "__"]
        return "{}({})".format(type(self).__name__, "".join(kwargs))


class QuoteKey(Data):
    """
    class QuoteKey used as a primary key to identify Quotes: We give a set of product codes and timestamps to get a unique id
    """
    def __init__(
            self,
            product_code: str,
            ts: Timestamp
    ):
        self._product_code = product_code
        self._ts = ts

    @property
    def product_code(self):
        return self._product_code

    @property
    def ts(self):
        return self._ts

    def __repr__(self):
        return "QuoteKey{"f'product_code={self.product_code},' \
               f'ts={self.ts}' + "}"

    def __lt__(self, other):
        return self.ts < other.ts

    def __le__(self, other):
        return self.ts <= other.ts

    def __gt__(self, other):
        return self.ts > other.ts

    def __ge__(self, other):
        return self.ts >= other.ts

    def __eq__(self, other):
        return self.product_code == other.product_code and self.ts == other.ts if isinstance(other,
                                                                                             self.__class__) else False

    def __ne__(self, other):
        return self.product_code != other.product_code or self.ts != other.ts if isinstance(other,
                                                                                            self.__class__) else True

    def __hash__(self):
        return hash((self.product_code, self.ts))


class Quote(Data):
    """
    class Quote:
    key from class QuoteKey
    """
    def __init__(
            self,
            key: QuoteKey = None,
            open: float = None,
            high: float = None,
            low: float = None,
            close: float = None
    ):
        self._key = key
        self._open = open
        self._high = high
        self._low = low
        self._close = close

    @property
    def key(self):
        return self._key

    @property
    def open(self):
        return self._open

    @property
    def high(self):
        return self._high

    @property
    def low(self):
        return self._low

    @property
    def close(self):
        return self._close

    def __repr__(self):
        return "Quote{"f'key={self.key},' \
               f'open={self.open},' \
               f'high={self.high},' \
               f'low={self.low},' \
               f'close={self.close}' + "}"

    def __lt__(self, other):
        return self.key < other.key

    def __le__(self, other):
        return self.key <= other.key

    def __gt__(self, other):
        return self.key > other.key

    def __ge__(self, other):
        return self.key >= other.key

    def __hash__(self):
        return hash(self.key)

    @classmethod
    def from_dict(cls, dict_object: dict):
        """
        TO DO : Make product_code dynamic
        :param dict_object:
        :return: key=QuoteKey{product_code=GLE.PA,ts=2017-04-25 00:00:00},open=50.91,high=51.459,low=50.361,close=50.91}
        """
        return cls(key=QuoteKey(product_code="product_code", ts=Timestamp(dict_object["Date"])),
                   open=dict_object["Open"],
                   high=dict_object["High"],
                   low=dict_object["Low"],
                   close=dict_object["Close"])


class QuoteDataFactory(object):

    @staticmethod
    def group_by(iterable: Iterable, key_func: Callable[[Quote], str]):
        return {_indexer: set(_grouper) for _indexer, _grouper in groupby(sorted(iterable, reverse=True), key=key_func)}


def read_csv_file(file_name: str) -> List[dict]:
    """
    read and structure the data read from a csv
    :param file_name:
    :return: List of dictionary
    """
    return list(read_csv(file_name).to_dict(orient='index').values())


def ohlc_CoinGecko(id: str = None, vs_currency: str = None, days: str = None):
    client = CoinGeckoClient()
    return client.get_ohlc(id, vs_currency, days)


def load_quote(file_name: str):
    """
    Function reading a CSV file from the read_csv_file function
    To do : give the file an opportunity to read from yahoofinance straight or other data providers
    :param file_name:str
    :return: list of mapping from the class Quote returning a Quote object
    """
    _dict_data = read_csv_file(file_name)
    return list(map(lambda _dict: Quote.from_dict(dict_object=_dict), _dict_data))


def load_quote_CG(CGParams):
    """
    :param CGParams:
                        id: str = None,
                        vs_currency: str= None,
                        days: int = None
    :return: list of mapping from the class Quote returning a Quote object
    """
    _dict_data = ohlc_CoinGecko(id = CGParams.id, vs_currency=CGParams.vs_currency, days=CGParams.days)
    _dict_data = pd.DataFrame(_dict_data)
    _dict_data['Date'] = pd.to_datetime(_dict_data['Date'], unit='ms')
    _dict_data = list(_dict_data.to_dict(orient='index').values())
    _dict_data = list(map(lambda _dict: Quote.from_dict(dict_object=_dict), _dict_data))
    return _dict_data


def print_close(quotes: List[Quote]):
    """
    function printing a list of closing quotes
    :param quotes:
    :return: ts:{quote.key.ts} close:{quote.close}
    """
    for quote in quotes:
        print(f"ts:{quote.key.ts} close:{quote.close}")


class WeightId(Data):
    """
    WeightID : primary key for the weight
    """
    def __init__(self, strategy_code, underlying_code, dt: datetime):
        self.strategy_code = strategy_code
        self.underlying_code = underlying_code
        self.dt = dt

    def __hash__(self):
        return hash((self.strategy_code, self.underlying_code, self.dt))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__ if isinstance(other, self.__class__) else False

    def __gt__(self, other):
        return self.dt > other.dt if isinstance(other, self.__class__) else False

    def __ge__(self, other):
        return self.dt >= other.dt if isinstance(other, self.__class__) else False

    def __lt__(self, other):
        return self.dt < other.dt if isinstance(other, self.__class__) else False

    def __le__(self, other):
        return self.dt <= other.dt if isinstance(other, self.__class__) else False


class Weight(Data):
    """
    class Weight using the primary key from WeightID
    This class is used to create a object containing our model list of weight for signal generation
    """
    def __init__(self, id: WeightId, value: float):
        self.id = id
        self.value = value

    def __hash__(self):
        return hash((self.id))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__ if isinstance(other, self.__class__) else False

    def __gt__(self, other):
        return self.id > other.id if isinstance(other, self.__class__) else False

    def __ge__(self, other):
        return self.id >= other.id if isinstance(other, self.__class__) else False

    def __lt__(self, other):
        return self.id < other.id if isinstance(other, self.__class__) else False

    def __le__(self, other):
        return self.id <= other.id if isinstance(other, self.__class__) else False


class PositionKey(Data):
    """
    class PositionKey : primary key of the position class, same use case as QuoteID and WeightID
    """
    def __init__(self, product_code: str, underlying_code: str, ts: Timestamp):
        self._product_code = product_code
        self._underlying_code = underlying_code
        self._ts = ts

    @property
    def product_code(self) -> str:
        return self._product_code

    @property
    def underlying_code(self) -> str:
        return self._underlying_code

    @property
    def ts(self) -> Timestamp:
        return self._ts

    def __hash__(self):
        return hash((self.product_code, self.underlying_code, self.ts))

    def __eq__(self, other):
        return self.product_code == other.product_code and self.underlying_code == other.underlying_code and self.ts == other.ts if isinstance(
            other, self.__class__) else False

    def __ne__(self, other):
        return self.product_code != other.product_code or self.underlying_code != other.underlying_code or self.ts != other.ts if isinstance(
            other, self.__class__) else True

    def __le__(self, other):
        return self.ts <= other.ts

    def __ge__(self, other):
        return self.ts >= other.ts

    def __lt__(self, other):
        return self.ts < other.ts

    def __gt__(self, other):
        return self.ts > other.ts


class Position(Data):
    """
    class position using the primary key from PositionID
    This class is used to create a object containing our model list of position for position generation
    """
    def __init__(self, key: PositionKey, value: float):
        self._key = key
        self._value = value

    @property
    def key(self) -> PositionKey:
        return self._key

    @key.setter
    def key(self, _key: PositionKey):
        self._key = _key

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, _value: float):
        self._value = _value

    @classmethod
    def from_dict(cls, dict_object: dict):
        if not isinstance(dict_object, dict):
            raise TypeError(f"dict_object should be dict current type is : {dict_object}")
        return cls(
            key=PositionKey(product_code=dict_object["product_code"],
                            underlying_code=dict_object["underlying_code"],
                            ts=dict_object["ts"]),
            value=dict_object["value"]
        )

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        return self.key == other.key if isinstance(other, self.__class__) else False

    def __ne__(self, other):
        return self.key != other.key if isinstance(other, self.__class__) else True

    def __le__(self, other):
        return self.key <= other.key

    def __ge__(self, other):
        return self.key >= other.key

    def __lt__(self, other):
        return self.key < other.key

    def __gt__(self, other):
        return self.key > other.key


class PositionDisplay:
    """
    Display position
    """
    def __init__(
            self,
            product_code: str,
            underlying_code: str,
            ts: Union[str, Timestamp],
            value: float,
    ):
        self._product_code = product_code
        self._underlying_code = underlying_code
        self._ts = ts
        self._value = value

    @property
    def product_code(self) -> str:
        return self._product_code

    @property
    def underlying_code(self) -> str:
        return self._underlying_code

    @property
    def ts(self) -> Timestamp:
        return self._ts

    @property
    def value(self):
        return self._value

    @classmethod
    def from_model(
            cls,
            position: Position
    ):
        if not isinstance(position, Position):
            raise TypeError(f"object should be Position current type is : {position}")

        return cls(
            product_code=position.key.product_code,
            underlying_code=position.key.underlying_code,
            ts=position.key.ts,
            value=position.value,
        )

    @property
    def json(self):
        self._ts = self.ts.strftime("%Y-%m-%dT%H:%M:%S")
        return dumps(vars(self))


class PositionFactory(object):

    @staticmethod
    def to_views(positions: List[Position]) -> List[PositionDisplay]:
        """
        This function will convert Position to PositionView for display
        :param quotes:
        :return:
        """
        [PositionFactory.to_view(position) for position in positions]
        return list(map(lambda position: PositionFactory.to_view(position), positions))

    @staticmethod
    def to_view(
            position: Position
    ) -> PositionDisplay:
        """
        This function will convert Position to PositionView for display
        :param quotes:
        :return:
        """
        return PositionDisplay.from_model(position)

    @staticmethod
    def group_by(iterable: Iterable, key_func: Callable[[Position], str]):
        return {_indexer: set(_grouper) for _indexer, _grouper in groupby(sorted(iterable, reverse=True), key=key_func)}


class ModelParameters:
    """
    class ModelParameters use case similar to Backtester Parameters but we configure what we use for our Model generating
    list of Weight
    """
    def __init__(self,
                 start_ts: datetime,
                 end_ts: datetime,
                 strategy_code: str,
                 underlying_code: List[str],
                 frequency: Frequency
                 ):
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.strategy_code = strategy_code
        self.underlying_code = underlying_code
        self.frequency = frequency


class MovingAverage(ModelParameters):
    """"
    Class inheriting from ModelParameters config parameters
    """

    def __init__(
            self,
            short_ma: int,
            long_ma: int,
            *args,
            **kwargs
    ):
        self.short_ma = short_ma
        self.long_ma = long_ma
        super(MovingAverage, self).__init__(*args, **kwargs)

    def __call__(self, weight_list: None, *args, **kwargs):
        """
        to be updated
        :param args:
        :param kwargs:
        :return:

        Weight = {}  # creating empty Weight dictionary
        for weight_dict in weight_list:
            Weight.append(self.to_weight)
        """
        pass



class Model:
    """
    class Model with use case similar to class Backtester : used as a initializer
    """
    pass


class SignalGenerator:
    """
    class used to get a signal -> determines the weights based on a determined strategy
    this class has to come before the backtester class because we send a list of weights to the backtester
    input : list of quote from the data loader
    return : list of weights used in the backtester
    """
    pass


class CalendarBuilder(object):

    @staticmethod
    def from_config(config: BacktesterConfig) -> List[Timestamp]:
        return Calendar(
            start_date=config.start_date,
            end_date=config.end_date,
            frequency=config.frequency
        ).compute_calendar()


class Backtester(object):
    def __init__(self, config: BacktesterConfig):
        self._config = config
        self._calendar = None
        self._position_by_ts = dict()
        self._position_by_key = dict()
        self._quote_by_key = dict()
        self._quote_by_ts = dict()
        self._level_by_ts = dict()
        self._underlying_codes = list()
        Backtester.__post_init__(self)

    @property
    def underlyings_codes(self) -> List[str]:
        return self._underlying_codes

    @property
    def level_by_ts(self) -> Dict[Timestamp, Quote]:
        return self._level_by_ts

    @property
    def position_by_key(self) -> Dict[PositionKey, Position]:
        return self._position_by_key

    @property
    def position_by_ts(self):
        return self._position_by_ts

    @property
    def quote_by_key(self) -> Dict[QuoteKey, Quote]:
        return self._quote_by_key

    @property
    def quote_by_ts(self) -> Dict[Timestamp, Set[Quote]]:
        return self._quote_by_ts

    @property
    def calendar(self) -> List[Timestamp]:
        return self._calendar

    @calendar.setter
    def calendar(self, _calendar: List[Timestamp]):
        self._calendar = _calendar

    @property
    def config(self) -> BacktesterConfig:
        return self._config

    def __post_init__(self):
        self.calendar = CalendarBuilder.from_config(self.config)
        self._load_quotes()
        self._load_underlying_codes()
        self._update_calendar()

    def _load_underlying_codes(self):
        self._underlying_codes = list(set(map(lambda quote: quote.key.product_code, self.quote_by_key.values())))

    def _update_calendar(self):
        self._calendar = sorted(set(self.calendar).intersection(set(self.quote_by_ts.keys())))
        self.config.start_date = min(self.calendar)
        self.config.end_date = max(self.calendar)

    def _load_quotes(self):
        quotes = load_quote_CG(CGParams=self.config.file_path)
        #quotes = load_quote(file_name=self.config.file_path)
        self._quote_by_ts = QuoteDataFactory.group_by(quotes, lambda quote: quote.key.ts)
        self._quote_by_key = {quote.key: quote for quote in quotes}

    def compute_positions(self):
        for ts in self.calendar:
            quotes_set = self.quote_by_ts.get(ts)
            """
            Example of quotes_set object
            quote_set = {
                Quote(id=QuoteId("AAPL", datetime.now(timezone.utc), Provider.YAHOO), close=100),
                Quote(id=QuoteId("AAPL", datetime.now(timezone.utc), Provider.YAHOO), close=101)
            }
            """
            nb_components = len(quotes_set)
            for quote in quotes_set:
                key = PositionKey(product_code=self.config.strategy_name, underlying_code=quote.key.product_code, ts=ts)
                self.position_by_key[key] = Position(key, value=1 / nb_components)

        self._position_by_ts = PositionFactory.group_by(self.position_by_key.values(), lambda position: position.key.ts)
        return self

    def compute_levels(self, basis: int = 100):
        """
        Compute levels from yahoo finance
        -> only close supported yet
        to do : adapt for the other time of data we can read from API endpoints and csv files
        :param basis:
        :return: Quote(QuoteKey(product_code=self.config.strategy_name, ts=ts), close=value_of_strat)
        """
        for index in range(len(self.calendar)):
            ts: Timestamp = self.calendar[index]
            if ts == self.config.start_date:
                key = QuoteKey(product_code=self.config.strategy_name, ts=ts)
                self.level_by_ts[ts] = Quote(key, close=basis)
            else:
                for underlying_code in self.underlyings_codes:
                    _previous_ts: Timestamp = self.calendar[index - 1]
                    _previous_position_key = PositionKey(product_code=self.config.strategy_name,
                                                         underlying_code=underlying_code,
                                                         ts=_previous_ts
                                                         )

                    _previous_quote_key = QuoteKey(product_code=underlying_code, ts=_previous_ts)
                    _current_quote_key = QuoteKey(product_code=underlying_code, ts=ts)
                    _perf = self.position_by_key.get(_previous_position_key).value * (
                            self.quote_by_key.get(_current_quote_key).close / self.quote_by_key.get(
                        _previous_quote_key).close - 1)

                    value_of_strat = self.level_by_ts.get(_previous_ts).close * (1 + _perf)
                    self.level_by_ts[ts] = Quote(QuoteKey(product_code=self.config.strategy_name, ts=ts),
                                                 close=value_of_strat)

    def _compute_performance(
            self,
            ts: Timestamp, previous_positions: List[Position],
            current_quotes: List[Quote],
            previous_quotes: List[Quote]
    ) -> float:

        pass

    def _compute_time_delta(self):
        if self.config.frequency == Frequency.DAILY:
            return Timedelta(days=1)
        if self.config.frequency == Frequency.HOURLY:
            return Timedelta(hours=1)
        if self.config.frequency == Frequency.WEEKLY:
            return Timedelta(days=7)


class KPI:
    """
    class KPI used to compute standardised computation for our strategies
    """
    def __init__(
            self,
            quote: Quote
    ):
        self.quote = quote

    def StrategyReturn(self):
        pass

    def SharpeRatio(self):
        pass

    def plot_ret(self):
        '''
        self.backtest.returns.plot()
        plt.show()
        '''
        raise NotImplemented

    def plot_prices(self):
        '''
        self.backtest.levels.plot()
        plt.show()
        '''
        raise NotImplemented


if __name__ == '__main__':

    CG_Params = CGParams(id="bitcoin", vs_currency="usd", days=365)
    #CG_Params = CGParams(id="zuplo", vs_currency="usd", days=365)

    now = Timestamp(Timestamp("2022-05-05").date())
    config = BacktesterConfig(strategy_name=f"CoinGecko {CG_Params.id} Index",
                              file_path=CG_Params,
                              start_date=now - Timedelta(days=365),
                              end_date=now,
                              product_codes=[CG_Params.id],
                              frequency=Frequency.DAILY
                              )

    """
    Print Quotes we get from the custom API client from CoinGecko
    Print Index levels with 100 as a base index
    """

    backtester = Backtester(config=config)
    backtester.compute_positions().compute_levels()
    QuoteTS = {print(value) for value in backtester.quote_by_ts.values()}
    IndexLevelTS = {print(value) for value in backtester.level_by_ts.values()}

