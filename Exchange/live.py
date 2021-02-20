import sys, getopt
import time
from urllib.error import URLError

from Exchange.Bot.botchart import BotChart
from Exchange.Bot.botstrategy import BotStrategy
from Exchange.Bot.botlog import BotLog
from Exchange.Bot.botcandlestick import BotCandlestick

def main(argv):
	chart = BotChart("poloniex","BTC_XMR",300,False)

	strategy = BotStrategy()

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