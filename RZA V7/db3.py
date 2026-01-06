import sqlite3

# Create connection to DB
conn = sqlite3.connect("zoo.db")
cursor = conn.cursor()

# Create table called zoobookings 
cursor.execute('''
    CREATE TABLE IF NOT EXISTS zoobookings (
        bookingID INTEGER PRIMARY KEY AUTOINCREMENT,
        userID INTEGER NOT NULL,
        dateID INTEGER NOT NULL,
        FOREIGN KEY (userID) REFERENCES users(id),   
        FOREIGN KEY (dateID) REFERENCES availablezoo(Date) 
        CONSTRAINT fk_user_exists FOREIGN KEY (userID) REFERENCES users(id) ON DELETE CASCADE  
    )
''')

#userID is foreign key from users ID column, #dateID is date from availablezoo date column  # Deletes booking if user is removed

conn.commit()
conn.close()
