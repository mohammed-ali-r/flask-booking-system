import sqlite3

#Create connection to DB
conn = sqlite3.connect("zoo.db")
cursor = conn.cursor()

#Creates a table called availablezoo in zoo database if it doesnt already exist

cursor.execute(''' CREATE TABLE IF NOT EXISTS availablezoo(AvailabliltyID INTEGER PRIMARY KEY AUTOINCREMENT,Slots INTEGER DEFAULT 250, Date INTEGER)''')