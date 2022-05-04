import csv
from time import sleep

from ScannerBot.BinanceUtil import getClient
import pandas as pd
import talib as ta

isTA = False


def initaliseBTCPairs(client):
    btcPairs = []
    info = client.get_all_tickers()
    for coin in info:
        if 'BTC' in coin.get('symbol')[-3:]:
            btcPairs.append(coin)
    return btcPairs


def runCSVFile(btcPair, pairPricesDict):
    global isTA
    for pairPrice in btcPair:
        currentPrice = pairPrice.get('price')
        pair = pairPrice.get('symbol')
        pairPriceList = pairPricesDict.get(pair)
        if pairPriceList is None:
            pairPricesDict[pair] = [currentPrice]
        else:
            if len(pairPriceList) >= 30:
                pairPriceList.pop(0)
                isTA = True
            pairPriceList.append(currentPrice)
    if isTA:
        CSVList = []
        for k, v in pairPricesDict:
            pairPriceSeries = pd.Series(v)
            rsi = ta.RSI(pairPriceSeries, 24).iloc[-1]
            macd = ta.MACD(pairPriceSeries)[0].iloc[-1]
            CSVList.append([str(k), str(macd), str(rsi)])
        with open('../TA.csv', 'w', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerows(CSVList)


def runTA():
    client = getClient()
    pairPrices = {}
    btcPairs = initaliseBTCPairs(client)
    with open('../TA.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(["Testing"])
    while True:
        runCSVFile(btcPairs, pairPrices)
        sleep(60)  # 1 minute
