import ast
from typing import List
import json
import pandas as pd
import requests
from datetime import datetime, tzinfo, timedelta
from base import BaseClient
from requests import *

from models.gecko import *


class CoinGeckoClient(BaseClient):
    __base_url = 'https://api.coingecko.com/api/v3/'

    def __init__(self, base_url=__base_url):
        self.base_url = base_url

    #@property
    #def credentials(self):
    #    raise self._credentials

    @property
    def session(self):
        return Session()

    def _get_url(self, route):
        return self.base_url + route

    def ping(self):
        response = self._get(f"ping")
        return response

    # ========= SIMPLE =============

    def get_token_prices(self,
                         id: str = None,
                         contract_addresses: str = None,
                         vs_currencies: str = None,
                         include_market_cap: str = 'false',
                         include_24hr_vol: str = 'false',
                         include_24hr_change: str = 'false',
                         include_last_updated_at: str = 'false'):
        """
         Function that fetches and returns supported
         - coins id
         - name
         - symbol
                 id: str = None,
                 contract_addresses: str = None,
                 vs_currencies: str = None,
                 include_market_cap : str = 'false',
                 include_24hr_vol : str = 'false',
                 include_24hr_change : str = 'false',
                 include_last_updated_at : str = 'false'
         """
        url = f'{self.base_url}simple/token_price/{id}?&contract_addresses={contract_addresses}&vs_currencies={vs_currencies}&include_market_cap={include_market_cap}&include_24hr_vol={include_24hr_vol}&include_24hr_change={include_24hr_change}&include_last_updated_at={include_last_updated_at} '
        response = self._geturl(url)
        df = pd.DataFrame(response)
        return df

    def get_price(self, ids: str = None, vs_currencies: str = None):
        """
        Function that fetches and returns supported coins id, name and symbol
        """
        ids = ids.replace(' ', '')
        vs_currencies = vs_currencies.replace(' ', '')
        url = '{a}simple/price?ids={b}&vs_currencies={c}'.format(a=self.base_url, b=ids, c=vs_currencies)
        response = self._geturl(url)
        # prices = json.dumps([{"asset": b[0], "prices": b[1]} for b in response])
        # prices = ast.literal_eval(prices)
        # prices = list(map(lambda x: CoinGeckoPrice.from_json(**x), prices))
        return response

    # ========= COINS ==============

    def get_list(self, include_platform="false"):
        """
        Function that fetches and returns supported coins id, name and symbol

        """
        url = '{a}coins/list?{b}'.format(a=self.base_url, b=include_platform)
        response = self.session.get(url)
        content = json.loads(response.content.decode('utf-8'))
        data = list(map(lambda x: CoinGeckoList.from_json(**x), content))
        return data

    def get_markets(self, vs_currency: str = None, ids: str = None, **kwargs) -> List[CoinGeckoMarkets]:
        """
        Function that fetches and returns supported coins price, market cap, volume and market related data.

        :param
        vs_currency: The target currency of market data (usd, eur, jpy, etc.)
        ids:    The ids of the coin, comma separated cryptocurrency symbols (base). refers to /coins/list.
                When left empty, returns numbers the coins observing the params limit and start
                eg: bitcoin,etherum
        """
        ids = ids.replace(' ', '')
        url = '{a}coins/markets?vs_currency={b}&ids={c}'.format(a=self.base_url, b=vs_currency, c=ids)
        response = self._geturl(url)
        data = list(map(lambda x: CoinGeckoMarkets.from_json(**x), response))
        return data

    def get_ohlc(self, id: str = None, vs_currency: str = None, days: str = None):
        """
        Function that fetches and returns OHLC data.

        Candle's body:

            1 - 2 days: 30 minutes
            3 - 30 days: 4 hours
            31 and before: 4 days

        """
        url = '{a}coins/{b}/ohlc?vs_currency={c}&days={d}'.format(a=self.base_url, b=id, c=vs_currency, d=days)
        response = self.session.get(url)
        data = json.loads(response.content.decode('utf-8'))
        ohlc = json.dumps([{"Date": b[0], "Open": b[1], "High": b[2], "Low": b[3], "Close": b[4]} for b in data])
        data = ast.literal_eval(ohlc)
        ohlc = list(map(lambda x: CoinGeckoOHLC.from_json(**x), data))
        return ohlc

    def get_tickers_by_id(self, id: str = None, exchange_ids: str = None, **kwargs):
        """
        Function that fetches and returns Get coin tickers (paginated to 100 items).


        IMPORTANT:
        Ticker object is limited to 100 items, to get more tickers, use /coins/{id}/tickers
        Ticker is_stale is true when ticker that has not  been updated/unchanged from the exchange for a while.
        Ticker is_anomaly is true if ticker's price is outliered by our system.
        You are responsible for managing how you want to display these information
        (e.g. footnote, different background, change opacity, hide)
        """

        url = '{a}coins/{b}/tickers?exchange_ids={c}'.format(a=self.base_url, b=id, c=exchange_ids)
        response = self._geturl(url)
        data = response.get("tickers")
        data = list(map(lambda x: TickersCoin.from_json(**x), data))
        return data

    def get_market_chart_by_range(self, id: str = None, vs_currency: str = None, start: str = None,
                                  end: str = None):
        """
        Function that fetches and returns historical data by range
        """
        url = '{a}coins/{b}/market_chart/range?vs_currency={c}&from={d}&to={e}'.format(a=self.base_url, b=id,
                                                                                       c=vs_currency, d=start, e=end)
        response = self._geturl(url)
        data = [dict(zip(response, t)) for t in zip(*response.values())]
        market_chart_range = list(map(lambda x: CoinGeckoMarketChart.from_json(**x), data))

        return market_chart_range

    def get_market_chart(self, id: str = None, vs_currency: str = None, days: str = None):
        """
        Function that fetches and returns historical data (name, price, market, stats) at a given date for a coin
        """
        url = '{a}coins/{b}/market_chart?vs_currency={c}&days={d}'.format(a=self.base_url, b=id, c=vs_currency, d=days)
        response = self._geturl(url)
        data = [dict(zip(response, t)) for t in zip(*response.values())]
        market_chart = list(map(lambda x: CoinGeckoMarketChart.from_json(**x), data))
        return market_chart

    # ===== ASSET PLATFORMS ========

    def get_asset_platforms(self):
        """
        Function that fetches and returns a list of asset platforms/blockchain platforms


        """
        url = '{0}asset_platforms'.format(self.base_url)
        response = self.session.get(url)
        data = json.loads(response.content.decode('utf-8'))
        data = list(map(lambda x: CoinGeckoAssetPlatforms.from_json(**x), data))
        return data

    # ======== CATEGORIES  =========

    def get_categories(self):
        """
        Function that fetches and returns categories
        """
        response = self._get(f"coins/categories/list")
        data = list(map(lambda x: CoinGeckoCategory.from_json(**x), response))
        return data

    def get_categories_data(self):
        """
        Function that fetches and returns categories with market data
        """
        response = self._get(f"coins/categories")
        data = list(map(lambda x: CoinGeckoCategoriesData.from_json(**x), response))
        return data

    # ========= EXCHANGES  =========

    def get_exchanges(self):
        """
        Function that fetches and returns exchanges

        """
        url = '{0}exchanges'.format(self.base_url)
        response = self.session.get(url)
        data = json.loads(response.content.decode('utf-8'))
        exchanges = list(map(lambda x: CoinGeckoExchange.from_json(**x), data))
        return exchanges

    def get_exchanges_id(self):
        """
        Function that fetches and returns all supported markets id and name (no pagination required)

        :returns list of exchanges with ids and names
        """
        url = '{0}exchanges/list'.format(self.base_url)
        response = self.session.get(url)
        data = json.loads(response.content.decode('utf-8'))
        data = list(map(lambda x: CoinGeckoExchangeID.from_json(**x), data))
        return data

    def get_exchange_volume(self, id: str = None):
        """
        Function that fetches and returns exchanges volumes in BTC and tickers

        IMPORTANT:
        Ticker object is limited to 100 items, to get more tickers, use /exchanges/{id}/tickers
        Ticker is_stale is true when ticker that has not been updated/unchanged from the exchange for a while.
        Ticker is_anomaly is true if ticker's price is outliered by our system.
        You are responsible for managing how you want to display these information (e.g. footnote, different
        background, change opacity, hide)
        """
        url = '{a}exchanges/{b}'.format(a=self.base_url, b=id)
        response = self.session.get(url)
        data = json.loads(response.content.decode('utf-8'))
        volume = [{"name": data['name'], "trade_volume_24h_btc": data['trade_volume_24h_btc'],
                   "trade_volume_24h_btc_normalized": data['trade_volume_24h_btc_normalized']}]
        volume = list(map(lambda x: CoinGeckoExchangeVolume.from_json(**x), volume))
        return volume

    def get_exchange_volume_chart(self, id: str = None, days: str = None):
        """
        Function that fetches and returns exchanges volume chart data for a given exchange

        """
        url = '{a}exchanges/{b}/volume_chart?days={c}'.format(a=self.base_url, b=id, c=days)
        response = self.session.get(url)
        data = json.loads(response.content.decode('utf-8'))
        volume_chart = json.dumps([{"timestamp": b[0], "volume": b[1]} for b in data])
        data = ast.literal_eval(volume_chart)
        volume_chart = list(map(lambda x: CoinGeckVolumeChart.from_json(**x), data))
        return volume_chart

    # ========= INDEXES ===========

    def get_indexes(self):
        """
        List all markets indexes
        """
        url = '{a}indexes'.format(a=self.base_url)
        response = self.session.get(url)
        data = json.loads(response.content.decode('utf-8'))
        data = list(map(lambda x: CoinGeckoIndexes.from_json(**x), data))
        return data

    # ======== DERIVATIVES =========

    def get_derivatives_tickers(self):
        """
        List all derivative tickers
        """
        url = '{a}derivatives'.format(a=self.base_url)
        response = self.session.get(url)
        data = json.loads(response.content.decode('utf-8'))
        data = list(map(lambda x: CoinGeckoDerivativesTickers.from_json(**x), data))
        print(data)
        return data

    def get_derivatives_by_id(self, id: str = None):
        """
        Show derivative exchange data
        """
        url = '{a}derivatives/exchanges/{b}'.format(a=self.base_url, b=id)
        response = self.session.get(url)
        data = [json.loads(response.content.decode('utf-8'))]
        data = list(map(lambda x: CoinGeckoDerivativesExchangeData.from_json(**x), data))
        return data

    # ======= EXCHANGE RATE  =======

    def get_exchange_rate(self):
        """
        Function that fetches and returns BTC-to-Currency exchange rates
        """
        response = self._get(f"exchange_rates")
        for value in response.values():
            rates = value
        rates = [value for value in rates.values()]
        rates = list(map(lambda x: CoinGeckoExchangeRate.from_json(**x), rates))
        return rates

    # ========= GLOBAL ==============

    def get_global(self):
        """
        Get cryptocurrency global data
        request : https://api.coingecko.com/api/v3/global
        """
        url = 'global'
        response = self._get(url)
        for value in response.values():
            global_data = [value]
        data = list(map(lambda x: CoinGeckoGlobal.from_json(**x), global_data))
        return data

    def get_global_defi(self):
        """
        Get cryptocurrency global data
        request : https://api.coingecko.com/api/v3/global/decentralized_finance_defi
        """
        url = 'global/decentralized_finance_defi'
        response = self._get(url)
        for value in response.values():
            global_defi = [value]
        global_defi = list(map(lambda x: CoinGeckoGlobalDeFi.from_json(**x), global_defi))
        return global_defi


