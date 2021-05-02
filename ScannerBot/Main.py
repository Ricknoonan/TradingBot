import time
from urllib.error import URLError

from Exchange.Bot.botcandlestick import BotCandlestick
from Exchange.Bot.botchart import BotChart
from Exchange.Bot.botstrategy1 import BotStrategy1


# 1. Get 10 small cap coins
# 1.1. need to get list of all coins traded and sort by market cap.
# 2. Check for momentum, developer activity,
# 2.1. this will involve pulling candlesticks for each small cap coin and running various analysis. Check for computational load.
# 3. Buy and sell short term, or buy and hold.
# 3.1.
def Main(argv):
    while True:

        # TODO get coin list
        chart = BotChart(exchange="poloniex", period=3600, backtest=False)

        candlesticks = []
        developingCandlestick = BotCandlestick()

        while True:
            try:
                developingCandlestick.tick(chart.getCurrentPrice())
            except URLError:
                time.sleep(int(30))
                developingCandlestick.tick(chart.getCurrentPrice())

            if developingCandlestick.isClosed():
                candlesticks.append(developingCandlestick)
                developingCandlestick = BotCandlestick()

            time.sleep(int(30))
