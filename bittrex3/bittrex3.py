"""
   See https://bittrex.com/Home/Api
"""

import urllib.parse
import time
import hmac
import hashlib
from decimal import Decimal
import json
import requests

BUY_ORDERBOOK = 'buy'
SELL_ORDERBOOK = 'sell'
BOTH_ORDERBOOK = 'both'

# API v1.1
PUBLIC_SET = ['getmarkets', 'getcurrencies', 'getticker', 'getmarketsummaries', 'getorderbook',
              'getmarkethistory']

MARKET_SET = ['getopenorders', 'cancel', 'sellmarket', 'selllimit', 'buymarket', 'buylimit']

ACCOUNT_SET = ['getbalances', 'getbalance', 'getdepositaddress', 'withdraw', 'getorder', 'getorderhistory',
               'getwithdrawalhistory', 'getdeposithistory']

# API v2.0
MARKET_SET_2 = ['GetTicks', 'GetLatestTick']

class Bittrex3(object):
    """
    Used for requesting Bittrex with API key and API secret

    (Limited Bittrex API v2.0 support)
    """

    def __init__(self, api_key, api_secret):
        self.api_key = str(api_key) if api_key is not None else ''
        self.api_secret = str(api_secret) if api_secret is not None else ''
        self.public_set = set(PUBLIC_SET)
        self.market_set = set(MARKET_SET)
        self.account_set = set(ACCOUNT_SET)
        self.market_set_2 = set(MARKET_SET_2)

    def api_query(self, method, options=None):
        """
        Queries Bittrex with given method and options

        :param method: Query method for getting info
        :type method: str

        :param options: Extra options for query
        :type options: dict

        :return: JSON response from Bittrex
        :rtype : dict
        """
        if not options:
            options = {}
        nonce = str(int(time.time() * 1000))
        if method in self.market_set_2:
            base_url = 'https://bittrex.com/Api/v2.0/pub/%s/'
        else:
            base_url = 'https://bittrex.com/api/v1.1/%s/'
        request_url = ''

        if method in self.public_set:
            request_url = (base_url % 'public') + method + '?'
        elif method in self.market_set:
            request_url = (base_url % 'market') + method + '?apikey=' + self.api_key + "&nonce=" + nonce + '&'
        elif method in self.account_set:
            request_url = (base_url % 'account') + method + '?apikey=' + self.api_key + "&nonce=" + nonce + '&'
        elif method in self.market_set_2:
            request_url = (base_url % 'market') + method + '?'

        request_url += urllib.parse.urlencode(options)

        signature = hmac.new(self.api_secret.encode(), request_url.encode(), hashlib.sha512).hexdigest()

        headers = {"apisign": signature}

        sresponse = requests.get(request_url, headers=headers).content.decode('utf-8')
        return json.loads(sresponse, parse_float=Decimal, parse_int=Decimal)

    def get_markets(self):
        """
        Used to get the open and available trading markets
        at Bittrex along with other meta data.

        :return: Available market info in JSON
        :rtype : dict
        """
        return self.api_query('getmarkets')

    def get_currencies(self):
        """
        Used to get all supported currencies at Bittrex
        along with other meta data.

        :return: Supported currencies info in JSON
        :rtype : dict
        """
        return self.api_query('getcurrencies')

    def get_ticker(self, market):
        """
        Used to get the current tick values for a market.

        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str

        :return: Current values for given market in JSON
        :rtype : dict
        """
        return self.api_query('getticker', {'market': market})

    def get_market_summaries(self):
        """
        Used to get the last 24 hour summary of all active exchanges

        :return: Summaries of active exchanges in JSON
        :rtype : dict
        """
        return self.api_query('getmarketsummaries')

    def get_orderbook(self, market, depth_type, depth=20):
        """
        Used to get retrieve the orderbook for a given market

        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str

        :param depth_type: buy, sell or both to identify the type of orderbook to return.
            Use constants BUY_ORDERBOOK, SELL_ORDERBOOK, BOTH_ORDERBOOK
        :type depth_type: str

        :param depth: how deep of an order book to retrieve. Max is 100, default is 20
        :type depth: int

        :return: Orderbook of market in JSON
        :rtype : dict
        """
        return self.api_query('getorderbook', {'market': market, 'type': depth_type, 'depth': depth})

    def get_market_history(self, market, count):
        """
        Used to retrieve the latest trades that have occured for a
        specific market.

        /market/getmarkethistory

        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str

        :param count: Number between 1-100 for the number of entries to return (default = 20)
        :type count: int

        :return: Market history in JSON
        :rtype : dict
        """
        return self.api_query('getmarkethistory', {'market': market, 'count': count})

    def buy_market(self, market, quantity, rate):
        """
        Used to place a buy order in a specific market. Use buymarket to
        place market orders. Make sure you have the proper permissions
        set on your API keys for this call to work

        /market/buymarket

        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str

        :param quantity: The amount to purchase
        :type quantity: float

        :param rate: The rate at which to place the order.
            This is not needed for market orders
        :type rate: float

        :return:
        :rtype : dict
        """
        return self.api_query('buymarket', {'market': market, 'quantity': quantity, 'rate': rate})

    def buy_limit(self, market, quantity, rate):
        """
        Used to place a buy order in a specific market. Use buylimit to place
        limit orders Make sure you have the proper permissions set on your
        API keys for this call to work

        /market/buylimit

        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str

        :param quantity: The amount to purchase
        :type quantity: float

        :param rate: The rate at which to place the order.
            This is not needed for market orders
        :type rate: float

        :return:
        :rtype : dict
        """
        return self.api_query('buylimit', {'market': market, 'quantity': quantity, 'rate': rate})

    def sell_market(self, market, quantity, rate):
        """
        Used to place a sell order in a specific market. Use sellmarket to place
        market orders. Make sure you have the proper permissions set on your
        API keys for this call to work

        /market/sellmarket

        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str

        :param quantity: The amount to purchase
        :type quantity: float

        :param rate: The rate at which to place the order.
            This is not needed for market orders
        :type rate: float

        :return:
        :rtype : dict
        """
        return self.api_query('sellmarket', {'market': market, 'quantity': quantity, 'rate': rate})

    def sell_limit(self, market, quantity, rate):
        """
        Used to place a sell order in a specific market. Use selllimit to place
        limit orders Make sure you have the proper permissions set on your
        API keys for this call to work

        /market/selllimit

        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str

        :param quantity: The amount to purchase
        :type quantity: float

        :param rate: The rate at which to place the order.
            This is not needed for market orders
        :type rate: float

        :return:
        :rtype : dict
        """
        return self.api_query('selllimit', {'market': market, 'quantity': quantity, 'rate': rate})

    def cancel(self, uuid):
        """
        Used to cancel a buy or sell order

        /market/cancel

        :param uuid: uuid of buy or sell order
        :type uuid: str

        :return:
        :rtype : dict
        """
        return self.api_query('cancel', {'uuid': uuid})

    def get_open_orders(self, market):
        """
        Get all orders that you currently have opened. A specific market can be requested

        /market/getopenorders

        :param market: String literal for the market (ie. BTC-LTC)
        :type market: str

        :return: Open orders info in JSON
        :rtype : dict
        """
        return self.api_query('getopenorders', {'market': market})

    def get_balances(self):
        """
        Used to retrieve all balances from your account

        /account/getbalances

        :return: Balances info in JSON
        :rtype : dict
        """
        return self.api_query('getbalances', {})

    def get_balance(self, currency):
        """
        Used to retrieve the balance from your account for a specific currency

        /account/getbalance

        :param currency: String literal for the currency (ex: LTC)
        :type currency: str

        :return: Balance info in JSON
        :rtype : dict
        """
        return self.api_query('getbalance', {'currency': currency})

    def get_deposit_address(self, currency):
        """
        Used to generate or retrieve an address for a specific currency

        /account/getdepositaddress

        :param currency: String literal for the currency (ie. BTC)
        :type currency: str

        :return: Address info in JSON
        :rtype : dict
        """
        return self.api_query('getdepositaddress', {'currency': currency})

    def withdraw(self, currency, quantity, address):
        """
        Used to withdraw funds from your account

        /account/withdraw

        :param currency: String literal for the currency (ie. BTC)
        :type currency: str

        :param quantity: The quantity of coins to withdraw
        :type quantity: float

        :param address: The address where to send the funds.
        :type address: str

        :return:
        :rtype : dict
        """
        return self.api_query('withdraw', {'currency': currency, 'quantity': quantity, 'address': address})

    def get_order(self, uuid):
        """
        Used to get an order from your account

        /account/getorder

        :param uuid: The order UUID to look for
        :type uuid: str

        :return:
        :rtype : dict
        """
        return self.api_query('getorder', {'uuid': uuid})

    def get_order_history(self, market=""):
        """
        Used to retrieve your order history

        /account/getorderhistory

        :param market: Bittrex market identifier (i.e BTC-DOGE)
        :type market: str

        :return:
        :rtype : dict
        """
        return self.api_query('getorderhistory', {"market": market})

    def get_withdrawal_history(self, currency=""):
        """
        Used to retrieve your withdrawal history

        /account/getwithdrawalhistory

        :param currency: String literal for the currency (ie. BTC) (defaults to all)
        :type currency: str

        :return:
        :rtype : dict
        """
        return self.api_query('getwithdrawalhistory', {"currency": currency})

    def get_deposit_history(self, currency=""):
        """
        Used to retrieve your deposit history

        /account/getdeposithistory

        :param currency: String literal for the currency (ie. BTC) (defaults to all)
        :type currency: str

        :return:
        :rtype : dict
        """
        return self.api_query('getdeposithistory', {"currency": currency})

    def get_ticks(self, market, tick_interval="tenMinutes", timestamp=""):
        """
        Used to retrieve market ticker 'ticks' data (APIv2.0)

        /pub/market/GetTicks

        :param market: Bittrex market identifier (i.e BTC-DOGE)
        :type market: str

        :param tick_interval: ticker sample interval in camel case (defaults to 10 minutes)
        :type market: str
        :valid values: “oneMin”, “fiveMin”, “thirtyMin”, “hour”, “day”

        :param timestamp: (optional) timestamp value that is currently not used by the API.
        :type market: int

        :return:
        :rtype : dict :
        """
        return self.api_query('GetTicks', {"marketName": market, "tickInterval": tick_interval, "_": timestamp})

    def get_latest_candle(self, market, tick_interval, timestamp=""):
        """
        Used to get the latest candle for the market.
        Endpoint:
        1.1 NO EQUIVALENT
        2.0 /pub/market/GetLatestTick
        Example ::
            { success: true,
              message: '',
              result:
              [ {   O : 0.00350397,
                    H : 0.00351000,
                    L : 0.00350000,
                    C : 0.00350350,
                    V : 1326.42643480,
                    T : 2017-11-03T03:18:00,
                    BV: 4.64416189 } ]
            }
        :return: Available latest tick candle in JSON
        :rtype: dict

        *** This is was pulled from: https://github.com/ericsomdahl/python-bittrex/blob/master/bittrex/bittrex.py#L818
        It was the original project this is based on. ***
        """
        return self.api_query('GetLatestTick', {"marketName": market, "tickInterval": tick_interval, "_": timestamp})