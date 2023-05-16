import os
from notion_client import Client
from googleapiclient.discovery import build
import pickle
from setup import *

# Set up the Google Tasks API connection

gTasksCredentials = pickle.load(open(PROJECT_LOCATION + 'token.pkl', 'rb'))
service = build('tasks', 'v1', credentials=gTasksCredentials)

# If the the Google Calendar API token expires, then gTasksApiToken.py creates a new token for the program to use

print("Verifying the Google Tasks API token...\n")

try:
    testList = service.tasklists().get(tasklist=DEFAULT_LIST_ID).execute()
    print("Google Tasks API token is valid!\n")
except:
    print("Attempting to refresh the Google Tasks API token...\n")
    
    os.system('python ' + PROJECT_LOCATION + 'gTasksApiToken.py') # Refresh the token (uses the gTasksApiToken script)

    gCalCredentials = pickle.load(open(PROJECT_LOCATION + 'token.pkl', 'rb'))
    service = build('calendar', 'v3', credentials=gCalCredentials)

    try:
        calendar = service.tasklists().get(tasklist=DEFAULT_LIST_ID).execute()
        print("Successfully refreshed the Google Tasks API token!\n")
    except:
        print("Could not refresh the Google Tasks API token!\n")
        exit()

# Set up the Notion API connection

notion = Client(auth=NOTION_TOKEN)
