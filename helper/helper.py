import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials


def setup_auth():
    credentials_json = json.loads(os.environ.get('GOOGLE_CREDENTIALS'))
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_json, scope)
    gc = gspread.authorize(credentials)
    return gc
