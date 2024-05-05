# gtasks-notion-integration

## Overview

This integration between Notion and Google Tasks provides free, unlimited two-way synchronization between your Notion Tasks database and your Google Tasks.

I have built a Google Calendar integration as well available [here](https://github.com/nathan-dykstra/gcal-notion-integration).

## Features
- Sync Google Tasks to Notion task database.
  - Synced tasks will be updated in Notion if you change them in Google Tasks.
  - No limit on what tasks will be synced - you can even sync your past tasks if you want!
- Sync Notion tasks to Google Tasks.
  - Synced tasks will be updated in Google Tasks if you change them in Notion.
- Syncs the following properties: task name, status (see limitations), and some other properties that make the integration work.
- Multiple List support:
  - Specify each Google Tasks list you want to sync with Notion, and the program will only look in those lists when adding/updating tasks.
  - Supports changing tasks from one list to another.
- Syncs deleted tasks* (see [Limitations](#limitations)).
- Ability to add date ranges so the program will only sync tasks that are a specified number of weeks into the past/future - makes the program run much quicker.
- Ability to run individual sections of the code separately (the code is broken into five main steps). For example, you can just do a one-time import of your Google Tasks to Notion. See [Usage Notes](#usage-notes).
- Run the program at scheduled intervals using tools like Windows Event Scheduler (instructions will be included in the setup documentation).

## Limitations
- You will have to use my Notion tasks database template available [here](https://nathan-dykstra-personal.notion.site/578e5103911b42bb96809909f1de7325?v=8bcec2b2cf384b6bb256c7694fa052c5&pvs=73).
- Google API limitations means I can't sync the time part of a Notion task date to Google Tasks (i.e. only the date gets synced, not the date and time). Will attempt to fix this in the future if there is an API update.
- The "Status" property syncs only To-do and Completed statuses because Google Tasks does not have intermediate stages (like in progress/on hold).
- Does not sync the "Priority" or "Tags" properties from Notion to Google Tasks (these features are not available in Google Tasks)
- The Notion API does not allow deleting pages, so deleted tasks will have the "deleted" checkbox checked in Notion
    - If you check this box in Notion, the corresponding task will actually be deleted in Google Tasks

## Setup Instructions

Step-by-step setup instructions will be available shortly. The setup process will probably take around 30 minutes.

## Usage Notes
To run: 
```sh
python syncGTasksAndNotion.py
```
- To run each individual section separately: 
  - Sync deleted tasks only: `python syncDeletions.py`
  - Import tasks from Notion to Google Tasks: `python importToGTasks.py`
  - Import tasks from Google Tasks to Notion: `python importToNotion.py`
  - Sync updates from Notion to Google Tasks: `python updateGTasks.py`
  - Sync update from Google Tasks to Notion: `python updateNotion.py`
- You'll have to re-authenticate your Google account every few weeks.
  - You can manually re-authenticate by running `python gTasksApiToken.py`, just like you did when you set it up.
- You'll notice that several properties are hidden by default in the Notion tasks pages. They help facilitate the sync and are updated automatically when running the program. Please do not edit the content of those properties, or the program might not function correctly!
