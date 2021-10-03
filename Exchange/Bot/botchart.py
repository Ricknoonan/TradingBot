from Exchange.Bot.poloniex import poloniex
import pandas as pd
import urllib, json
import pprint
from Exchange.Bot.botcandlestick import BotCandlestick


class BotChart(object):
    startTime = 1491048000
    endTime = 1491591200

    def __init__(self, exchange, pair=None, startTime=None, endTime=None, period=None, backtest=True):
        self.pair = pair
        self.period = period
        self.startTime = startTime
        self.endTime = endTime

        self.data = []

        if exchange == "poloniex":
            self.conn = poloniex('', '')

            if backtest:
                poloData = self.conn.api_query("returnChartData",
                                               {"currencyPair": self.pair, "start": self.startTime, "end": self.endTime,
                                                "period": self.period})
                for datum in poloData:
                    if datum['open'] and datum['close'] and datum['high'] and datum['low']:
                        self.data.append(
                            BotCandlestick(self.period, datum['open'], datum['close'], datum['high'], datum['low'],
                                           datum['weightedAverage'], datum['date']))

        if exchange == "bittrex":
            if backtest:
                url = "https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName=" + self.pair + "&tickInterval=" + self.period + "&_=" + str(
                    self.startTime)
                response = urllib.urlopen(url)
                rawdata = json.loads(response.read())

                self.data = rawdata["result"]

        if exchange == 'binance':
            binance

    def getPoints(self):
        return self.data

    def getCurrentPrice(self):
        currentValues = self.conn.api_query("returnTicker")
        lastPairPrice = {}
        lastPairPrice = currentValues[self.pair]["last"]
        return lastPairPrice
