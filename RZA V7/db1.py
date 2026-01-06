import sqlite3

#Create connection to DB
conn = sqlite3.connect("zoo.db")
cursor = conn.cursor()

#Creates a table called users in zoo database if it doesnt already exist

#cursor.execute(''' CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,email TEXT, password TEXT, firstname TEXT, lastname TEXT, address TEXT)''')

#creates a table thats called users in the zoo db that has an ID that goes by itself as a new user is created and is the primary key, includes an email and password that is hashed as well as other info.

# appended table to add users points column for point system (rewards)
cursor.execute('''ALTER TABLE users ADD COLUMN user_points INTEGER DEFAULT 0''')
conn.commit()
conn.close()

