import getopt
import sys
import coinbaseCredentials

import requests
import time

from coinbase.wallet.client import Client

PRIVATE_KEY = coinbaseCredentials.private_key
PUBLIC_KEY = coinbaseCredentials.public_key


def main(argv):
    prevCrypto = []
    purchaseAmount = 0
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
        fiat = 'EUR'
        if len(cryptoList) > 0:
            buyOrder(cryptoList, purchaseAmount, fiat)
        prevCrypto = currentCrypto
        print(purchaseAmount)
        print(currentCrypto)
        time.sleep(10)


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


def getNewCryptoAddedList(prevCryptoList, currentCryptoList):
    cryptoDiffList = diff(prevCryptoList, currentCryptoList)
    if len(cryptoDiffList) == 0:
        print("no new cryptos")
    if len(cryptoDiffList) >= 1 & len(prevCryptoList) != 0:
        return cryptoDiffList
    else:
        return []


def fiatConverter(crypto, client, buyAmount, fiat):
    pair = crypto + "-" + fiat
    price = client.get_spot_price(currency_pair=pair)
    buyAmountCrypto = buyAmount / price
    return buyAmountCrypto


def buyOrder(addedCryptoList, amount, currency):
    client = Client(PUBLIC_KEY, PRIVATE_KEY)
    account = client.get_primary_account()
    payment_method = client.get_payment_methods()[0]
    for crypto in addedCryptoList:
        buyAmountCrypto = fiatConverter(crypto, client, amount, currency)
        buy = account.buy(amount=str(buyAmountCrypto), currency=str(crypto), payment_method=payment_method.id)
        print(buy)


if __name__ == "__main__":
    main(sys.argv[1:])
