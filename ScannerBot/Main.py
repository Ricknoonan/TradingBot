import sys
from pythonic_binance.client import Client

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

# binance
# 0 get markets from binance -> Done
# 1. Get small cap coins -> Done
# 1.1. need to get list of all coins traded and sort by market cap. then pick the smallest 10 caps that have a BTC market on binance
# 2. Check for momentum, developer activity, news?
# 2.1. this will involve pulling candlesticks for each small cap coin and running various analysis.
# 3. Buy and sell short term, or buy and hold.
# 3.1.
from ScannerBot import binanceCredential


def sortByMarketCap(datum):
    marketCap = {}
    for coin in datum:
        if coin.get('quote').get('USD').get('market_cap') != 0:
            marketCap[coin.get('symbol')] = (coin.get('quote').get('USD').get('market_cap'))
    sortedDict = {k: v for k, v in sorted(marketCap.items(), key=lambda item: item[1])}
    return sortedDict


def marketCapData():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',
        'limit': '5000',
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': 'f3f497ea-cba3-4866-80c8-16e0f8e0d02d',
    }
    session = Session()
    session.headers.update(headers)
    datum = None
    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        datum = data.get('data')
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    return sortByMarketCap(datum)


def binanceData():
    api_key = binanceCredential.public_key
    api_secret = binanceCredential.private_key
    baseBTC = []

    client = Client(api_key, api_secret)
    info = client.get_all_tickers()
    for coin in info:
        if 'BTC' in coin.get('symbol')[3:]:
            market = coin.get('symbol')
            base = market[:-3]
            baseBTC.append(base)
    return baseBTC


def compare(baseBTC, marketCapDict):
    for key, value in marketCapDict.items():
        for quote in baseBTC:
            if quote == key:
                return quote
    return "No Match"


def Main():
    bastBTC = binanceData()
    marketCapDict = marketCapData()
    result = compare(bastBTC, marketCapDict)
    print(result)


if __name__ == "__main__":
    Main()
