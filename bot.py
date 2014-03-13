## reddit bot that will connect to a mysql db, grab twitch streamers, connect to api, then update sidebar with online streamers
## created by /u/zpoon, with help from /u/Deimorz

import time
import praw
import json
import urllib
import HTMLParser
import pymysql
import re
from datetime import datetime

twitch_string = ''

## Configs, be sure to modify these!!

dbhost = 'database host'
db_user = 'database username'
db_pass = 'database password'
db_database = 'selected database'

reddit_useragent = 'Enter a reddit useragent string that will identify your bot with the reddit API'
reddit_user = 'reddit username'
reddit_pass = 'reddit password'

TwitchAPI_clientID = 'Enter your twitch developer client ID here'

target_subreddit = 'reddit subreddit'

## End configs

conn = pymysql.connect(host=dbhost, port=3306, user=db_user, passwd=db_pass, db=db_database)

with conn: 

    cur = conn.cursor()
    ## You might need to modify this to make it work with your db
    cur.execute("SELECT displaychannel FROM stream_approve")

    rows = cur.fetchall()

    twitch_string = ''.join(map(str, rows))
    twitch_string = twitch_string.translate(None, '()\'')

twitchAPI = "https://api.twitch.tv/kraken/streams/?channel=" + twitch_string + "&?client_id=" + TwitchAPI_clientID

r = praw.Reddit(reddit_useragent)
r.login(reddit_user, reddit_pass)

subreddit = r.get_subreddit(target_subreddit)


response = urllib.urlopen(twitchAPI)
data = json.loads(response.read().decode('utf8'))

if data['_total'] > 0:
    for stream in data['streams']:
        viewCount = str(stream['viewers'])
        payload += '>[' + stream['channel']['name'] + '](' + stream['channel']['url'] + ')\n\n'
        payload += '>***************\n\n'
else:
    payload = '>No streams\n\n'
payload += '>last updated: ' + time.strftime("%b %d %H:%M:%S") + '\n'

current_sidebar = subreddit.get_settings()['description']
current_sidebar = HTMLParser.HTMLParser().unescape(current_sidebar)
replace_pattern = re.compile('%s.*?%s' % (re.escape('[](/twitch)'), re.escape('[](/twitch-end)')), re.IGNORECASE|re.DOTALL|re.UNICODE)
new_sidebar = re.sub(replace_pattern,'%s\\n\\n%s\\n%s' % ('[](/twitch)', payload, '[](/twitch-end)'), current_sidebar)

subreddit.update_settings(description=new_sidebar)
payload = ""