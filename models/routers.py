from fastapi import APIRouter

import Backtester
from geckoclient import CoinGeckoClient
from Backtester import *
from typing import Union
from pandas import Timestamp, Timedelta, read_csv
from datetime import datetime, timezone, timedelta


class CGParams:
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


class _QuoteRouter(APIRouter):
    """
    Integrate FastAPI to create our own API
    """

    def __init__(self, *args, **kwargs):
        super(_QuoteRouter, self).__init__(*args, **kwargs)
        self._prepare()

    def _prepare(self):
        @self.get("/ping", tags=self.tags)
        def get_ping() -> object:
            client = CoinGeckoClient()
            return client.ping()

        @self.get("/IndexLevel-from-Backtester", tags=self.tags)
        def Index_Level(
                id: str = "bitcoin",
                vs_currencies: str = "usd",
                days: int = 365,
                now: str = "2022-05-05",
                strategy_name: str = "CoinGecko Strategy",
                startdelta: int = 365
        ):
            CG_Params = CGParams(id=id, vs_currency=vs_currencies, days=days)
            # CG_Params = CGParams(id="zuplo", vs_currency="usd", days=365)

            now = Timestamp(Timestamp(now).date())
            config = BacktesterConfig(strategy_name=strategy_name,
                                      file_path=CG_Params,
                                      start_date=now - Timedelta(days=startdelta),
                                      end_date=now,
                                      product_codes=[CG_Params.id],
                                      frequency=Frequency.DAILY)

            backtester = Backtester(config=config)
            backtester.compute_positions().compute_levels()
            IndexLevelTS = backtester.level_by_ts
            return IndexLevelTS

        @self.get("/Quote-Backtester", tags=self.tags)
        def Quote_TS(
                id: str = "bitcoin",
                vs_currencies: str = "usd",
                days: int = 365,
                now: str = "2022-05-05",
                strategy_name: str = "CoinGecko Strategy",
                startdelta: int = 365
        ):
            CG_Params = CGParams(id=id, vs_currency=vs_currencies, days=days)
            # CG_Params = CGParams(id="zuplo", vs_currency="usd", days=365)

            now = Timestamp(Timestamp(now).date())
            config = BacktesterConfig(strategy_name=strategy_name,
                                      file_path=CG_Params,
                                      start_date=now - Timedelta(days=startdelta),
                                      end_date=now,
                                      product_codes=[CG_Params.id],
                                      frequency=Frequency.DAILY)

            backtester = Backtester(config=config)
            backtester.compute_positions().compute_levels()
            QuoteTS = backtester.quote_by_ts
            return QuoteTS

        @self.get("/{id}/{contract_addresses}/{vs_currencies}/price", tags=self.tags)
        def get_token_prices(
                id: str = None,
                contract_addresses: str = None,
                vs_currencies: str = None,
                include_market_cap: Union[str, None] = 'false',
                include_24hr_vol: Union[str, None] = 'false',
                include_24hr_change: Union[str, None] = 'false',
                include_last_updated_at: Union[str, None] = 'false'
        ):
            client = CoinGeckoClient()
            return client.get_token_prices(id,
                                           contract_addresses,
                                           vs_currencies,
                                           include_market_cap,
                                           include_24hr_vol,
                                           include_24hr_change,
                                           include_last_updated_at
                                           )

        @self.get("/list", tags=self.tags)
        def get_list(include_platform: Union[str, None] = 'false'):
            client = CoinGeckoClient()
            return client.get_list(include_platform)

        @self.get("/categories", tags=self.tags)
        def get_categories():
            client = CoinGeckoClient()
            return client.get_categories()

        @self.get("/categories-data", tags=self.tags)
        def get_categories_data():
            client = CoinGeckoClient()
            return client.get_categories_data()

        @self.get("/asset-platforms", tags=self.tags)
        def get_asset_platforms():
            client = CoinGeckoClient()
            return client.get_asset_platforms()

        @self.get("/exchanges-id", tags=self.tags)
        def get_exchanges_id():
            client = CoinGeckoClient()
            return client.get_exchanges_id()

        @self.get("/{id}/{exchange_ids}/ticket-by-id", tags=self.tags)
        def get_tickers_by_id(
                id: str = None,
                exchange_ids: str = None):
            client = CoinGeckoClient()
            return client.get_tickers_by_id(id, exchange_ids)

        @self.get("/index", tags=self.tags)
        def get_indexes():
            client = CoinGeckoClient()
            return client.get_indexes()

        @self.get("/derivatives-tickers", tags=self.tags)
        def get_derivatives_tickers():
            client = CoinGeckoClient()
            return client.get_derivatives_tickers()

        @self.get("/{id}/{vs_currency}/ohlc", tags=self.tags)
        def get_ohlc(
                id: str = None,
                vs_currency: str = None,
                days: int = 1):
            client = CoinGeckoClient()
            return client.get_ohlc(id, vs_currency, days)

        @self.get("/exchanges", tags=self.tags)
        def get_exchanges():
            client = CoinGeckoClient()
            return client.get_exchanges()

        @self.get("/{id}/exchanges-volume", tags=self.tags)
        def get_exchange_volume(id: str = None):
            client = CoinGeckoClient()
            return client.get_exchange_volume(id)

        @self.get("/{id}/{days}/exchanges-volume-chart", tags=self.tags)
        def get_exchange_volume(
                id: str,
                days: int = 10
        ):
            client = CoinGeckoClient()
            return client.get_exchange_volume_chart(id, days)

        @self.get("/exchanges-rate", tags=self.tags)
        def get_exchange_rate():
            client = CoinGeckoClient()
            return client.get_exchange_rate()

        @self.get("/global", tags=self.tags)
        def get_global():
            client = CoinGeckoClient()
            return client.get_global()

        @self.get("/global-defi", tags=self.tags)
        def get_global_defi():
            client = CoinGeckoClient()
            return client.get_global_defi()

        @self.get("/{id}/derivatives-by-id", tags=self.tags)
        def get_derivatives_by_id(id: str):
            client = CoinGeckoClient()
            return client.get_derivatives_by_id(id)

        @self.get("/{id}/{vs_currencies}/price", tags=self.tags)
        def get_price(
                id: str,
                vs_currencies: str
        ):
            client = CoinGeckoClient()
            return client.get_price(id, vs_currencies)

        @self.get("/{id}/{vs_currencies}/{days}/market-chart", tags=self.tags)
        def get_market_chart(
                id: str,
                vs_currencies: str,
                days: int = None
        ):
            client = CoinGeckoClient()
            return client.get_market_chart(id, vs_currencies, days)

        @self.get("/{id}/{vs_currencies}/{start}/{end}/market-chart-by-range", tags=self.tags)
        def get_market_chart_by_range(
                id: str = None,
                vs_currencies: str = None,
                start: str = None,
                end: str = None

        ):
            client = CoinGeckoClient()
            return client.get_market_chart_by_range(id, vs_currencies, start, end)

router = _QuoteRouter(prefix="/coingecko", tags=["endpoints"])
