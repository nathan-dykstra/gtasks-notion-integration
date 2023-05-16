

#####################
### INITIAL SETUP ###
#####################


# Path to the folder you created for this project (include the trailing '/')
PROJECT_LOCATION = ''

# Whether or not to sync deleted tasks
# If this is set to "False", then the program will not sync deleted tasks
# If this is set to "True", then the program will sync deleted tasks
SYNC_DELETED_TASKS = True

# ----------------------------------------- NOTION SETUP ------------------------------------------

NOTION_TOKEN = ''

# Database ID of Notion Calendar database (everything between 'https://www.notion.so/my-notion-workspace/' and '?v=...', exclusive)
NOTION_DATABASE_ID = ''

# URL root of new page in Notion Calendar database (everything up to and including '&p=')
NOTION_PAGE_URL_ROOT = ''

# ------------------------------------- GOOGLE TASKS SETUP -------------------------------------

# Choose your timezone (use the link below to find your timezone)
# http://www.timezoneconverter.com/cgi-bin/zonehelp.tzc
TIMEZONE = 'America/Toronto'

# The timezone difference between GMT and your timezone.
# For example, the offset for EDT is '-04:00' and the offset for EST '-05:00'.
# If your timezone has time changes, then you will have to update this (for example Eastern Time changes from EST to EDT)
TIMEZONE_OFFSET_FROM_GMT = '-04:00'

# The number of weeks to go back in history to sync your tasks
# If this is set to -1, then the program will attempt to sync ALL your historical tasks
# If this is set to a non-negative integer, then the program will attempt to sync your tasks since PAST_WEEKS_TO_SYNC weeks ago
# Recommendation: 
#   1. The recommended value is 52 when initially running the program, to sync all your data from the past year.
#   2. The recommended value is 1 after your initial sync is complete, since you will likely only update current tasks.
PAST_WEEKS_TO_SYNC = 1

# The number of weeks to go into the future to sync your tasks
# If this is set to -1, then the program will attempt to sync ALL your future tasks
# If this is set to a non-negative integer, then the program will attempt to sync your tasks up to PAST_WEEKS_TO_SYNC weeks in the future
# Recommendation: 
#   1. The recommended value is 52 when initially running the program, to sync all your data for the upcoming year
#   2. The recommended value is 10 after your initial sync is complete
FUTURE_WEEKS_TO_SYNC = 10

# ------------------------------------ MULTIPLE LIST SETUP ------------------------------------

# Default Notion calendar name and Google Task ID
DEFAULT_LIST_NAME = ''
DEFAULT_LIST_ID = ''

# These are all of the Google Tasks Lists you want to sync with your Notion Calendar database
# Format: 'Notion Calendar Name' : 'Google Tasks List ID'
LIST_DICTIONARY = {
    DEFAULT_LIST_NAME : DEFAULT_LIST_ID,
    
}

# ------------------------------------- NOTION DATABASE SETUP -------------------------------------

# Basic task fields
NOTION_TASK_NAME = 'Summary'
NOTION_STATUS = 'Status'
NOTION_LIST_NAME = 'List'
NOTION_DATE = 'Date'
NOTION_DESCRIPTION = 'Description'
NOTION_DELETED = 'Deleted'

# Additional fields to facilitate the integration
NOTION_SYNCED = 'Synced'
NOTION_NEEDS_GTASKS_UPDATE = 'Needs GTasks Update'
NOTION_GTASKS_TASK_ID = 'GTasks Task ID'
NOTION_GTASKS_LIST_ID = 'GTasks List ID'
NOTION_LAST_SYNCED = 'Last Synced'

# Notion task statuses
# If you customzie the status options in your Notion tasks database, you will need to modify them here as well
# If you keep the statuses the same as my database template, then you don't need to change these

# To-do statuses:
NOTION_TO_DO_STATUSES = ['To-do']

# In progress statuses:
NOTION_IN_PROGRESS_STATUSES = ['In progress', 'On hold']

# Complete statuses: 
NOTION_COMPLETE_STATUSES = ['Done']

NOTION_DEFAULT_STATUS = 'To-do'

# ------------------------------ ADDITIONAL CONSTANTS (DO NOT MODIFY) -----------------------------

# Google Tasks statuses
GOOGLE_TO_DO_STATUS = 'needsAction'
GOOGLE_DONE_STATUS = 'completed'
