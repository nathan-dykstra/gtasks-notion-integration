from setup import *
from helperFunctions import *


#######################################################
### PART 2: IMPORT NEW NOTION TASKS TO GOOGLE TASKS ###
#######################################################


print("Adding new Notion tasks to Google Tasks...\n")

# Get all of your Notion tasks that have not been synced with Google Tasks

query = {
    'database_id': NOTION_DATABASE_ID, 
    'filter': {
        'and': [
            {
                'property': NOTION_SYNCED,
                'checkbox': {
                    'equals': False
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

maxDate = addTimeZoneForNotion(dateTimeToString(datetime.now() + timedelta(weeks=FUTURE_WEEKS_TO_SYNC)))
minDate = addTimeZoneForNotion(dateTimeToString(datetime.now() - timedelta(weeks=PAST_WEEKS_TO_SYNC)))

if PAST_WEEKS_TO_SYNC >=0 and FUTURE_WEEKS_TO_SYNC >= 0:
    query['filter']['and'].append({'or': [{'property': NOTION_DATE, 'date': {'on_or_after': minDate}}, { 'property': NOTION_DATE, 'date': {'is_empty': True}}]})
    query['filter']['and'].append({'or': [{'property': NOTION_DATE, 'date': {'on_or_before': maxDate}}, { 'property': NOTION_DATE, 'date': {'is_empty': True}}]})
elif PAST_WEEKS_TO_SYNC >=0:
    query['filter']['and'].append({'or': [{'property': NOTION_DATE, 'date': {'on_or_after': minDate}}, { 'property': NOTION_DATE, 'date': {'is_empty': True}}]})
elif FUTURE_WEEKS_TO_SYNC >= 0:
    query['filter']['and'].append({'or': [{'property': NOTION_DATE, 'date': {'on_or_before': maxDate}}, { 'property': NOTION_DATE, 'date': {'is_empty': True}}]})

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
#notionTaskStatuses = []
gTasksStatuses = []
notionTaskDates = []
notionDescriptions = []
gTasksLists = []
notionLists = []

if len(notionPagesResults) > 0:
    for i, page in enumerate(notionPagesResults):
        try:
            notionTaskNames.append(page['properties'][NOTION_TASK_NAME]['title'][0]['plain_text'])
        except:
            notionTaskNames.append('No Title')

        #try:
        #    notionTaskStatuses.append(page['properties'][NOTION_STATUS]['status']['name'])
        #except:
        #    notionTaskStatuses.append('')

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
            gTasksLists.append(LIST_DICTIONARY[page['properties'][NOTION_LIST_NAME]['select']['name']])
        except:
            gTasksLists.append(DEFAULT_LIST_ID)

        try:
            notionLists.append(page['properties'][NOTION_LIST_NAME]['select']['name'])
        except:
            notionLists.append('')

        # Create the Google Task
        newGoogleTask = makeGoogleTask(notionTaskNames[i], notionDescriptions[i], notionTaskDates[i], gTasksLists[i], gTasksStatuses[i])

        # Update the necessary fields in Notion with the new Google Task info
        notionTaskUpdate = notion.pages.update(
            **{
                'page_id': page['id'],
                'properties': {
                    NOTION_GTASKS_TASK_ID: {
                        'rich_text': [{
                            'text': {
                                'content': newGoogleTask['id']
                            }
                        }]
                    },
                    NOTION_GTASKS_LIST_ID: {
                        'rich_text': [{
                            'text': {
                                'content': gTasksLists[i]
                            }
                        }]
                    },
                    NOTION_SYNCED: {
                        'checkbox': True
                    },
                    NOTION_LAST_SYNCED: {
                        'date': {
                            'start': addTimeZoneForNotion(nowToDateTimeString()),
                            'end': None
                        }
                    }
                }
            }
        )

        # Update the Notion 'List' field with the default list if it wasn't assigned
        if notionLists[i] == '':
            notionTaskUpdate = notion.pages.update(
                **{
                    'page_id': page['id'],
                    'properties': {
                        NOTION_LIST_NAME: { 
                            'select': {
                                "name": DEFAULT_LIST_NAME
                            }
                        }
                    }
                }
            )
        
    print("Finished adding new Notion tasks to Google Tasks!\n")
else:
    print("No new Notion tasks to add to Google Tasks\n")