if __name__ == '__main__':

    ###################################
    ##  Run the different endpoinds  ##
    ###################################

    client = CoinGeckoClient()

    client.ping()
    # markets = client.get_markets(vs_currency="usd", ids="bitcoin, zuplo")
    # listcoin = client.get_list()  # Very long response list to handle for the swagger, might bug
    # categories = client.get_categories()
    # categories_data = client.get_categories_data()
    # asset_platforms = client.get_asset_platforms()
    # exchanges_id = client.get_exchanges_id()
    # tickers_by_id = client.get_tickers_by_id(id="tether", exchange_ids="binance")
    # derivatives_data = client.get_derivatives_tickers() # Very long response list to handle for the swagger, might bug
    # indexes_data = client.get_indexes()
    # ohlc = client.get_ohlc(id="bitcoin", vs_currency="usd", days=10)
    # exchanges = client.get_exchanges()
    # exchange_volume = client.get_exchange_volume(id="binance")
    # exchange_volume_price = client.get_exchange_volume_chart(id="binance", days=10)
    # exchangeRate = client.get_exchange_rate()
    # global_market = client.get_global()
    # global_defi = client.get_global_defi()
    # derivatives_data = client.get_derivatives_by_id(id = "bitmex")
    # market_chart = client.get_market_chart(id="tether", vs_currency="jpy", days=21)
    # market_chart_by_range = client.get_market_chart_by_range(id="bitcoin", vs_currency="usd", start="1392577232", end="1422577232")
    # price = client.get_price(ids="bitcoin", vs_currencies="usd")
    # price_multiple = client.get_price(ids="bitcoin,litecoin, ethereum", vs_currencies="usd, eur")  # Take on multiple inputs
    # pricecurrencies = client.get_price(ids="bitcoin", vs_currencies="usd, eur")
