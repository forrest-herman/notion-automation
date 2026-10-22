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
- A set of functions for interacting with Google Firestore
- Github Actions configuration file to run this automation on a cron schedule, including webdriver and Google Auth tasks


### Requirements
- This code requires some configuration files and variables to work:
  - a `.env` file containing:
    -  a Notion Integration `secret_key` in the form:
       - `NOTION_TOKEN = 'secret_key'`
 - Github Secret `TIMEZONE` key with your local timezone string of the form `America/New_York`
  - a `gcal_client_secret.json` file that contains the Google Auth 2.0 Client ID and Client secret for `InstalledAppFlow.from_client_secrets_file`, downloaded directly from `console.cloud.google.com/apis/credentials`
  - These files should be stored at `project_dir/credentials/` or stored in Github secret

### Browser driver setup

`web_scraping.build_driver()` uses Selenium Manager to find or download a driver
for the installed browser. The first download requires access to the browser
vendor's download servers. A proxy, firewall, DNS, or certificate problem can
prevent this even when other websites work.

To use an already downloaded driver without contacting the download servers,
set its full executable path in `.env`:

```dotenv
CHROME_DRIVER_PATH=C:/tools/chromedriver.exe
# For Edge instead:
EDGE_DRIVER_PATH=C:/tools/msedgedriver.exe
```

The driver must be compatible with the installed browser version. Call
`build_driver(browser='chrome')` to explicitly select Chrome; the default remains
Edge on Windows and Chrome elsewhere.

Selenium 4.35.0 includes the updated Microsoft Edge driver download host. Older
Selenium versions such as 4.11.2 use a retired host and may report "Unable to
obtain driver" even with a working internet connection. Update the active
environment after pulling these changes:

```powershell
.\env\Scripts\python.exe -m pip install --upgrade "selenium==4.35.0" "cloudinary==1.44.1" "google-auth==2.40.3"
```

`requirements.txt` pins Selenium and its required dependencies so GitHub Actions
also installs the updated driver manager.
Cloudinary and Google Auth are updated alongside Selenium to support its required
urllib3 version.

### Goodreads login

Set `GOODREADS_EMAIL` and `GOODREADS_PASSWORD` in your local `.env` and as
GitHub Actions repository secrets with the same names. All Goodreads requests
open their target URL first. If Goodreads presents a sign-in page or visible
email-login form, the browser signs in and returns to the requested URL.
Public pages do not require credentials. No session files are saved.

To check login locally without running the Notion/Firestore updates:

```powershell
.\env\Scripts\python.exe -c "from goodreads_session import build_goodreads_driver; driver = build_goodreads_driver(); print('Goodreads login succeeded'); driver.quit()"
```

When login is required, missing credentials or a login timeout stop the scrape.
If Goodreads requests
additional verification, complete it manually and retry. Credentials and login
page HTML are not included in login failure messages.

Blank pages are given up to 15 seconds to render before the scrape stops with
an explicit error. If a URL works with `headless=False` but stays blank in
headless mode, test Chrome and Edge separately. A headed browser on a Linux
virtual display (Xvfb) is another option for unattended runs; it must use
`headless=False`, and Xvfb must be installed on the runner.

### Running tests

Install dependencies with `python -m pip install -r requirements.txt`, then run
`python -m pytest` from the repository root. GitHub Actions runs the same unit
suite without Google authentication or repository secrets.

Tests supply dummy Notion and Steam configuration, disable loading `.env`, and
reject unexpected HTTP requests and Google credential/client initialization.
External services must be mocked in tests; local credentials are not used.
Firestore initializes and caches its client only when a database operation is
requested. Production automation still requires a valid local Firebase
certificate or Application Default Credentials supplied by its Google
authentication step.

### Work in Progress
- [x] Add calendar integration for events
- [x] Add proper tags based on template
- [x] Goodreads web scraper integration for my reading list
- [ ] Add testing suite
- [x] Host online to run automatically on schedule
- [x] Integrate Cloud Firestore as storage for user_data and logs
  - [x] Create daily-automations Firebase account
  - [x] Add write and read scripts for ease of use
  - [x] Integrate into existing scripts
