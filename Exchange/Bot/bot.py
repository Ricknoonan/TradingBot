import sys, getopt
import time
import pprint

from urllib.error import URLError

from Exchange.Bot.botchart import BotChart
from Exchange.Bot.botstrategy import BotStrategy
from Exchange.Bot.botlog import BotLog
from Exchange.Bot.botcandlestick import BotCandlestick
from Exchange.Bot.botstrategy1 import BotStrategy1
from Exchange.Bot.botstrategy2 import BotStrategy2


def main(argv):
    startTime = False
    endTime = False
    pair = "BTC_XMR"

    try:
        opts, args = getopt.getopt(argv, "hp:c:n:s:e:", ["period=", "currency=", "points="])
    except getopt.GetoptError:
        print('trading-bot.py -p <period length> -c <currency pair> -n <period of moving average>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('trading-bot.py -p <period length> -c <currency pair> -n <period of moving average>')
            sys.exit()
        elif opt in ("-p", "--period"):
            if (int(arg) in [300, 900, 1800, 7200, 14400, 86400]):
                period = arg
            else:
                print('Poloniex requires periods in 300,900,1800,7200,14400, or 86400 second increments')
                sys.exit(2)
        elif opt in ("-c", "--currency"):
            pair = arg
        elif opt in ("-n", "--points"):
            lengthOfMA = int(arg)
        elif opt in ("-s"):
            startTime = arg
        elif opt in ("-e"):
            endTime = arg

    #if there is a start time, then we are using backtest data.
    # A botchart object is created passing. getPoints() reutns the array of h
    # historical data that has been populate on constructor call
    #

    if startTime:
        chart = BotChart("poloniex", pair, startTime, endTime, 300)

        #strategy = BotStrategy(pair)
        #strategy = BotStrategy1(pair)
        strategy = BotStrategy(pair)


        for candlestick in chart.getPoints():
            strategy.tick(candlestick)

    else:
        chart = BotChart("poloniex", "BTC_XMR", startTime, endTime, 3600, False)

        #strategy = BotStrategy("BTC_XMR")
        strategy = BotStrategy1("BTC_XMR")

        candlesticks = []
        developingCandlestick = BotCandlestick()

        while True:
            try:
                developingCandlestick.tick(chart.getCurrentPrice())
            except URLError:
                time.sleep(int(30))
                developingCandlestick.tick(chart.getCurrentPrice())

            if (developingCandlestick.isClosed()):
                candlesticks.append(developingCandlestick)
                strategy.tick(developingCandlestick)
                developingCandlestick = BotCandlestick()

            time.sleep(int(30))


if __name__ == "__main__":
    main(sys.argv[1:])
