from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

# Set up the Google Tasks API credentials

SCOPES = ['https://www.googleapis.com/auth/tasks']
flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', scopes=SCOPES)
credentials = flow.run_console()

pickle.dump(credentials, open('token.pkl', 'wb'))

credentials = pickle.load(open('token.pkl', 'rb'))
service = build('tasks', 'v1', credentials=credentials)
