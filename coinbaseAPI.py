import json
import requests
import schedule
import time

from coinbase.wallet.client import Client

# client = Client("ihZm0KXM467Qvc0a", "nO9SSuawChpf8MGvBWoq9JUdnDEm1AQw")

# currencies = client.get_exchange_rates()
# json_string = json.dumps(currencies)

# for curr in currencies:
#    print(curr)

def getCryptoList():
    currentCrpyto = []
    uri = 'https://api.pro.coinbase.com/currencies'
    response = requests.get(uri).json()
    for i in range(len(response)):
        if response[i]['details']['type'] == 'crypto':
            crypto = response[i]['id']
            currentCrpyto.append(crypto)
    return currentCrpyto


def diff(list1, list2):
    c = set(list1).union(set(list2))  # or c = set(list1) | set(list2)
    d = set(list1).intersection(set(list2))  # or d = set(list1) & set(list2)
    return list(c - d)


def run(prev_crypto):
    currentCrypto = getCryptoList()
    cryptoDiff = diff(prev_crypto, currentCrypto)
    if len(cryptoDiff) == 0:
        print("no new cryptos")
    if len(cryptoDiff) >= 1 & len(prev_crypto) != 0:
        for crypto in cryptoDiff:
            print(crypto)
    return currentCrypto


prevCrypto = []
while True:
    prevCrypto = run(prevCrypto)
    time.sleep(5)