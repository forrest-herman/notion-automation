# notion-automation
 
### This repository contains
- A set of methods for interacting with Notion's API
  - get databases, pages, and blocks
  - create new pages in a database
  - append blocks to pages
- A main function that when run, creates a new journal entry in my Journal Database
  - ensures the correct template is used
  - only 1 page is created per day


### Requirements
- This code requires a config.py file containing a Notion Integration `secret_key` in the form:
  - `token = 'secret_key'`

### Work in Progress
- [ ] Add calendar integration for events
- [ ] Add proper tags based on template
