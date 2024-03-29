from datetime import datetime
import csv


class BotLog(object):
    def __init__(self):
        pass

    def logOpen(self, message):
        date = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        f = open("trade-log.txt", "a+")
        s = date + " New trade opened: " + " " + message + "\n"
        f.write(s)

    def logClose(self, message):
        date = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        f = open("trade-log.txt", "a+")
        s = date + " Trade closed " + " " + message + "\n"
        f.write(s)

    def log(self, message):
        date = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        f = open("trade-log.txt", "a+")
        s = date + message + "\n"
        f.write(s)
