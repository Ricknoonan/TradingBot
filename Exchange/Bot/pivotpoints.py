import yfinance as yf
import datetime as dt


# TODO 10 days resistance pivot points. If pivot point gets broken and stays broken for x time slices, bull indicator
# pipe dataframe as prices from strategy function
class PivotPoints:

    def calcPivot(self, prices):
        pivots = []
        dates = []
        counter = 0
        lastPivot = 0

        Range = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        dateRange = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        for i in prices.index:
            currentMax = max(Range, default=0)
            value=round(prices["prices"][i], 2)
