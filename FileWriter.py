import os
import pickle
from urllib.request import Request

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

INPUT = '1JqTecTzlTI_MHaR6K2yBvasv-0r8lj8gU41eMN1RO1E'
RANGE = 'A1:AA1000'


class FileWriter(object):

    def writeSheet(self, client_secret_file, api_service_name, api_version, scopes, df):
        #global service
        # SCOPES = [scope for scope in scopes[0]]
        # print(SCOPES)

        cred = None

        if os.path.exists('token_write.pickle'):
            with open('token_write.pickle', 'rb') as token:
                cred = pickle.load(token)

        if not cred or not cred.valid:
            if cred and cred.expired and cred.refresh_token:
                cred.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
                cred = flow.run_local_server()

            with open('token_write.pickle', 'wb') as token:
                pickle.dump(cred, token)

        try:
            service = build(api_service_name, api_version, credentials=cred)
            print(api_service_name, 'service created successfully')
            response_date = service.spreadsheets().values().update(
                spreadsheetId=INPUT,
                valueInputOption='RAW',
                range=RANGE,
                body=dict(
                    majorDimension='ROWS',
                    values=df.T.reset_index().T.values.tolist())
            ).execute()
            print('Sheet successfully Updated')
        except Exception as e:
            print(e)
            # return None
