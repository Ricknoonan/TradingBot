import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
import os
import pickle
from FileReader import readSheet
from FileWriter import writeSheet


def updateSheet():
    cred = 'credentials.json'
    sheet = 'sheets'
    version = 'v4'
    scope = ['https://www.googleapis.com/auth/spreadsheets']

    data = readSheet()

    # Do something with dateframe
    # Write df back to sheet
    # df.set_option("display.max_rows", None, "display.max_columns", None)

    data.loc[0 if pd.isnull(data.index.max()) else data.index.max() + 1] = [1, 2, 3, 4, 5, 7]

    writeSheet(cred, sheet, version, scope, data)


updateSheet()
