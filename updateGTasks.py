from setup import *
from helperFunctions import *


###############################################################
### PART 4: UPDATE GOOGLE TASKS THAT WERE CHANGED IN NOTION ###
###############################################################


print("Updating Google Tasks that were changed in Notion...\n")

# Get all of your Notion tasks that need to be updated in Google Tasks

query = {
    'database_id': NOTION_DATABASE_ID, 
    'filter': {
        "and": [
            {
                'property': NOTION_NEEDS_GTASKS_UPDATE,
                'checkbox': {
                    'equals': True
                }
            },
            {
                'property': NOTION_SYNCED,
                'checkbox': {
                    'equals': True
                }
            },
            {
                'property': NOTION_DELETED,
                'checkbox': {
                    'equals': False
                }
            }
        ]
    }
}
notionPages = notion.databases.query(  
    **query
)
nextCursor = notionPages['next_cursor']

while notionPages['has_more']:
    query['start_cursor'] = nextCursor
    moreNotionPages = notion.databases.query(
        **query
    )
    nextCursor = moreNotionPages['next_cursor']
    notionPages['results'] += moreNotionPages['results']
    if nextCursor is None:
        break

notionPagesResults = notionPages['results']

notionTaskNames = []
gTasksStatuses = []
notionTaskDates = []
notionDescriptions = []
gTasksIds = [makeOneLinePlainText(page['properties'][NOTION_GTASKS_TASK_ID]['rich_text']) for page in notionPagesResults]
notionLists = []
currentGTasksLists = [makeOneLinePlainText(page['properties'][NOTION_GTASKS_LIST_ID]['rich_text']) for page in notionPagesResults]
newGTasksLists = []

if len(notionPagesResults) > 0:
    for i, page in enumerate(notionPagesResults):
        try:
            notionTaskNames.append(page['properties'][NOTION_TASK_NAME]['title'][0]['plain_text'])
        except:
            notionTaskNames.append('No Title')

        try:
            status = page['properties'][NOTION_STATUS]['status']['name']
            if status in NOTION_TO_DO_STATUSES or status in NOTION_IN_PROGRESS_STATUSES:
                gTasksStatuses.append(GOOGLE_TO_DO_STATUS)
            elif status in NOTION_COMPLETE_STATUSES:
                gTasksStatuses.append(GOOGLE_DONE_STATUS)
        except:
            gTasksStatuses.append(GOOGLE_TO_DO_STATUS)

        try:
            notionTaskDates.append(parseDateTimeString(page['properties'][NOTION_DATE]['date']['start'][:-6], '%Y-%m-%dT%H:%M:%S.000'))
        except:
            try:
                notionTaskDates.append(parseDateString(page['properties'][NOTION_DATE]['date']['start'], '%Y-%m-%d'))
            except:
                notionTaskDates.append('')

        try: 
            notionDescriptions.append(makeDescription(page['properties'][NOTION_DESCRIPTION]['rich_text']))
        except:
            notionDescriptions.append('')

        try:
            newGTasksLists.append(LIST_DICTIONARY[page['properties'][NOTION_LIST_NAME]['select']['name']])
        except:
            newGTasksLists.append(DEFAULT_LIST_ID)

        try:
            notionLists.append(page['properties'][NOTION_LIST_NAME]['select']['name'])
        except:
            notionLists.append('')
        
        # Update the Google Calendar event
        updatedGoogleTask = updateGoogleTask(notionTaskNames[i], notionDescriptions[i], notionTaskDates[i], currentGTasksLists[i], newGTasksLists[i], gTasksIds[i], gTasksStatuses[i])

        # Update the necessary fields in Notion with the updated Google Calendar event info
        notionTaskUpdate = notion.pages.update(
            **{
                'page_id': page['id'],
                'properties': {
                    NOTION_LAST_SYNCED: {
                        'date': {
                            'start': addTimeZoneForNotion(nowToDateTimeString()),
                            'end': None
                        }
                    },
                }
            }
        )

        # List changed to empty, so set it to the list associated with the 'GTasks List ID' field
        if notionLists[i] == '':
            notionTaskUpdate = notion.pages.update(
                **{
                    'page_id': page['id'],
                    'properties': {
                        NOTION_LIST_NAME: { 
                            'select': {
                                "name": list(LIST_DICTIONARY.keys())[list(LIST_DICTIONARY.values()).index(currentGTasksLists[i])]
                            }
                        }
                    }
                }
            )

        # List changed (but not to an empty value), so update the 'GTasks List ID' field 
        elif newGTasksLists[i] != currentGTasksLists[i]:
            notionTaskUpdate = notion.pages.update(
                **{
                    'page_id': page['id'],
                    'properties': {
                        NOTION_GTASKS_LIST_ID: { 
                            'rich_text': [{
                                'text': {
                                    'content': LIST_DICTIONARY[notionTaskUpdate['properties'][NOTION_LIST_NAME]['select']['name']]
                                }
                            }]
                        },
                        NOTION_GTASKS_TASK_ID: {
                            'rich_text': [{
                                'text': {
                                    'content': updatedGoogleTask['id']
                                }
                            }]
                        }
                    }
                }
            )
        
    print("Finished updating Google Tasks that were changed in Notion!\n")
else:
    print("No Google Tasks to update\n")
