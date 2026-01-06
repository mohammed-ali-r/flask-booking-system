import sqlite3
import datetime

def create_initial_bookings(db_file, num_days=365):

    today = datetime.date.today()
    start_date = today

    
    conn = sqlite3.connect("zoo.db")
    cursor = conn.cursor()


    # Insert booking entries for the next 'num_days'
    for i in range(num_days):
        date = start_date + datetime.timedelta(days=i)
        cursor.execute("INSERT INTO availablezoo (Date) VALUES (?)", (date,))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_initial_bookings("zoo.db")  # Replace with your actual database file path
