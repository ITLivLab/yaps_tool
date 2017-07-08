Yet Another Pastebin Scraping tool
--------------------------------------

This is another Pastebin Scraping tool written in Python. It's not fancy but it does the job.

**Features**:
 - Email Alerts
 - Saves metadata and the pastes
 - Uses Pastebin Pro Scraping API

Note: ALL pastes are saved.

**Setup**:
 1. Sign up for Pastebin Pro
 2. White List your IP address: https://pastebin.com/api_scraping_faq
 3. Clone this repository
 4. Open yaps_tool.py and edit the configuration variables on the top
 5. Configure regex.conf with the terms you want to search for. You can use this tool to build your regex and test it: https://regex101.com/
 6. That's all! Start screen or tmux and run yaps_tool.py

Example regex file:

    $ cat regex.conf
    iupui.edu
    3AhYA82DBQsfv9tDV25DrhLC

Email alert body:

    Paste key: cgV4Aq50
    Matches:
    {'3AhYA82DBQsfv9tDV25DrhLC': 1, 'iupui.edu': 4}

**Design Decisions**:
Project needed to be really simple. Recommendations from Pastebin Scraping API page were used. New paste key is saved into SQLite3 database after they're compared with the most recent 100 keys. New paste and paste metadata is saved in a folder titled with the current date. Semaphores are used to make sure regex searcher only starts a limited amount of searches at once (https://stackoverflow.com/a/42174512).

License: WTFPL
