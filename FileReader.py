import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
import os
import pickle


class FileReader(object):

    def __init__(self):
        self.scope = ['https://www.googleapis.com/auth/spreadsheets']
        self.input = '1JqTecTzlTI_MHaR6K2yBvasv-0r8lj8gU41eMN1RO1E'
        self.range = 'A1:AA1000'

    def readSheet(self):
        global values_input, service
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.scope)  # here enter the name of your downloaded JSON file
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result_input = sheet.values().get(spreadsheetId=self.input,
                                          range=self.range).execute()
        values_input = result_input.get('values', [])

        if not values_input:
            print('No data found.')

        df = pd.DataFrame(values_input[1:], columns=values_input[0])

        return df
