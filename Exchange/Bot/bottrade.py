from Exchange.Bot.botlog import BotLog


class BotTrade(object):
    def __init__(self, currentPrice, stopLoss, quantity, positionSize, pair, openTimeStamp, liveTrade):
        self.output = BotLog()
        self.status = "OPEN"
        self.entryPrice = currentPrice
        self.exitPrice = 0.0
        self.profit = 0
        self.quantity = quantity
        self.positionSize = positionSize
        self.tradePair = pair
        self.tradeOpenedStatus = "Entry Price: " + str(self.entryPrice) + " Status: " + str(self.status)
        self.openTimeStamp = openTimeStamp
        self.closeTimeStamp = 0
        self.liveTrade = liveTrade
        if stopLoss:
            self.stopLossPrice = currentPrice - (stopLoss * currentPrice)

    # TODO: Refactor this output/ combine close and stopLoss
    def close(self, currentPrice, closeTimeStamp):
        self.status = "CLOSED"
        self.exitPrice = currentPrice
        self.closeTimeStamp = closeTimeStamp
        self.profit = (self.exitPrice * self.quantity) - (self.entryPrice * self.quantity)
        print("CLOSED " + str(self.profit))
        return self.profit

    def stopLoss(self, currentPrice):
        if self.stopLossPrice:
            if currentPrice < self.stopLossPrice:
                self.close(currentPrice, 0)
                self.output.logOpen(
                    "Stop loss hit! Status: " + self.status + " Exit Price: " + str(self.exitPrice) + "Loss: " + str(
                        self.profit))

    def getProfit(self):
        return self.profit

    def showTrade(self):
        if self.status == "OPEN":
            self.output.logOpen(self.tradeOpenedStatus)
            print(self.tradeOpenedStatus)

    def isClosed(self):
        if self.status == "CLOSED":
            return True
        else:
            return False

    def getEntryPrice(self):
        return self.entryPrice
