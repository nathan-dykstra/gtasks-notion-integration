from datetime import date, datetime, timedelta
from pytz import timezone, utc
from setup import *
from apiConnections import *


########################
### HELPER FUNCTIONS ###
########################


def nowToDateTimeString():
    """Returns the current date and time as a string"""

    # Note: Adding the timedelta of +1 minute prevents events in both Google Calendar and Notion Calendar from having 
    # last updated times that are greater than the last synced time.
    now = datetime.now() + timedelta(minutes=1)
    return now.strftime('%Y-%m-%dT%H:%M:%S')


def dateTimeToString(dateTime):
    """
    Returns dateTime as a string
    Required: dateTime is a datetime object
    """

    return dateTime.strftime('%Y-%m-%dT%H:%M:%S')


def dateToString(date):
    """
    Returns date as a string
    Required: date is a date/datetime object
    """

    return date.strftime('%Y-%m-%d')
    

def parseDateTimeString(dateTimeString, format):
    """
    Returns dateTimeString as a datetime object with date and time
    Required: dateTimeString follows the specified format
    """

    return datetime.strptime(dateTimeString, format)


def parseDateString(dateString, format):
    """
    Returns dateString as a datetime object with date only
    Required: dateString follows the specified format
    """

    return datetime.strptime(dateString, format)#.date()


def addTimeZoneForNotion(dateTimeString):
    """Adds timezone indicator to dateTimeString (for ET this will be -04:00 or -05:00)"""

    return dateTimeString + TIMEZONE_OFFSET_FROM_GMT


def convertTimeZone(dateTime, newTimeZone=TIMEZONE):
    """
    Convert dateTime from UTC to newTimeZone
    Requires: dateTime is a datetime object of the form '%Y-%m-%dT%H:%M:%S'
    """

    return utc.localize(dateTime).astimezone(timezone(newTimeZone)).replace(tzinfo=None)


def getGoogleMeetId(link):
    """Returns the Google Meet ID (everything after https://meet.google.com/)"""

    link.split('https://meet.google.com/', 1)[1]


def makeNotionPageURL(pageId, urlRoot):
    """Returns a URL to the Notion page"""

    urlId = pageId.replace('-', '')
    return urlRoot + urlId


def makeDescription(richText):
    """Returns a plain text description from Notion's rich text field"""

    description = ""
    for item in richText:
        description += item['text']['content']
    return description


def makeOneLinePlainText(richText):
    """Returns a single line of plain text from Notion's rich text field"""

    return richText[0]['plain_text']


def makeLink(richText):
    """Returns a Python List with the following format: [Display text, URL]"""

    return [richText[0]['text']['content'], richText[0]['text']['link']['url']]

def makeGoogleTask(taskName, taskDescription, taskDate, gTasksListId, taskStatus):
    """Creates a new Google Task and returns the task"""

    task = {
        'title': taskName,
        'notes': taskDescription,
        'status': taskStatus
    }

    # Two cases for the due dates:
    #   1. No due date was specified in Notion
    #   2. The due date is a date object (Google Tasks API does not allow reading/writing the time part)
    if isinstance(taskDate, date):
        taskDate = datetime.combine(taskDate, datetime.min.time())
        task['due'] = addTimeZoneForNotion(dateTimeToString(taskDate))
    
    # Note: Google Tasks API currently only allows setting the date (not time) for when the task is due
    # Two cases for the due dates:
    #   1. Date with time
    #   2. Date without time
    #if isinstance(taskDate, datetime):
    #    task['due'] = dateToString(taskDate)
        #{
        #    'date': dateTimeToString(taskDate),
        #    'timeZone': TIMEZONE
        #}
    #else:
    #    task['due'] = dateToString(taskDate)
     
    print(f'Adding this event to Google Tasks: {taskName}\n')

    newTask = service.tasks().insert(tasklist=gTasksListId, body=task).execute()
    return newTask

