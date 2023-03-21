# notion-automation
 
### This repository contains
- A set of methods for interacting with Notion's API
  - get databases, pages, and blocks
  - create new pages in a database
  - append blocks to pages
  - update the properties on a page
- A main function that when run:
  - Creates a new journal entry in my Journal Database
    - ensures the correct template is used
    - only 1 page is created per day
    - calendar events from all my Google Calendars are automatically added
  - Pulls data from Goodreads and compares with my Notion Reading List
    - Updates existing entires with dates and ratings
    - Adds nonexistant books to the database


### Requirements
- This code requires some configuration files to work:
  - a `.env` file containing a Notion Integration `secret_key` in the form:
    - `token = 'secret_key'`
  - a `gcal_client_secret.json` file that contains the Google Auth 2.0 Client ID and Client secret for `InstalledAppFlow.from_client_secrets_file`, downloaded directly from `console.cloud.google.com/apis/credentials`
  - These files should be stored at `project_dir/credentials/`

### Work in Progress
- [x] Add calendar integration for events
- [x] Add proper tags based on template
- [x] Goodreads web scraper integration for my reading list
- [] Add testing suite
