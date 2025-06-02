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
def create_customer_templates():
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Customer base template
    with open('templates/customer_base.html', 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}FitLife Gymnasium{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-gray-50">
    <nav class="bg-blue-900 shadow-lg">
        <div class="max-w-7xl mx-auto px-4">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <i class="fas fa-dumbbell text-yellow-400 text-2xl mr-3"></i>
                    <span class="text-2xl font-bold text-gray-50">Rams Court</span>
                </div>
                <div class="flex items-center space-x-4">
                    <a href="/schedule" class="text-gray-50 hover:text-yellow-300">Schedule</a>
                </div>
            </div>
        </div>
    </nav>
    
    <main class="max-w-7xl mx-auto py-6 px-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="mb-4 p-4 rounded-md {% if category == 'success' %}bg-green-100 text-green-700{% elif category == 'info' %}bg-blue-100 text-blue-700{% else %}bg-red-100 text-red-700{% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </main>
    
    <footer class="bg-gray-800 text-white mt-12">
        <div class="max-w-7xl mx-auto py-8 px-4">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div>
                    <h3 class="text-lg font-semibold mb-4">FitLife Gymnasium</h3>
                    <p class="text-gray-300">Your journey to fitness starts here. Professional trainers, modern equipment, and a supportive community.</p>
                </div>
                <div>
                    <h3 class="text-lg font-semibold mb-4">Contact Info</h3>
                    <p class="text-gray-300">📍 123 Fitness Street, Gym City</p>
                    <p class="text-gray-300">📞 (555) 123-4567</p>
                    <p class="text-gray-300">✉️ info@fitlifegym.com</p>
                </div>
                <div>
                    <h3 class="text-lg font-semibold mb-4">Hours</h3>
                    <p class="text-gray-300">Monday - Friday: 5:00 AM - 11:00 PM</p>
                    <p class="text-gray-300">Saturday - Sunday: 6:00 AM - 10:00 PM</p>
                </div>
            </div>
            <div class="border-t border-gray-700 mt-8 pt-8 text-center">
                <p class="text-gray-300">&copy; 2024 Rams Court. All rights reserved.</p>
            </div>
        </div>
    </footer>
    
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>''')

    # Customer schedule template
    with open('templates/customer_schedule.html', 'w', encoding='utf-8') as f:
        f.write('''{% extends "customer_base.html" %}

{% block title %}Court Schedule - Rams Court{% endblock %}

{% block content %}
<div class="space-y-8">
    <div class="text-center">
        <h1 class="text-4xl font-bold text-gray-900">Court Schedule</h1>
        <p class="mt-2 text-gray-600">Book the gymnasium today Rams!</p>
    </div>
    
    {% for date, sessions in schedule_by_date.items() %}
    <div class="bg-white rounded-lg shadow overflow-hidden">
        <div class="bg-yellow-400 text-black px-6 py-3">
            <h2 class="text-xl font-semibold">{{ date }}</h2>
        </div>
        
        <div class="p-6">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {% for session in sessions %}
                <div class="border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <h3 class="text-lg font-semibold mb-2">{{ session[1] }}</h3>
                    <div class="space-y-2 text-sm text-gray-600 mb-4">
                        <div class="flex items-center">
                            <i class="fas fa-clock mr-2"></i>
                            <span>{{ session[3] }}</span>
                        </div>
                        <div class="flex items-center">
                            <i class="fas fa-users mr-2"></i>
                            <span>{{ session[5] }} / {{ session[4] }} booked</span>
                        </div>
                    </div>
                    <div class="flex justify-between items-center">
                        <div class="w-full bg-gray-200 rounded-full h-2 mr-2">
                            <div class="h-2 bg-blue-600 rounded-full" style="width: {{ (session[5] / session[4] * 100) if session[4] > 0 else 0 }}%"></div>
                        </div>
                        <a href="/book/{{ session[0] }}" 
                           class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 {% if session[5] >= session[4] %}opacity-50 cursor-not-allowed{% endif %}"
                           {% if session[5] >= session[4] %}aria-disabled="true"{% endif %}>
                            {% if session[5] >= session[4] %}Full{% else %}Book{% endif %}
                        </a>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    {% endfor %}
    
    {% if not schedule_by_date %}
    <div class="bg-white rounded-lg shadow p-8 text-center">
        <p class="text-gray-500">No classes scheduled at the moment.</p>
        <p class="text-gray-500 mt-2">Please check back later.</p>
    </div>
    {% endif %}
</div>
{% endblock %}''')

    # Customer booking template
    with open('templates/customer_book.html', 'w', encoding='utf-8') as f:
        f.write('''{% extends "customer_base.html" %}

{% block title %}Book Class - FitLife Gymnasium{% endblock %}

{% block content %}
<div class="max-w-md mx-auto">
    <div class="bg-white rounded-lg shadow p-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-6">Book a Class</h1>
        
        <div class="mb-6 p-4 bg-gray-50 rounded-lg">
            <h2 class="text-lg font-semibold mb-2">{{ session[1] }}</h2>
            <div class="space-y-1 text-sm text-gray-600">
                <div class="flex items-center">
                    <i class="fas fa-calendar mr-2"></i>
                    <span>{{ session[2] }}</span>
                </div>
                <div class="flex items-center">
                    <i class="fas fa-clock mr-2"></i>
                    <span>{{ session[3] }}</span>
                </div>
                <div class="flex items-center">
                    <i class="fas fa-users mr-2"></i>
                    <span>{{ session[5] }} / {{ session[4] }} booked</span>
                </div>
            </div>
        </div>
        
        <form method="POST">
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Your Name</label>
                    <input type="text" name="name" required 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
                           placeholder="Enter your full name">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input type="email" name="email" required 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
                           placeholder="your@email.com">
                </div>
            </div>
            
            <div class="flex justify-end mt-6 space-x-3">
                <a href="/schedule" class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">
                    Cancel
                </a>
                <button type="submit" class="px-4 py-2 bg-yellow-400 text-white rounded-md hover:bg-yellow-400">
                    Confirm Booking
                </button>
            </div>
        </form>
    </div>
</div>
{% endblock %}''')

create_customer_templates()

if __name__ == '__main__':
    # Make sure database exists
    if not os.path.exists("gym_schedule.db"):
        db.initialize_sample_data()
        print("Database initialized with sample data.")
    
    print("🏋️ Gymnasium Scheduler - Customer Interface")
    print("=" * 50)
    print("Starting Customer Flask server...")
    print("Customer Portal: http://localhost:5002")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5004)