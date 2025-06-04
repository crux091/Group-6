from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from gym_database import GymDatabase
import os

app = Flask(__name__)
app.secret_key = 'customer-secret-key-2024'

# Initialize database
db = GymDatabase()

# Routes
@app.route('/')
def index():
    return redirect(url_for('schedule'))

@app.route('/schedule')
def schedule():
    upcoming_schedule = db.get_upcoming_schedule(14)  # Get schedule for next 14 days
    
    # Group by date
    schedule_by_date = {}
    for session in upcoming_schedule:
        date = session[2]  # date is at index 2
        if date not in schedule_by_date:
            schedule_by_date[date] = []
        schedule_by_date[date].append(session)
    
    return render_template('customer_schedule.html', schedule_by_date=schedule_by_date)

@app.route('/book/<int:schedule_id>', methods=['GET', 'POST'])
def book(schedule_id):
    session_data = db.get_schedule_by_id(schedule_id)
    
    if not session_data:
        flash('Session not found!', 'error')
        return redirect(url_for('schedule'))
    
    if session_data[5] >= session_data[4]:  # If booked_count >= capacity
        flash('This session is already full!', 'error')
        return redirect(url_for('schedule'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        
        success, message = db.book_session(schedule_id, name, email)
        
        if success:
            flash('Booking successful!', 'success')
            return redirect(url_for('schedule'))
        else:
            flash(f'Booking failed: {message}', 'error')
    
    return render_template('customer_book.html', session=session_data)

@app.route('/api/book', methods=['POST'])
def api_book():
    data = request.get_json()
    schedule_id = data.get('schedule_id')
    name = data.get('name')
    email = data.get('email')
    
    if not all([schedule_id, name, email]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    success, message = db.book_session(schedule_id, name, email)
    
    if success:
        return jsonify({'success': True, 'message': 'Booking successful'})
    else:
        return jsonify({'success': False, 'message': message}), 400

# Create customer templates

if __name__ == '__main__':
    # Make sure database exists
    if not os.path.exists("gym_schedule.db"):
        db.initialize_sample_data()
        print("Database initialized with sample data.")
    app.run(debug=True, host='0.0.0.0', port=5004)