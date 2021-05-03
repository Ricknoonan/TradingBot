import sys

from pythonic_binance.client import Client
from ScannerBot import binanceCredential


# binance
# 1. Get 10 small cap coins
# 1.1. need to get list of all coins traded and sort by market cap.
# 2. Check for momentum, developer activity,
# 2.1. this will involve pulling candlesticks for each small cap coin and running various analysis. Check for computational load.
# 3. Buy and sell short term, or buy and hold.
# 3.1.


def Main(argv):
    api_key = binanceCredential.public_key
    api_secret = binanceCredential.private_key

    client = Client(api_key, api_secret)
    info = client.get_all_tickers()
    print(len(info))
    count = 0
    for coin in info:
        if "ANJ" in coin.get('symbol'):
            print(coin)
            count += 1
    print(count)


if __name__ == "__main__":
    Main(sys.argv[1:])
