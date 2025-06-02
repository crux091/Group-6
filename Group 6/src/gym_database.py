import sqlite3
import os
from datetime import datetime, timedelta

class GymDatabase:
    def __init__(self, db_name="gym_schedule.db"):
        """Initialize the database connection and create tables if they don't exist."""
        self.db_name = db_name
        # Add check_same_thread=False to allow SQLite connection to be used across threads
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """Create the necessary tables if they don't exist."""
        # Create schedule table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            capacity INTEGER DEFAULT 20,
            booked_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create admin table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        ''')
        
        # Create bookings table to track who booked what
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            schedule_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (schedule_id) REFERENCES schedule (id)
        )
        ''')
        
        # Check if admin exists, if not create default admin
        self.cursor.execute("SELECT COUNT(*) FROM admin")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("INSERT INTO admin (username, password) VALUES (?, ?)", 
                              ("admin", "admin123"))  # In production, use hashed passwords
        
        self.conn.commit()
    
    def add_schedule(self, name, date, time, capacity=20):
        """Add a new schedule entry."""
        try:
            self.cursor.execute(
                "INSERT INTO schedule (name, date, time, capacity) VALUES (?, ?, ?, ?)",
                (name, date, time, capacity)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def get_all_schedules(self):
        """Get all schedule entries."""
        self.cursor.execute(
            "SELECT id, name, date, time, capacity, booked_count FROM schedule ORDER BY date, time"
        )
        return self.cursor.fetchall()
    
    def get_schedule_by_id(self, schedule_id):
        """Get a specific schedule entry by ID."""
        self.cursor.execute(
            "SELECT id, name, date, time, capacity, booked_count FROM schedule WHERE id = ?",
            (schedule_id,)
        )
        return self.cursor.fetchone()
    
    def update_schedule(self, schedule_id, name, date, time, capacity):
        """Update an existing schedule entry."""
        try:
            self.cursor.execute(
                "UPDATE schedule SET name = ?, date = ?, time = ?, capacity = ? WHERE id = ?",
                (name, date, time, capacity, schedule_id)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def delete_schedule(self, schedule_id):
        """Delete a schedule entry."""
        try:
            # First check if there are any bookings
            self.cursor.execute("SELECT COUNT(*) FROM bookings WHERE schedule_id = ?", (schedule_id,))
            if self.cursor.fetchone()[0] > 0:
                # Delete associated bookings first
                self.cursor.execute("DELETE FROM bookings WHERE schedule_id = ?", (schedule_id,))
            
            # Then delete the schedule
            self.cursor.execute("DELETE FROM schedule WHERE id = ?", (schedule_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def book_session(self, schedule_id, customer_name, customer_email):
        """Book a session for a customer."""
        try:
            # Check if there's capacity
            self.cursor.execute(
                "SELECT capacity, booked_count FROM schedule WHERE id = ?",
                (schedule_id,)
            )
            result = self.cursor.fetchone()
            if not result:
                return False, "Schedule not found"
            
            capacity, booked_count = result
            if booked_count >= capacity:
                return False, "Session is full"
            
            # Add booking
            self.cursor.execute(
                "INSERT INTO bookings (schedule_id, customer_name, customer_email) VALUES (?, ?, ?)",
                (schedule_id, customer_name, customer_email)
            )
            
            # Update booked count
            self.cursor.execute(
                "UPDATE schedule SET booked_count = booked_count + 1 WHERE id = ?",
                (schedule_id,)
            )
            
            self.conn.commit()
            return True, "Booking successful"
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False, f"Database error: {str(e)}"
    
    def get_bookings_by_schedule(self, schedule_id):
        """Get all bookings for a specific schedule."""
        self.cursor.execute(
            """
            SELECT b.id, b.customer_name, b.customer_email, b.booking_time 
            FROM bookings b
            WHERE b.schedule_id = ?
            ORDER BY b.booking_time DESC
            """,
            (schedule_id,)
        )
        return self.cursor.fetchall()
    
    def get_today_schedule(self):
        """Get today's schedule."""
        today = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute(
            """
            SELECT id, name, date, time, capacity, booked_count 
            FROM schedule 
            WHERE date = ? 
            ORDER BY time
            """,
            (today,)
        )
        return self.cursor.fetchall()
    
    def get_upcoming_schedule(self, days=7):
        """Get upcoming schedule for the next X days."""
        today = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        self.cursor.execute(
            """
            SELECT id, name, date, time, capacity, booked_count 
            FROM schedule 
            WHERE date BETWEEN ? AND ?
            ORDER BY date, time
            """,
            (today, end_date)
        )
        return self.cursor.fetchall()
    
    def verify_admin(self, username, password):
        """Verify admin credentials."""
        self.cursor.execute(
            "SELECT id FROM admin WHERE username = ? AND password = ?",
            (username, password)
        )
        result = self.cursor.fetchone()
        return result is not None
    
    def initialize_sample_data(self):
        """Initialize with sample schedule data."""
        # Check if we already have data
        self.cursor.execute("SELECT COUNT(*) FROM schedule")
        if self.cursor.fetchone()[0] > 0:
            return
        
        # Add sample classes for the next 7 days
        class_names = [
            "Morning Yoga", "HIIT Training", "Strength Training",
            "Evening Pilates", "Boxing Basics", "Dance Fitness"
        ]
        
        today = datetime.now()
        for day in range(7):
            current_date = (today + timedelta(days=day)).strftime("%Y-%m-%d")
            
            # Morning class
            morning_time = "07:00"
            self.add_schedule(class_names[day % len(class_names)], current_date, morning_time, 15)
            
            # Afternoon class
            afternoon_time = "12:30"
            self.add_schedule(class_names[(day + 1) % len(class_names)], current_date, afternoon_time, 20)
            
            # Evening class
            evening_time = "18:00"
            self.add_schedule(class_names[(day + 2) % len(class_names)], current_date, evening_time, 25)
    
    def close(self):
        """Close the database connection."""
        self.conn.close()

# Create and initialize the database if running this file directly
if __name__ == "__main__":
    # Delete the database file if it exists
    if os.path.exists("gym_schedule.db"):
        os.remove("gym_schedule.db")
    
    db = GymDatabase()
    db.initialize_sample_data()
    print("Database initialized with sample data.")
    
    # Show sample data
    schedules = db.get_all_schedules()
    print("\nSample Schedule Data:")
    print("ID | Name | Date | Time | Capacity | Booked")
    print("-" * 60)
    for schedule in schedules:
        print(f"{schedule[0]} | {schedule[1]} | {schedule[2]} | {schedule[3]} | {schedule[4]} | {schedule[5]}")
    
    db.close()