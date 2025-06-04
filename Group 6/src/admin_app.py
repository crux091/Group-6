from flask import Flask, render_template, request, redirect, url_for, flash, session
from gym_database import GymDatabase
import os

app = Flask(__name__)
app.secret_key = 'admin-secret-key-2024'

# Initialize database
db = GymDatabase()

# Authentication decorator
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'admin_logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if db.verify_admin(username, password):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Successfully logged in!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Successfully logged out!', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@admin_required
def dashboard():
    today_schedule = db.get_today_schedule()
    return render_template('admin_dashboard.html', today_schedule=today_schedule)

@app.route('/schedule')
@admin_required
def schedule():
    all_schedules = db.get_all_schedules()
    return render_template('admin_schedule.html', schedules=all_schedules)

@app.route('/add_schedule', methods=['GET', 'POST'])
@admin_required
def add_schedule():
    if request.method == 'POST':
        name = request.form.get('name')
        date = request.form.get('date')
        time = request.form.get('time')
        capacity = int(request.form.get('capacity', 20))
        
        if db.add_schedule(name, date, time, capacity):
            flash('Schedule added successfully!', 'success')
            return redirect(url_for('schedule'))
        else:
            flash('Failed to add schedule!', 'error')
    
    return render_template('admin_add_schedule.html')

@app.route('/edit_schedule/<int:schedule_id>', methods=['GET', 'POST'])
@admin_required
def edit_schedule(schedule_id):
    schedule = db.get_schedule_by_id(schedule_id)
    
    if not schedule:
        flash('Schedule not found!', 'error')
        return redirect(url_for('schedule'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        date = request.form.get('date')
        time = request.form.get('time')
        capacity = int(request.form.get('capacity', 20))
        
        if db.update_schedule(schedule_id, name, date, time, capacity):
            flash('Schedule updated successfully!', 'success')
            return redirect(url_for('schedule'))
        else:
            flash('Failed to update schedule!', 'error')
    
    return render_template('admin_edit_schedule.html', schedule=schedule)

@app.route('/delete_schedule/<int:schedule_id>', methods=['POST'])
@admin_required
def delete_schedule(schedule_id):
    if db.delete_schedule(schedule_id):
        flash('Schedule deleted successfully!', 'success')
    else:
        flash('Failed to delete schedule!', 'error')
    
    return redirect(url_for('schedule'))

@app.route('/view_bookings/<int:schedule_id>')
@admin_required
def view_bookings(schedule_id):
    schedule = db.get_schedule_by_id(schedule_id)
    bookings = db.get_bookings_by_schedule(schedule_id)
    
    if not schedule:
        flash('Schedule not found!', 'error')
        return redirect(url_for('schedule'))
    
    return render_template('admin_view_bookings.html', schedule=schedule, bookings=bookings)

if __name__ == '__main__':
    # Initialize database with sample data
    if not os.path.exists("gym_schedule.db"):
        db.initialize_sample_data()
        print("Database initialized with sample data.")
    
    print("🏋️ Gymnasium Scheduler - Admin Interface")
    print("=" * 50)
    print("Starting Admin Flask server...")
    print("Admin Login: http://localhost:5001")
    print("Credentials: admin / admin123")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5001)