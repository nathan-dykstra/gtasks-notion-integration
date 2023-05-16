from datetime import datetime
from setup import *
from helperFunctions import *


#################################################
### PART 3: IMPORT NEW GOOGLE TASKS TO NOTION ###
#################################################


print("Adding new Google Tasks to Notion...\n")

# Get all synced Notion tasks that aren't deleted

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

gTasksIdsInNotion = [makeOneLinePlainText(page['properties'][NOTION_GTASKS_TASK_ID]['rich_text']) for page in notionPages['results']]

# Get all task info from Google Tasks

gTasks = []
gTasksListIds = []

for tasklist in LIST_DICTIONARY.keys(): # Only get Google Tasks info for lists of interest
    maxDate = addTimeZoneForNotion(dateTimeToString(datetime.now() + timedelta(weeks=FUTURE_WEEKS_TO_SYNC)))
    minDate = addTimeZoneForNotion(dateTimeToString(datetime.now() - timedelta(weeks=PAST_WEEKS_TO_SYNC)))

    if PAST_WEEKS_TO_SYNC >= 0 and FUTURE_WEEKS_TO_SYNC >= 0:
        gTasksResults = service.tasks().list(tasklist=LIST_DICTIONARY[tasklist], maxResults=500, showHidden=True, showDeleted=False, dueMax=maxDate, dueMin=minDate).execute()
    elif PAST_WEEKS_TO_SYNC >= 0:
        gTasksResults = service.tasks().list(tasklist=LIST_DICTIONARY[tasklist], maxResults=500, showHidden=True, showDeleted=False, dueMin=minDate).execute()
    elif FUTURE_WEEKS_TO_SYNC >= 0:
        gTasksResults = service.tasks().list(tasklist=LIST_DICTIONARY[tasklist], maxResults=500, showHidden=True, showDeleted=False, dueMax=maxDate).execute()
    else:
        gTasksResults = service.tasks().list(tasklist=LIST_DICTIONARY[tasklist], maxResults=500, showHidden=True, showDeleted=False).execute()

    allGTasks = service.tasks().list(tasklist=LIST_DICTIONARY[tasklist], maxResults=500, showHidden=True, showDeleted=False).execute()
    gTasksWithoutDates = [gTask for gTask in allGTasks['items'] if 'due' not in gTask]
    gTasksResults['items'].extend(gTasksWithoutDates)
    
    for item in gTasksResults['items']:
        gTasks.append(item)
        gTasksListIds.append(LIST_DICTIONARY[tasklist])
    
# Get the keys and values from tasklist dictionary
listDictionaryKeys = list(LIST_DICTIONARY.keys())
listDictionaryValues = list(LIST_DICTIONARY.values())

gTasksNames = []
gTasksDates = []
gTasksDescriptions = []
gTasksStatuses = [gTask['status'] for gTask in gTasks]
gTasksIds = [gTask['id'] for gTask in gTasks]
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

# Compare the task IDs from Google Tasks to the task IDs currently in Notion
# If a task ID from Google Tasks does not exist in Notion, then that task should be added to Notion

newGTasksIndicies = []

for i in range(len(gTasksIds)):
    if gTasksIds[i] not in gTasksIdsInNotion:
        newGTasksIndicies.append(i)

if len(newGTasksIndicies) > 0:
    for index in newGTasksIndicies:
        # Create the Notion Task
        newNotionTask = makeNotionTask(gTasksNames[index], gTasksDates[index], gTasksDescriptions[index], notionListNames[index], gTasksIds[index], gTasksListIds[index], gTasksStatuses[index])
    
    print("Finished adding new Google Tasks to Notion!\n")
else:
    print("No new Google Tasks to add to Notion\n")
