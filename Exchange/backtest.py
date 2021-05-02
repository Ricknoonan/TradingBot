import sys, getopt

from Exchange.Bot.botstrategy import BotStrategy
from Exchange.Bot.botchart import BotChart

def main(argv):
	chart = BotChart("poloniex", "BTC_XMR", 300,,

	strategy = BotStrategy()

	for candlestick in chart.getPoints():
		strategy.tick(candlestick)

if __name__ == "__main__":
	main(sys.argv[1:])