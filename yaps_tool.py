import sqlite3, requests, time, os, datetime, threading, re, smtplib
from email.mime.text import MIMEText

dbname="test.db" #Database name
sleeptime=60 #Time to sleep between scraping
api_scraping="https://pastebin.com/api_scraping.php?limit=100" #Number of pastes to scrape
debugmsg=True #Print debug messages or not
regex_conf_file = "regex.conf"
max_search_threads = 10 #Amount of regex search threads to run at the same time

#Email alert configuration
SMTP_SERVER = 'YOUR_EMAIL_SERVER'
SMTP_PORT = 587
LOGIN_EMAIL = "pastealert@YOUR_EMAIL_SERVER"
LOGIN_PASSWORD = "hi"
RECV_EMAIL = "alert@YOUR_EMAIL_SERVER"

#Print messages
def debug(message):
    if debugmsg:
        print message

#Email function
def sendmail(targetemail,message):
    debug("Sending an email")
    server = smtplib.SMTP(SMTP_SERVER,SMTP_PORT)
    server.login(LOGIN_EMAIL,LOGIN_PASSWORD)
    msg = MIMEText(message)
    msg['From'] = LOGIN_EMAIL
    msg['To'] = targetemail
    msg['Subject'] = "Pastebin Alert"
    server.sendmail(LOGIN_EMAIL,targetemail,msg.as_string())

#Load regex configurations
debug("Loading regex conf")
regexconf = open(regex_conf_file,'r').read().strip().split('\n')

#Setup threading related things
debug("Setting up threading related things")
search_sema = threading.Semaphore(value=max_search_threads)
search_threads = list()

#Searcher
def searcher(text,paste_key):
    search_sema.acquire()
    debug("Searching key: " + paste_key)
    match_list = {}
    #Look to see which regex terms match this paste
    for regex_term in regexconf:
        if len(re.findall(regex_term,text)) > 0:
            match_list[str(regex_term)] = len(re.findall(regex_term,text))
    if len(match_list) > 0:
        sendmail(RECV_EMAIL,"Paste key: "+paste_key+"\nMatches:\n"+str(match_list))
    search_sema.release()

#Create or connect to database
if (os.path.isfile(dbname) == False):
    debug("Creating a database")
    conn = sqlite3.connect(dbname)
    conn.execute("create table pastes(id INTEGER PRIMARY KEY AUTOINCREMENT, key)")
    conn.commit()
if (os.path.isfile(dbname) == True):
    debug("Connecting to a database")
    conn = sqlite3.connect(dbname)

#Scapper loop
while True:
    debug("Scraping started")
    TODAY = str(datetime.date.today())
    #Create a directory if it does not exist
    if (os.path.isdir(TODAY) == False):
        debug("Creating a directory")
        os.system("mkdir " + TODAY)
    #Get the most recent pastes
    debug("Getting pastes from pastebin")
    recent_pastes = requests.get(api_scraping).json()
    #Get recent pastes from local sqlite database
    debug("Getting paste keys from database")
    db_keys = conn.execute("select key from pastes order by id desc limit 100").fetchall()
    #Loop through all the pastes grabbed from pastebin
    debug("Saving and searching pastes")
    for paste in recent_pastes:
        #Compare new paste keys against old ones
        if (paste['key'],) not in db_keys:
            #Add new key to the database
            conn.execute("insert into pastes(key) values (?)", (paste['key'],))
            #Save metadata and paste
            paste_content = requests.get(paste['scrape_url']).content
            writer = open(TODAY+"/"+str(paste['key']),'w')
            writer.write(paste_content)
            writer.close()
            writer = open(TODAY+"/"+str(paste['key'])+'.metadata','w')
            writer.write(str(paste))
            writer.close()
            thread = threading.Thread(target=searcher,args=(paste_content,paste['key'],))
            search_threads.append(thread)
            thread.start()
    conn.commit()
    debug("Sleeping")
    time.sleep(sleeptime)
