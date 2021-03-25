import getopt
import sys
import Coinbase.coinbaseCredentials

import requests
import time

from coinbase.wallet.client import Client
import cbpro
import json

PRIVATE_KEY = Coinbase.coinbaseCredentials.private_key
PUBLIC_KEY = Coinbase.coinbaseCredentials.public_key
PASSPHRASE = Coinbase.coinbaseCredentials.passphrase


def main(argv):
    prevCrypto = []
    purchaseAmount = 0

    fiat = 'EUR'

    try:
        opts, args = getopt.getopt(argv, "a:", ["amount="])
    except getopt.GetoptError:
        print('error')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-a", "--amount"):
            purchaseAmount = float(arg)

    while True:
        currentCrypto = getCryptoList()
        cryptoList = getNewCryptoAddedList(prevCrypto, currentCrypto)
        if len(cryptoList) > 0:
            buyOrder(cryptoList, purchaseAmount, fiat)
        prevCrypto = currentCrypto
        print(purchaseAmount)
        print(currentCrypto)
        time.sleep(15)


def getCryptoList():
    currentCrpyto = []
    uri = 'https://api.pro.coinbase.com/currencies'
    response = requests.get(uri).json()
    for i in range(len(response)):
        if response[i]['details']['type'] == 'crypto':
            crypto = response[i]['id']
            currentCrpyto.append(crypto)
    return currentCrpyto


def getNewCryptoAddedList(prevCryptoList, currentCryptoList):
    cryptoDiffList = diff(prevCryptoList, currentCryptoList)
    if len(cryptoDiffList) == 0:
        print("no new cryptos")
    if len(cryptoDiffList) >= 1:
        return cryptoDiffList
    else:
        return []


def diff(list1, list2):
    c = set(list1).union(set(list2))  # or c = set(list1) | set(list2)
    d = set(list1).intersection(set(list2))  # or d = set(list1) & set(list2)
    return list(c - d)


def buyOrder(addedCryptoList, amount, fiat):
    auth_client = cbpro.AuthenticatedClient(PUBLIC_KEY, PRIVATE_KEY, PASSPHRASE)
    client = Client(PUBLIC_KEY, PRIVATE_KEY)
    for crypto in addedCryptoList:
        buyAmountCrypto = fiatConverter(crypto, client, amount, fiat)
        pair = crypto + "-" + fiat
        buy = auth_client.place_market_order(product_id=pair, side='buy', funds=amount)
        print(str(buy) + ". This is a buy of: " + str(pair) + " of " + str(amount))


def fiatConverter(crypto, auth_client, buyAmount, fiat):
    pair = crypto + "-" + fiat
    price = auth_client.get_spot_price(currency_pair=pair)
    coinbaseAmount = float(price.__getitem__('amount'))
    buyAmountCrypto = buyAmount / coinbaseAmount
    return buyAmountCrypto


if __name__ == "__main__":
    main(sys.argv[1:])
