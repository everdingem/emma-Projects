"""
The purpose of this file is to get stories and URLs from the hackernews API
and insert the stories into database.db.
"""
import requests
import json
import sqlite3
import datetime

response_API = requests.get('https://hacker-news.firebaseio.com/v0/newstories.json?print=pretty&orderBy="$priority"&limitToFirst=50')
data = response_API.text
parse_json = json.loads(data)

#Create database file
connection = sqlite3.connect('database.db')

#Run script to create db table
with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("DELETE FROM stories WHERE likes = 0")

#Loops through story ID list to get story titles & urls
for x in range(0, 50):
    stories_response = requests.get('https://hacker-news.firebaseio.com/v0/item/{}.json?print=pretty'.format(parse_json[x]))
    data = stories_response.text
    parse_json_stories = json.loads(data)
    if 'url' in parse_json_stories:
        story_author = parse_json_stories['by']
        story_date = parse_json_stories['time']
        story_url = parse_json_stories['url']
        story_title = parse_json_stories['title']
    else:
        continue

    #Adds story to table
    cur.execute("SELECT rowid FROM stories WHERE storyID = ?", (parse_json[x],))
    result = cur.fetchall()
    if len(result) == 0:
        cur.execute("INSERT INTO stories (storyID, title, url, storyDate, author, likes, dislikes) VALUES (?, ?, ?, ?, ?, ?, ?)",\
                (parse_json[x], story_title, story_url, datetime.datetime.fromtimestamp(story_date), story_author, 0, 0))

#Close connection
connection.commit()
connection.close()
