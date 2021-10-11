from ScannerBot import binanceCredential
from pythonic_binance.client import Client

api_key = binanceCredential.public_key
api_secret = binanceCredential.private_key


def getClient():
    client = Client(api_key, api_secret)
    return client




