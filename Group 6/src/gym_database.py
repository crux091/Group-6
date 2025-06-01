import mysql.connector
from datetime import datetime, timedelta

class GymDatabase:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost:3306",  # Replace with your MySQL host and port
            user="root",
            password="123456",  # Replace with your MySQL password
            database="gym_customer"  # Replace with your actual DB name
        )
        self.cursor = self.conn.cursor()

    def get_upcoming_schedule(self, days):
        query = """
        SELECT id, class_name, date, time, capacity, booked_count 
        FROM schedule 
        WHERE date >= CURDATE() AND date <= CURDATE() + INTERVAL %s DAY 
        ORDER BY date, time
        """
        self.cursor.execute(query, (days,))
        return self.cursor.fetchall()

    def get_schedule_by_id(self, schedule_id):
        query = "SELECT id, class_name, date, time, capacity, booked_count FROM schedule WHERE id = %s"
        self.cursor.execute(query, (schedule_id,))
        return self.cursor.fetchone()

    def book_session(self, schedule_id, name, email):
        schedule = self.get_schedule_by_id(schedule_id)
        if not schedule:
            return False, "Session not found."

        if schedule[5] >= schedule[4]:
            return False, "This session is already full."

        try:
            # Insert booking
            insert_query = "INSERT INTO bookings (schedule_id, name, email) VALUES (%s, %s, %s)"
            self.cursor.execute(insert_query, (schedule_id, name, email))

            # Update booked count
            update_query = "UPDATE schedule SET booked_count = booked_count + 1 WHERE id = %s"
            self.cursor.execute(update_query, (schedule_id,))
            
            self.conn.commit()
            return True, "Booking successful."
        except mysql.connector.Error as err:
            self.conn.rollback()
            return False, f"MySQL Error: {err}"
