import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
import os
import pickle
from FileReader import FileReader
from FileWriter import FileWriter


class FileController:

    def updateSheet(self):
        cred = 'credentials.json'
        sheet = 'sheets'
        version = 'v4'
        scope = ['https://www.googleapis.com/auth/spreadsheets']

        df = FileReader()

        data = df.readSheet()

        # Do something with dateframe
        # Write df back to sheet

        fw = FileWriter()
        fw.writeSheet(cred, sheet, version, scope, data)
