from dataclasses import dataclass
from datetime import datetime
from abc import ABCMeta, abstractmethod


class NestedObject(metaclass=ABCMeta):

    @abstractmethod
    def to_view(self):
        """
        this property must be implemented in subclasses
        Returns
        -------
            object
        """
        raise NotImplementedError


class Embedded(type):
    def __new__(mcs, *args):
        return super().__new__(mcs, *args)


@dataclass
class CoinGeckoMarkets:
# list all supported coins price, mkt cap, volume, and market related data

    id: str = None
    symbol: str = None
    name: str = None
    current_price: float = None
    market_cap: float = None
    market_cap_rank: int = None
    fully_diluted_valuation : float = None
    total_volume: float = None
    high_24h: float = None
    low_24h: float = None
    price_change_24h: float = None
    image: str = None
    price_change_percentage_24h: float = None
    market_cap_change_24h: float = None
    market_cap_change_percentage_24h: float = None
    circulating_supply: int = None
    total_supply:int = None
    max_supply: int = None
    ath: float = None
    ath_change_percentage: float = None
    ath_date: str = None
    atl: float = None
    atl_change_percentage: float = None
    atl_date: str = None
    roi: dict = None
    last_updated: str = None

    @classmethod
    def from_json(cls, **kwargs):
        return cls(**kwargs)


@dataclass
class CoinGeckoList:
    id: str = None
    symbol: str = None
    name: str = None

    @classmethod
    def from_json(cls, **kwargs):
        return cls(**kwargs)

    def to_view(self):
        """
        extrated the nested object in order to get a clean dataframe
        :return:
        """
        _view = {}
        for name, value in self.__dict__.items():
            if isinstance(type(value), Embedded):
                _view.update(**value.__dict__)
            else:
                _view.update({name: value})
        return _view

@dataclass
class CoinGeckoCategory:
    category_id: str = None
    name: str = None

    @classmethod
    def from_json(cls, **kwargs):
        return cls(**kwargs)


@dataclass
class CoinGeckoCategoriesData:
    id: str = None
    name: str = None
    market_cap: float = None
    market_cap_change_24h: float = None
    content: str = None
    top_3_coins: list = None
    volume_24h: float = None
    updated_at: str = None

    @classmethod
    def from_json(cls, **kwargs):
        return cls(**kwargs)

# needs tweaking
@dataclass
class CoinGeckoHistory:
    prices = None
    market_caps = None
    total_volumes = None

    @classmethod
    def from_json(cls, **kwargs):
        return cls(**kwargs)



# needs tweaking
@dataclass
class CoinGeckoOHLC:
    Date: datetime = None
    Open: float = None
    High: float = None
    Low: float = None
    Close: float = None

    def __post_init__(self):
        if isinstance(self.Date, str):
            self.Date = datetime.utcfromtimestamp(self.Date).strptime("%Y-%m-%dT%H:%M:%S.%fZ")

    @classmethod
    def from_json(cls, **kwargs):
        return cls(**kwargs)


@dataclass
class CoinGeckoPrice:
    asset: str = None
    usd: str = None

    @classmethod
    def from_json(cls, **kwargs):
        return cls(**kwargs)


@dataclass
class CoinGeckoAssetPlatforms:
    id: str = None
    chain_identifier: int = None
    name: str = None
    shortname: str = None

    @classmethod
    def from_json(cls, **kwargs):
        return cls(**kwargs)



@dataclass
class CoinGeckoExchangeRate:
    name: str = None
    unit: str = None
    value: float = None
    type: str = None

    @classmethod
    def from_json(cls, **kwargs):
        return cls(**kwargs)


@dataclass
class CoinGeckoExchange:
    id:str = None
    name:str = None
    year_established:int = None
    country:str = None
    description:str = None
    url:str = None
    image:str = None
    has_trading_incentive:bool = None
    trust_score:int = None
    trust_score_rank:int = None
    trade_volume_24h_btc:float = None
    trade_volume_24h_btc_normalized:float = None


    @classmethod
    def from_json(cls, **kwargs):
        return cls(**kwargs)



