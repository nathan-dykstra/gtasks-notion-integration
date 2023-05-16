from setup import *
from helperFunctions import *


##################################
### PART 1: SYNC DELETED TASKS ###
##################################


print("Updating tasks that were deleted...\n")

# Delete Google Tasks where the 'Deleted' checkbox is checked in Notion

query = {
    'database_id': NOTION_DATABASE_ID,
    'filter': {
        'and':[
            {
                'property': NOTION_GTASKS_TASK_ID,
                'rich_text': {
                    'is_not_empty': True
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
                    'equals': True
                }
            },
            {
                'property': NOTION_NEEDS_GTASKS_UPDATE,
                'checkbox': {
                    'equals': True
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

deletedNotionPages = notion.databases.query(
    **query
)
nextCursor = deletedNotionPages['next_cursor']

while deletedNotionPages['has_more']:
    query['start_cursor'] = nextCursor
    moreDeletedNotionPages = notion.databases.query(
        **query
    )
    nextCursor = moreDeletedNotionPages['next_cursor']
    deletedNotionPages['results'] += moreDeletedNotionPages['results']
    if nextCursor is None:
        break

for i, deletedPage in enumerate(deletedNotionPages['results']):
    gTasksListId = makeOneLinePlainText(deletedPage['properties'][NOTION_GTASKS_LIST_ID]['rich_text'])
    gTasksId = makeOneLinePlainText(deletedPage['properties'][NOTION_GTASKS_TASK_ID]['rich_text'])
    deletedPageName = deletedPage['properties'][NOTION_TASK_NAME]['title'][0]['plain_text']

    try:
        print(f'Deleting this task from Google Tasks: {deletedPageName}\n')
        service.tasks().delete(tasklist=gTasksListId, task=gTasksId).execute() 
    except:
        print(f'Could not delete this task from Google Tasks: {deletedPageName}\n')

    notionPageUpdate = notion.pages.update(
        **{
            'page_id': deletedPage['id'],
            'properties': {
                NOTION_LAST_SYNCED: {
                    'date': {
                        'start': addTimeZoneForNotion(nowToDateTimeString()),
                        'end': None
                    }
                }
            }
        }
    )

# Check off the 'Deleted' checkbox for tasks that were deleted in Google Tasks

deletedGTasks = []

for tasklist in LIST_DICTIONARY.keys(): # Only get Google Tasks info for lists of interest
        maxDate = addTimeZoneForNotion(dateTimeToString(datetime.now() + timedelta(weeks=FUTURE_WEEKS_TO_SYNC)))
        minDate = addTimeZoneForNotion(dateTimeToString(datetime.now() - timedelta(weeks=PAST_WEEKS_TO_SYNC)))

        if PAST_WEEKS_TO_SYNC >= 0 and FUTURE_WEEKS_TO_SYNC >= 0:
            gTasksResults = service.tasks().list(tasklist=LIST_DICTIONARY[tasklist], maxResults=500, showHidden=True, showDeleted=True, dueMax=maxDate, dueMin=minDate).execute()
        elif PAST_WEEKS_TO_SYNC >= 0:
            gTasksResults = service.tasks().list(tasklist=LIST_DICTIONARY[tasklist], maxResults=500, showHidden=True, showDeleted=True, dueMin=minDate).execute()
        elif FUTURE_WEEKS_TO_SYNC >= 0:
            gTasksResults = service.tasks().list(tasklist=LIST_DICTIONARY[tasklist], maxResults=500, showHidden=True, showDeleted=True, dueMax=maxDate).execute()
        else:
            gTasksResults = service.tasks().list(tasklist=LIST_DICTIONARY[tasklist], maxResults=500, showHidden=True, showDeleted=True).execute()

        for item in gTasksResults['items']:
            try: # Only deleted Google Tasks have the 'deleted' key, so the try & except block is necessary to catch key errors on tasks that aren't deleted
                if item['deleted'] == True:
                    deletedGTasks.append(item)
            except:
                continue
for deletedGTask in deletedGTasks:
    deletedGTaskId = deletedGTask['id']
    
    notionPagesToDelete = notion.databases.query(
        **{
            'database_id': NOTION_DATABASE_ID,
            'filter': {
                'and': [
                    {
                        'property': NOTION_GTASKS_TASK_ID,
                        'rich_text': {
                            'equals': deletedGTaskId
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
    )

    for notionPageToDelete in notionPagesToDelete['results']:
        print(f'Deleting this task in Notion: {deletedGTaskId}\n')

        notionPageUpdate = notion.pages.update(
            **{
                'page_id': notionPageToDelete['id'],
                'properties': {
                    NOTION_DELETED: {
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

print("Finished updating tasks that were deleted!\n")
