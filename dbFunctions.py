"""
The purpose of this file is to handle database inserts and deletions
using various functions. These functions are called in our routes
file, myproject.py
"""
import sqlite3

def get_db_connection():
    """
    This function opens a connection to our database.db and returns the connection
    get_db_connection is called by all other functions in this file.
    """
    conn = sqlite3.connect('/home/emma/myproject/database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_stories():
    """
    This function gets all stories from the "stories" table of database.db and
    organizes them by date. The stories are returned.
    """
    conn = get_db_connection()
    stories = conn.execute('SELECT * FROM stories ORDER BY storyDate DESC').fetchall()
    conn.close()
    return stories

def get_users():
    """
    This function gets all users from database.db and returns them.
    """
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return users

def get_user(user_ID):
    """
    This function gets a specific user using the user_ID, which is the user email.
    The user is returned from the users table.
    """
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', [user_ID]).fetchall()
    conn.close()
    return user

def get_likes():
    """
    This function gets all entries in the liked table and returns them.
    """
    conn = get_db_connection()
    likes = conn.execute('SELECT * FROM liked').fetchall()
    conn.close()
    return likes

def get_dislikes():
    """
    This function gets all entries in the disliked table of database.db annd returns them.
    """
    conn = get_db_connection()
    dislikes = conn.execute('SELECT * FROM disliked').fetchall()
    conn.close()
    return dislikes

def add_user(userID, name, admin):
    """
    This function will add a user into the database if they are not already present.
    userID, name, and admin are passed in as email, name, and admin in the users table.
    """
    if check_user(userID) == False:
        conn = get_db_connection()
        conn.execute("INSERT INTO users (email, name, admin) VALUES (?, ?, ?)", (userID, name, admin))
        conn.commit()
        conn.close()

def check_user(userID):
    """
    This function will check if a user is present in the database passing the userID in the query.
    The length of result is checked for conditional.
    """
    conn = get_db_connection()
    result = conn.execute("SELECT rowid FROM users WHERE email = ?", ([userID])).fetchall()
    conn.close()
    if len(result) == 0:
        return False
    else:
        return True

def check_admin(userID):
    """
    This function checks if a user who is also an admin is already present in the database.
    The length of result is checked in the conditional.
    """
    conn = get_db_connection()
    result = conn.execute("SELECT rowid FROM users WHERE email = ? AND admin = ?", (userID, 1)).fetchall()
    conn.close()
    if len(result) == 0:
        return False
    else:
        return True

def check_like(story_ID, user_ID):
    """
    This function checks the liked table for an already present like by an associated
    storyID and userID.
    If len(result) == 0, then it is not present in the database.
    """
    conn = get_db_connection()
    result = conn.execute("SELECT rowid FROM liked WHERE storyID = ? AND userID = ?", (story_ID, user_ID)).fetchall()
    conn.close()
    if len(result) == 0:
        return False
    else:
        return True

def check_dislike(story_ID, user_ID):
    """
    This function does the same as the check_like function however for dislikes in the disliked
    table.
    """
    conn = get_db_connection()
    result = conn.execute("SELECT rowid FROM disliked WHERE storyID = ? AND userID = ?", (story_ID, user_ID)).fetchall()
    conn.close()
    if len(result) == 0:
        return False
    else:
        return True

def add_like(story_ID, user_ID, title):
    """
    This function will add a like after checking if the associated storyID and userID
    is present in the disliked table. If so, delete the dislike and insert storyID and userID
    into liked. Then updates the associated storyID with + 1 likes in stories.
    """
    if check_dislike(story_ID, user_ID) == True:
        delete_dislike(story_ID, user_ID)
    if check_like(story_ID, user_ID) == False:
        conn = get_db_connection()
        conn.execute("INSERT INTO liked (storyID, userID, title) VALUES (?, ?, ?)", (story_ID, user_ID, title))
        conn.execute('UPDATE stories SET likes = likes+1 WHERE storyID = ?', [story_ID])
        conn.commit()
        conn.close()

def add_dislike(story_ID, user_ID, title):
    """
    Does the same as add_like but opposite for dislikes. Checks if the user already liked the
    disliked story, if so delete from the liked table. If the user has not disliked the story,
    the userID and storyID are inserted into the disliked tabe and the associated story is
    updated with + 1 dislikes in the stories table.
    """
    if check_like(story_ID, user_ID) == True:
        delete_like(story_ID, user_ID)
    if check_dislike(story_ID, user_ID) == False:
        conn = get_db_connection()
        conn.execute("INSERT INTO disliked (storyID, userID, title) VALUES (?, ?, ?)", (story_ID, user_ID, title))
        conn.execute('UPDATE stories SET dislikes = dislikes+1 WHERE storyID = ?', [story_ID])
        conn.commit()
        conn.close()

def delete_dislike(story_ID, user_ID):
    """
    This function will delete an entry in the disliked table with the associated user and story.
    Stories table is updated where the storyID dislikes are updated with dislikes - 1.
    """
    conn = get_db_connection()
    conn.execute("DELETE FROM disliked WHERE storyID = ? AND userID = ?", (story_ID, user_ID))
    conn.execute('UPDATE stories SET dislikes = dislikes-1 WHERE storyID = ?', [story_ID])
    conn.commit()
    conn.close()

def delete_like(story_ID, user_ID):
    """
    Does the same as delete_dislike but opposite for likes. Will delete associated storyID and
    userID from liked table in database. StoryID from stories table is updated with dislikes - 1.
    """
    conn = get_db_connection()
    conn.execute("DELETE FROM liked WHERE storyID = ? AND userID = ?", (story_ID, user_ID))
    conn.execute('UPDATE stories SET likes = likes-1 WHERE storyID = ?', [story_ID])
    conn.commit()
    conn.close()
