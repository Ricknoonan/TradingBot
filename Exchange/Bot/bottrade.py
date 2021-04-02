from Exchange.Bot.botlog import BotLog


class BotTrade(object):
    def __init__(self, currentPrice, stopLoss):
        self.output = BotLog()
        self.status = "OPEN"
        self.entryPrice = currentPrice
        self.exitPrice = 0.0
        self.output.logOpen("Trade opened")
        self.profit = 0
        self.tradeStatus = "Entry Price: " + str(self.entryPrice) + " Status: " + str(self.status)
        if stopLoss:
            self.stopLossPrice = currentPrice - (stopLoss * currentPrice)

    # TODO: Refactor this output/ combine close and stopLoss
    def close(self, currentPrice):
        self.status = "CLOSED"
        self.exitPrice = currentPrice
        self.profit = self.exitPrice - self.entryPrice
        self.output.logClose("Entry Price: " + str(self.entryPrice) + " Status: " + self.status + " Exit Price: " + str(
            self.exitPrice) + " P/L: " + str(self.profit) + "\n")

    def stopLoss(self, currentPrice):
        if self.stopLossPrice:
            if currentPrice < self.stopLossPrice:
                self.close(currentPrice)
                self.output.logOpen(
                    "Stop loss hit! Status: " + self.status + " Exit Price: " + str(self.exitPrice) + "Loss: " + str(
                        self.profit))

    def showTrade(self):
        if self.status == "OPEN":
            self.output.logOpen(self.tradeStatus)
