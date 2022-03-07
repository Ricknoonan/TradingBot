import csv
from datetime import datetime


class BotLog(object):
    def __init__(self):
        pass

    def logOpenTest(self, message):
        date = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        f = open("trade-log-test.txt", "a+")
        s = date + " New Test trade opened: " + " " + message + "\n"
        f.write(s)


    def logOpenLive(self, message):
        date = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        f = open("trade-log-live.txt", "a+")
        s = date + " New Live trade opened: " + " " + message + "\n"
        f.write(s)

    def logCloseTest(self, message):
        date = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        f = open("trade-log-test.txt", "a+")
        s = date + " Trade closed " + " " + message + "\n"
        f.write(s)

    def logCloseLive(self, message):
        date = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        f = open("trade-log-live.txt", "a+")
        s = date + " Trade closed " + " " + message + "\n"
        f.write(s)


    def log(self, message):
        date = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        f = open("trade-log-test.txt", "a+")
        s = date + message + "\n"
        f.write(s)

    def logPrices(self, price, timestamp):
        with open('prices.csv', 'w', encoding='UTF8', newline=' ') as f:
            writer = csv.writer(f)

            # write the data
            writer.writerow([str(price), str(timestamp)])

