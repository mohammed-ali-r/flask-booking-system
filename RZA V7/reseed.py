import sqlite3
import datetime

DB_FILE = "zoo.db"        # database your app is using
DAYS_AHEAD = 180          # how many future days to seed
DEFAULT_SLOTS = 250       # slots per day

def reseed_availability():
    today = datetime.date.today()
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()

    # Ensure table exists with good schema
    cur.execute("""
    CREATE TABLE IF NOT EXISTS availablezoo (
        Date TEXT PRIMARY KEY,
        Slots INTEGER NOT NULL DEFAULT 250
    )
    """)

    # Remove all past dates
    cur.execute("DELETE FROM availablezoo WHERE Date < ?", (today.isoformat(),))

    # Insert future dates
    for i in range(DAYS_AHEAD):
        d = today + datetime.timedelta(days=i)
        cur.execute(
            "INSERT OR IGNORE INTO availablezoo(Date, Slots) VALUES (?, ?)",
            (d.isoformat(), DEFAULT_SLOTS)
        )

    con.commit()
    con.close()
    print(f"✅ Reseeded from {today.isoformat()} for {DAYS_AHEAD} days with {DEFAULT_SLOTS} slots each.")

if __name__ == "__main__":
    reseed_availability()
