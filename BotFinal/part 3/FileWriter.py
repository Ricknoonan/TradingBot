import os
import pickle
from urllib.request import Request

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from FileReader import df

df_gold = df[(df['Medal'] == 'Gold') & (df['Sport'] == 'Gymnastics')]

# change this by your sheet ID
SAMPLE_SPREADSHEET_ID_input = '1cvZswLiDo3LfhnA7RcS8vFqacx73RGor-OZ_FtvyLE8'

# change the range if needed
SAMPLE_RANGE_NAME = 'A1:AA1000'


def Create_Service(client_secret_file, api_service_name, api_version, *scopes):
    global service
    SCOPES = [scope for scope in scopes[0]]
    # print(SCOPES)

    cred = None

    if os.path.exists('token_write.pickle'):
        with open('token_write.pickle', 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            cred = flow.run_local_server()

        with open('token_write.pickle', 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(api_service_name, api_version, credentials=cred)
        print(api_service_name, 'service created successfully')
        # return service
    except Exception as e:
        print(e)
        # return None


# change 'my_json_file.json' by your downloaded JSON file.
Create_Service('credentials.json.json', 'sheets', 'v4', ['https://www.googleapis.com/auth/spreadsheets'])


def Export_Data_To_Sheets():
    response_date = service.spreadsheets().values().update(
        spreadsheetId=SAMPLE_SPREADSHEET_ID_input,
        valueInputOption='RAW',
        range=SAMPLE_RANGE_NAME,
        body=dict(
            majorDimension='ROWS',
            values=df_gold.T.reset_index().T.values.tolist())
    ).execute()
    print('Sheet successfully Updated')


Export_Data_To_Sheets()