@dataclass
class CoinGeckoExchangeID:
    id:str = None
    name: str = None

    @classmethod
    def from_json(cls, **kwargs):
        return cls(**kwargs)


@dataclass
class CoinGeckoGlobal:
    active_cryptocurrencies:int = None
    upcoming_icos:int = None
    ongoing_icos:int = None
    ended_icos:int = None
    markets:int = None
    total_market_cap:dict = None
    total_volume:dict = None
    market_cap_percentage:dict = None
    market_cap_change_percentage_24h_usd:float = None
    updated_at:int = None

    @classmethod
    def from_json(cls, **kwargs):
        return cls(**kwargs)

@dataclass
class CoinGeckoGlobalDeFi:
    defi_market_cap: float = None
    eth_market_cap: float = None
    defi_to_eth_ratio: float = None
    trading_volume_24h: float = None
    defi_dominance:float = None
    top_coin_name:str = None
    top_coin_defi_dominance:float = None

    @classmethod
    def from_json(cls, **kwargs):
        return cls(**kwargs)

@dataclass
class CoinGeckoDerivativesExchangeData:
    name: str = None
    open_interest_btc: float = None
    trade_volume_24h_btc: str = None
    number_of_perpetual_pairs: int = None
    number_of_futures_pairs: int = None
    image:str = None
    year_established:str = None
    country:str = None
    description:str = None
    url:str = None


    @classmethod
    def from_json(cls, **kwargs):
        return cls(**kwargs)

@dataclass
class CoinGeckoDerivativesTickers:
    market: str = None
    symbol: float = None
    index_id: str = None
    price: str = None
    price_percentage_change_24h: float = None
    contract_type:str = None
    index:float = None
    basis:float = None
    spread:float = None
    funding_rate:float = None
    open_interest:float = None
    volume_24h:float = None
    last_traded_at:int = None
    expired_at:int = None


    @classmethod
    def from_json(cls, **kwargs):
        return cls(**kwargs)


@dataclass
class CoinGeckoIndexes:
    name:str = None
    id:str = None
    market:str = None
    last:float = None
    is_multi_asset_composite:bool = None

    @classmethod
    def from_json(cls, **kwargs):
        return cls(**kwargs)



@dataclass
class CoinGeckoMarketChart:
    prices:list = None
    market_caps:list = None
    total_volumes:list = None

    @classmethod
    def from_json(cls, **kwargs):
        return cls(**kwargs)

    def to_view(self):
        """
        extrated the nested object in order to get a clean dataframe
        :return:
        """
        _view = {}
        for name, value in self.__dict__.items():
            if isinstance(type(value), Embedded):
                _view.update(**value.__dict__)
            else:
                _view.update({name: value})
        return _view


@dataclass
class TickersCoin:
    base:str = None
    target:str = None
    market:dict = None
    last:float = None
    volume:float = None
    converted_last:dict = None
    converted_volume:dict = None
    trust_score:str = None
    bid_ask_spread_percentage:float = None
    timestamp:str = None
    last_traded_at:str = None
    last_fetch_at:str = None
    is_anomaly:bool = None
    is_stale: bool = None
    trade_url:str = None
    token_info_url: str = None
    coin_id:str = None
    target_coin_id:str = None

    @classmethod
    def from_json(cls, **kwargs):
        return cls(**{key: kwargs.get(key) for key in cls.__dict__.keys() & kwargs.keys()})




@dataclass
class CoinGeckVolumeChart:
    timestamp: str = None
    volume: float = None

    @classmethod
    def from_json(cls, **kwargs):
        return cls(**kwargs)

    def to_view(self):
        _view = {}
        for name, value in self.__dict__.items():
            if isinstance(type(value), Embedded):
                _view.update(**value.__dict__)
            else:
                _view.update({name: value})
        return _view



@dataclass
class CoinGeckoExchangeVolume:
    name: str = None
    trade_volume_24h_btc: float = None
    trade_volume_24h_btc_normalized: float = None


    @classmethod
    def from_json(cls, **kwargs):
        return cls(**kwargs)