def makeNotionTask(taskName, taskDate, taskDescription, notionList, gTasksId, gTasksListId, gTasksStatus):
    """Creates a new Notion task and returns the task"""

    notionStatus = ''
    if gTasksStatus == GOOGLE_TO_DO_STATUS:
        notionStatus = NOTION_TO_DO_STATUSES[0]
    else:
        notionStatus = NOTION_COMPLETE_STATUSES[0]

    newNotionTask = notion.pages.create(
        **{
            'parent': {
                'database_id': NOTION_DATABASE_ID
            },
            'properties': {
                NOTION_TASK_NAME: {
                    'title': [
                        {
                            'text': {
                                'content': taskName
                            }
                        }
                    ]
                },
                NOTION_LIST_NAME: {
                    'select': {
                        'name': notionList
                    }
                },
                NOTION_STATUS: {
                    'status': {
                        'name': notionStatus
                    }
                },
                NOTION_DESCRIPTION: {
                    'rich_text': [{
                        'text': {
                            'content': taskDescription
                        }
                    }]
                },
                NOTION_SYNCED: {
                    'checkbox': True
                },
                NOTION_GTASKS_TASK_ID: {
                    'rich_text': [{
                        'text': {
                            'content': gTasksId
                        }
                    }]
                },
                NOTION_GTASKS_LIST_ID: {
                    'rich_text': [{
                        'text': {
                            'content': gTasksListId
                        }
                    }]
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
    
    # Two cases for the due dates:
    #   1. No due date was specified in Notion
    #   2. The due date is a date object (Google Tasks API does not allow reading/writing the time part)
    if isinstance(taskDate, date):
        notionTaskUpdate = notion.pages.update(
            **{
                'page_id': newNotionTask['id'],
                'properties': {
                    NOTION_DATE: {
                        'date': {
                            'start': dateToString(taskDate),
                            'end': None
                        }
                    }
                }
            }
        )

    print(f'Adding this task to Notion: {taskName}\n')
    return newNotionTask


def updateGoogleTask(taskName, taskDescription, taskDate, currentGTasksListId, newGTasksListId, gTasksId, taskStatus):
    """Updates the Google Task and returns the task"""

    updatedTask = {
        'title': taskName,
        'id': gTasksId,
        'notes': taskDescription,
        'status': taskStatus
    }

    # Two cases for the due dates:
    #   1. No due date was specified in Notion
    #   2. The due date is a date object (Google Tasks API does not allow reading/writing the time part)
    if isinstance(taskDate, date):
        taskDate = datetime.combine(taskDate, datetime.min.time())
        updatedTask['due'] = addTimeZoneForNotion(dateTimeToString(taskDate))
    
    # Note: Google Tasks API currently only allows setting the date (not time) for when the task is due
    # Two cases for the due dates:
    #   1. Date with time
    #   2. Date without time
    #if isinstance(taskDate, datetime):
    #    task['due'] = dateToString(taskDate)
        #{
        #    'date': dateTimeToString(taskDate),
        #    'timeZone': TIMEZONE
        #}
    #else:
    #    task['due'] = dateToString(taskDate)

    print(f'Updating this event in Google Tasks: {taskName}\n')

    # Notes:
    #   1. currentGTasksTaskId is the Google Tasks List ID saved in the 'GTasks List ID' field in Notion
    #   2. newGTasksListId is the Google Tasks List ID associated with the 'List' field in Notion
    #   3. If the 'List' field in Notion is changed, then its associated Google Tasks List ID will not match the 'GTasks List ID' field
    if currentGTasksListId == newGTasksListId:
        updatedTask = service.tasks().update(tasklist=currentGTasksListId, task=gTasksId, body=updatedTask).execute()
    else: # The 'List' field was changed in Notion. Duplicate the task into new list, then delete the old one (API doesn't allow moving between lists)
        updatedTask = service.tasks().insert(tasklist=newGTasksListId , body=updatedTask).execute()
        oldTask = service.tasks().delete(tasklist=currentGTasksListId, task=gTasksId).execute()

    return updatedTask

def updateNotionTask(taskName, taskDate, taskDescription, notionList, notionPageId, gTasksId, gTasksListId, gTasksStatus):
    """Updates the Notion task and returns the task"""

    notionStatus = ''
    if gTasksStatus == GOOGLE_TO_DO_STATUS:
        notionStatus = NOTION_TO_DO_STATUSES[0]
    else:
        notionStatus = NOTION_COMPLETE_STATUSES[0]

    updatedNotionTask = notion.pages.update(
        **{
            'page_id': notionPageId,
            'properties': {
                NOTION_TASK_NAME: {
                    'title': [
                        {
                            'text': {
                                'content': taskName
                            }
                        }
                    ]
                },
                NOTION_LIST_NAME: {
                    'select': {
                        'name': notionList
                    }
                },
                NOTION_STATUS: {
                    'status': {
                        'name': notionStatus
                    }
                },
                NOTION_DESCRIPTION: {
                    'rich_text': [{
                        'text': {
                            'content': taskDescription
                        }
                    }]
                },
                NOTION_SYNCED: {
                    'checkbox': True
                },
                NOTION_GTASKS_TASK_ID: {
                    'rich_text': [{
                        'text': {
                            'content': gTasksId
                        }
                    }]
                },
                NOTION_GTASKS_LIST_ID: {
                    'rich_text': [{
                        'text': {
                            'content': gTasksListId
                        }
                    }]
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

    # Two cases for the due dates:
    #   1. No due date was specified in Notion
    #   2. The due date is a date object (Google Tasks API does not allow reading/writing the time part)
    if isinstance(taskDate, date):
        updatedNotionTaskUpate = notion.pages.update(
            **{
                'page_id': updatedNotionTask['id'],
                'properties': {
                    NOTION_DATE: {
                        'date': {
                            'start': dateToString(taskDate),
                            'end': None
                        }
                    }
                }
            }
        )

    print(f'Updating this task in Notion: {taskName}\n')
    return updatedNotionTask
