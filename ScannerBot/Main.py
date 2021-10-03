import sys
import time

from urllib.error import URLError
import os
from time import sleep
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
from Exchange.Bot.botcandlestick import BotCandlestick
from Exchange.Bot.botchart import BotChart
from Exchange.Bot.botstrategy import BotStrategy
from Exchange.Bot.botstrategy1 import BotStrategy1
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
            baseBTC.append("BTC" + base)
    return baseBTC


def compare(baseBTC, marketCapDict):
    quotes = []
    for key, value in marketCapDict.items():
        for quote in baseBTC:
            if (quote == key) & len(quotes) < 5:
                quotes.append(quote)
    return "No Match"


def strategyFeed(smallCapCoins):
    startTime = 1615226099
    endTime = 1617900899
    api_key = binanceCredential.public_key
    api_secret = binanceCredential.private_key
    client = Client(api_key, api_secret)

    for coin in smallCapCoins:
        strategy = BotStrategy(coin)
        nextCoin = False
        while nextCoin is False:
            current_price = client.get_symbol_ticker(params=coin)
            trade = strategy.tick(current_price)
            if trade.status == 'CLOSED':
                nextCoin = True


    # chart = BotChart("poloniex", coin, startTime, endTime, 300, True)
    #
    # strategy = BotStrategy1(coin)
    #
    # for candlestick in chart.getPoints():
    #     strategy.tick(candlestick)


def Main():
    bastBTC = binanceData()
    marketCapDict = marketCapData()
    result = compare(bastBTC, marketCapDict)
    strategyFeed(result)
    print(result)


if __name__ == "__main__":
    Main()
