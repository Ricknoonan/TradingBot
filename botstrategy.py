from botlog import BotLog
from botindicators import BotIndicators
from bottrade import BotTrade

class BotStrategy(object):
	def __init__(self):
		self.output = BotLog()
		self.prices = []
		self.closes = []  # Needed for Momentum Indicator
		self.trades = []
		self.currentPrice = ""
		self.currentClose = ""
		self.numSimulTrades = 1
		self.accumProfit = 0
		self.closedPosCounter = 0

		self.indicators = BotIndicators()

	def tick(self, candlestick):
		self.currentPrice = float(candlestick.priceAverage)
		self.prices.append(self.currentPrice)
		
		#self.currentClose = float(candlestick['close'])
		#self.closes.append(self.currentClose)
		#if self.indicators.movingAverage(self.prices, 15) is not None:
		self.output.log("Price: "+str(candlestick.priceAverage)+"\tMoving Average: "+str(self.indicators.movingAverage(self.prices, 15)) + "\n")

		self.evaluatePositions()
		self.showPositions()

	def evaluatePositions(self):
		openTrades = []

		for trade in self.trades:
			if trade.status == "OPEN":
				openTrades.append(trade)

		if len(openTrades) < self.numSimulTrades:
			if self.indicators.RSI(self.prices) < 30:
				self.trades.append(BotTrade(self.currentPrice, stopLossPrice=.001))


		# TODO: Refactor Clean up close/stoploss
		for trade in openTrades:
			if self.currentPrice >= (trade.entryPrice * 1.01):
				trade.close(self.currentPrice)
				self.accumProfit += trade.profit
				self.closedPosCounter += 1
				self.output.log("Strategy Profit/Loss: " + str(self.accumProfit) + "\n" + str(self.closedPosCounter) + "\n")

			#if float(self.currentPrice) > float(self.indicators.movingAverage(self.prices, 15)):
			#	trade.close(self.currentPrice)
			if trade.status == "OPEN":
				trade.stopLoss(self.currentPrice)



	def showPositions(self):
		for trade in self.trades:
			trade.showTrade()