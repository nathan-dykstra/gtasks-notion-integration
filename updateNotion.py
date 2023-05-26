from datetime import datetime
from setup import *
from helperFunctions import *


#####################################################################
### PART 5: UPDATE NOTION TASKS THAT WERE CHANGED IN GOOGLE TASKS ###
#####################################################################


print("Updating Notion tasks that were changed in Google Tasks...\n")

# Get all synced Notion tasks that aren't deleted and don't need an update in Google Tasks

query = {
    'database_id': NOTION_DATABASE_ID,
    'filter': {
        "and": [
            {
                'property': NOTION_DELETED, 
                'checkbox':  {
                    'equals': False
                }
            },
            {
                'property': NOTION_SYNCED, 
                'checkbox':  {
                    'equals': True
                }
            },
            {# is this condition necessary?
                'property': NOTION_NEEDS_GTASKS_UPDATE, 
                'checkbox':  {
                    'equals': False
                }
            }
        ]
    }
}

maxDate = addTimeZoneForNotion(dateTimeToString(datetime.now() + timedelta(weeks=FUTURE_WEEKS_TO_SYNC)))
minDate = addTimeZoneForNotion(dateTimeToString(datetime.now() - timedelta(weeks=PAST_WEEKS_TO_SYNC)))

if PAST_WEEKS_TO_SYNC >=0 and FUTURE_WEEKS_TO_SYNC >= 0:
    query['filter']['and'].append({'or': [{'property': NOTION_DATE, 'date': {'on_or_after': minDate}}, { 'property': NOTION_STATUS, 'status': {'does_not_equal': 'Done'}}]})
    query['filter']['and'].append({'or': [{'property': NOTION_DATE, 'date': {'on_or_before': maxDate}}, { 'property': NOTION_STATUS, 'status': {'does_not_equal': 'Done'}}]})
elif PAST_WEEKS_TO_SYNC >=0:
    query['filter']['and'].append({'or': [{'property': NOTION_DATE, 'date': {'on_or_after': minDate}}, { 'property': NOTION_STATUS, 'status': {'does_not_equal': 'Done'}}]})
elif FUTURE_WEEKS_TO_SYNC >= 0:
    query['filter']['and'].append({'or': [{'property': NOTION_DATE, 'date': {'on_or_before': maxDate}}, { 'property': NOTION_STATUS, 'status': {'does_not_equal': 'Done'}}]})

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

notionPageLastSyncedDates = [parseDateTimeString(page['properties'][NOTION_LAST_SYNCED]['date']['start'][:-6], '%Y-%m-%dT%H:%M:%S.000') for page in notionPages['results']]
notionPageIds = [page['id'] for page in notionPages['results']]
gTasksIds = [makeOneLinePlainText(page['properties'][NOTION_GTASKS_TASK_ID]['rich_text']) for page in notionPages['results']]
gTasksListIds = [makeOneLinePlainText(page['properties'][NOTION_GTASKS_LIST_ID]['rich_text']) for page in notionPages['results']]

# Get all task info from Google Tasks for each of the synced tasks in Notion

gTasks = []
gTasksListIds = []

listDictionaryKeys = list(LIST_DICTIONARY.keys())
listDictionaryValues = list(LIST_DICTIONARY.values())

for i, gTasksId in enumerate(gTasksIds):
    gTask = None

    for gTasksListId in listDictionaryValues:
        try:
            gTask = service.tasks().get(tasklist=gTasksListId, task=gTasksId).execute()
        except:
            gTask = {'status': 'deleted'}

        if gTask['status'] != 'deleted':
            gTasks.append(gTask)
            gTasksListIds.append(gTasksListId)
        else:
            continue

gTasksNames = []
gTasksDates = []
gTasksDescriptions = []
gTasksStatuses = [gTask['status'] for gTask in gTasks]
gTasksIds = [gTask['id'] for gTask in gTasks]
gTasksLastUpdatedDates = [convertTimeZone(parseDateTimeString(gTask['updated'][:-5], '%Y-%m-%dT%H:%M:%S')) for gTask in gTasks]
notionListNames = [listDictionaryKeys[listDictionaryValues.index(gTasksListId)] for gTasksListId in gTasksListIds]

for gTask in gTasks:
    try:
        gTasksNames.append(gTask['title'])
    except:
        gTasksNames.append('No Title')

    try:
        gTasksDates.append(parseDateTimeString(gTask['due'], '%Y-%m-%dT%H:%M:%S.000Z'))
    except:
        gTasksDates.append('')

    try:
        gTasksDescriptions.append(gTask['notes'])
    except:
        gTasksDescriptions.append('')

# Compare the Google Task last updated time to the 'Last Synced' time in Notion
# If the Google Tasks last updated time is greater than the 'Last Synced' time, then the task needs to be updated in Notion

updatedGTasksIndicies = []

for i in range(len(gTasks)):
    if gTasksLastUpdatedDates[i] > notionPageLastSyncedDates[i]:
        updatedGTasksIndicies.append(i)

if len(updatedGTasksIndicies) > 0:
    for index in updatedGTasksIndicies:
        # Update the Notion task
        updatedNotionTask = updateNotionTask(gTasksNames[index], gTasksDates[index], gTasksDescriptions[index], notionListNames[index], notionPageIds[index], gTasksIds[index], gTasksListIds[index], gTasksStatuses[index])
    print("Finished updating Notion tasks that were changed in Google Tasks!\n")
else:
    print("No Notion tasks to update\n")
