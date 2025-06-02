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

# Create admin templates
def create_admin_templates():
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Admin login template
    with open('templates/admin_login.html', 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - Gymnasium Scheduler</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100 min-h-screen flex items-center justify-center">
    <div class="max-w-md w-full bg-white rounded-lg shadow-md p-6">
        <div class="text-center mb-8">
            <i class="fas fa-dumbbell text-blue-600 text-4xl mb-4"></i>
            <h1 class="text-2xl font-bold text-gray-900">Admin Login</h1>
            <p class="text-gray-600">Gymnasium Schedule Manager</p>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="mb-4 p-4 rounded-md {% if category == 'success' %}bg-green-100 text-green-700{% else %}bg-red-100 text-red-700{% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="POST">
            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2">Username</label>
                <input type="text" name="username" required 
                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
                       placeholder="admin">
            </div>
            <div class="mb-6">
                <label class="block text-gray-700 text-sm font-bold mb-2">Password</label>
                <input type="password" name="password" required 
                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
                       placeholder="Enter your password">
            </div>
            <button type="submit" 
                    class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:bg-blue-700">
                Login
            </button>
        </form>
        
        <div class="mt-6 text-center text-sm text-gray-600">
            <p>Demo credentials:</p>
            <p>Username: admin</p>
            <p>Password: admin123</p>
        </div>
    </div>
</body>
</html>''')

    # Admin base template
    with open('templates/admin_base.html', 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Admin Panel - Gymnasium Scheduler{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-gray-50">
    <div class="flex h-screen">
        <!-- Sidebar -->
        <div class="bg-gray-800 text-white w-64 flex-shrink-0">
            <div class="p-4">
                <div class="flex items-center">
                    <i class="fas fa-dumbbell text-blue-400 text-2xl mr-3"></i>
                    <span class="text-xl font-bold">Schedule Admin</span>
                </div>
            </div>
            <nav class="mt-8">
                <a href="/dashboard" class="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white">
                    <i class="fas fa-tachometer-alt mr-3"></i>
                    Dashboard
                </a>
                <a href="/schedule" class="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white">
                    <i class="fas fa-calendar mr-3"></i>
                    Schedule Management
                </a>
                <a href="/add_schedule" class="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white">
                    <i class="fas fa-plus mr-3"></i>
                    Add New Session
                </a>
                <a href="/logout" class="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white mt-8">
                    <i class="fas fa-sign-out-alt mr-3"></i>
                    Logout
                </a>
            </nav>
        </div>
        
        <!-- Main content -->
        <div class="flex-1 flex flex-col overflow-hidden">
            <header class="bg-white shadow-sm border-b border-gray-200">
                <div class="flex justify-between items-center px-6 py-4">
                    <h1 class="text-2xl font-semibold text-gray-900">{% block header %}Admin Panel{% endblock %}</h1>
                    <div class="flex items-center space-x-4">
                        <span class="text-gray-600">Welcome, {{ session.admin_username }}</span>
                        <i class="fas fa-user-circle text-gray-400 text-2xl"></i>
                    </div>
                </div>
            </header>
            
            <main class="flex-1 overflow-y-auto p-6">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="mb-4 p-4 rounded-md {% if category == 'success' %}bg-green-100 text-green-700{% else %}bg-red-100 text-red-700{% endif %}">
                                {{ message }}
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                
                {% block content %}{% endblock %}
            </main>
        </div>
    </div>
    
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>''')

    # Admin dashboard template
    with open('templates/admin_dashboard.html', 'w', encoding='utf-8') as f:
        f.write('''{% extends "admin_base.html" %}

{% block title %}Dashboard - Admin Panel{% endblock %}
{% block header %}Dashboard{% endblock %}

{% block content %}
<div class="space-y-6">
    <!-- Quick Actions -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <a href="/schedule" class="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow">
            <div class="flex items-center">
                <div class="p-2 bg-blue-100 rounded-lg">
                    <i class="fas fa-calendar text-blue-600"></i>
                </div>
                <div class="ml-4">
                    <p class="text-sm font-medium text-gray-600">Manage Schedule</p>
                    <p class="text-lg font-bold text-gray-900">View All Sessions</p>
                </div>
            </div>
        </a>
        
        <a href="/add_schedule" class="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow">
            <div class="flex items-center">
                <div class="p-2 bg-green-100 rounded-lg">
                    <i class="fas fa-plus text-green-600"></i>
                </div>
                <div class="ml-4">
                    <p class="text-sm font-medium text-gray-600">Create New</p>
                    <p class="text-lg font-bold text-gray-900">Add Session</p>
                </div>
            </div>
        </a>
    </div>
    
    <!-- Today's Schedule -->
    <div class="bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900">Today's Schedule</h2>
        </div>
        <div class="p-6">
            {% if today_schedule %}
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Session Name</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Capacity</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Bookings</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            {% for session in today_schedule %}
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <div class="text-sm font-medium text-gray-900">{{ session[1] }}</div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <div class="text-sm text-gray-900">{{ session[3] }}</div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <div class="text-sm text-gray-900">{{ session[4] }}</div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <div class="text-sm text-gray-900">{{ session[5] }} / {{ session[4] }}</div>
                                    <div class="w-24 h-2 bg-gray-200 rounded-full mt-1">
                                        <div class="h-2 bg-blue-600 rounded-full" style="width: {{ (session[5] / session[4] * 100) if session[4] > 0 else 0 }}%"></div>
                                    </div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                    <a href="/view_bookings/{{ session[0] }}" class="text-blue-600 hover:text-blue-900 mr-3">View Bookings</a>
                                    <a href="/edit_schedule/{{ session[0] }}" class="text-indigo-600 hover:text-indigo-900">Edit</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <p class="text-gray-500 text-center py-4">No sessions scheduled for today.</p>
                <div class="text-center">
                    <a href="/add_schedule" class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
                        <i class="fas fa-plus mr-2"></i>
                        Add New Session
                    </a>
                </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}''')

    # Admin schedule management template
    with open('templates/admin_schedule.html', 'w', encoding='utf-8') as f:
        f.write('''{% extends "admin_base.html" %}

{% block title %}Schedule Management - Admin Panel{% endblock %}
{% block header %}Schedule Management{% endblock %}

{% block content %}
<div class="space-y-6">
    <div class="flex justify-between items-center">
        <h2 class="text-2xl font-bold text-gray-900">All Sessions</h2>
        <a href="/add_schedule" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            <i class="fas fa-plus mr-2"></i>Add New Session
        </a>
    </div>
    
    <div class="bg-white rounded-lg shadow overflow-hidden">
        <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Session Name</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Capacity</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Bookings</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                    {% for session in schedules %}
                    <tr>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <div class="text-sm font-medium text-gray-900">{{ session[1] }}</div>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <div class="text-sm text-gray-900">{{ session[2] }}</div>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <div class="text-sm text-gray-900">{{ session[3] }}</div>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <div class="text-sm text-gray-900">{{ session[4] }}</div>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <div class="text-sm text-gray-900">{{ session[5] }} / {{ session[4] }}</div>
                            <div class="w-24 h-2 bg-gray-200 rounded-full mt-1">
                                <div class="h-2 bg-blue-600 rounded-full" style="width: {{ (session[5] / session[4] * 100) if session[4] > 0 else 0 }}%"></div>
                            </div>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <a href="/view_bookings/{{ session[0] }}" class="text-blue-600 hover:text-blue-900 mr-3">View Bookings</a>
                            <a href="/edit_schedule/{{ session[0] }}" class="text-indigo-600 hover:text-indigo-900 mr-3">Edit</a>
                            <form method="POST" action="/delete_schedule/{{ session[0] }}" class="inline">
                                <button type="submit" class="text-red-600 hover:text-red-900" 
                                        onclick="return confirm('Are you sure you want to delete this session?')">
                                    Delete
                                </button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% if not schedules %}
        <div class="p-6 text-center">
            <p class="text-gray-500">No sessions found.</p>
            <a href="/add_schedule" class="inline-flex items-center px-4 py-2 mt-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
                <i class="fas fa-plus mr-2"></i>
                Add New Session
            </a>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}''')

    # Admin add schedule template
    with open('templates/admin_add_schedule.html', 'w', encoding='utf-8') as f:
        f.write('''{% extends "admin_base.html" %}

{% block title %}Add New Session - Admin Panel{% endblock %}
{% block header %}Add New Session{% endblock %}

{% block content %}
<div class="max-w-2xl mx-auto">
    <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-6">Create New Session</h2>
        
        <form method="POST">
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Session Name</label>
                    <input type="text" name="name" required 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
                           placeholder="e.g., Morning Yoga">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Date</label>
                    <input type="date" name="date" required 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Time</label>
                    <input type="time" name="time" required 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Capacity</label>
                    <input type="number" name="capacity" min="1" value="20" required 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500">
                </div>
            </div>
            
            <div class="flex justify-end mt-6 space-x-3">
                <a href="/schedule" class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">
                    Cancel
                </a>
                <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                    Create Session
                </button>
            </div>
        </form>
    </div>
</div>
{% endblock %}''')

    # Admin edit schedule template
    with open('templates/admin_edit_schedule.html', 'w', encoding='utf-8') as f:
        f.write('''{% extends "admin_base.html" %}

{% block title %}Edit Session - Admin Panel{% endblock %}
{% block header %}Edit Session{% endblock %}

{% block content %}
<div class="max-w-2xl mx-auto">
    <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-6">Edit Session</h2>
        
        <form method="POST">
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Session Name</label>
                    <input type="text" name="name" required 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
                           value="{{ schedule[1] }}">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Date</label>
                    <input type="date" name="date" required 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
                           value="{{ schedule[2] }}">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Time</label>
                    <input type="time" name="time" required 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
                           value="{{ schedule[3] }}">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Capacity</label>
                    <input type="number" name="capacity" min="{{ schedule[5] }}" required 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
                           value="{{ schedule[4] }}">
                    <p class="text-sm text-gray-500 mt-1">Note: Capacity cannot be less than current bookings ({{ schedule[5] }}).</p>
                </div>
            </div>
            
            <div class="flex justify-end mt-6 space-x-3">
                <a href="/schedule" class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">
                    Cancel
                </a>
                <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                    Update Session
                </button>
            </div>
        </form>
    </div>
</div>
{% endblock %}''')

    # Admin view bookings template
    with open('templates/admin_view_bookings.html', 'w', encoding='utf-8') as f:
        f.write('''{% extends "admin_base.html" %}

{% block title %}View Bookings - Admin Panel{% endblock %}
{% block header %}Session Bookings{% endblock %}

{% block content %}
<div class="space-y-6">
    <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-2">{{ schedule[1] }}</h2>
        <div class="flex space-x-4 text-sm text-gray-600">
            <div><i class="fas fa-calendar mr-1"></i> {{ schedule[2] }}</div>
            <div><i class="fas fa-clock mr-1"></i> {{ schedule[3] }}</div>
            <div><i class="fas fa-users mr-1"></i> {{ schedule[5] }} / {{ schedule[4] }} booked</div>
        </div>
    </div>
    
    <div class="bg-white rounded-lg shadow overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-semibold text-gray-900">Bookings</h3>
        </div>
        
        <div class="overflow-x-auto">
            {% if bookings %}
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer Name</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Booking Time</th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                    {% for booking in bookings %}
                    <tr>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <div class="text-sm font-medium text-gray-900">{{ booking[1] }}</div>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <div class="text-sm text-gray-900">{{ booking[2] }}</div>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <div class="text-sm text-gray-900">{{ booking[3] }}</div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <div class="p-6 text-center">
                <p class="text-gray-500">No bookings for this session yet.</p>
            </div>
            {% endif %}
        </div>
    </div>
    
    <div class="flex justify-end">
        <a href="/schedule" class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700">
            Back to Schedule
        </a>
    </div>
</div>
{% endblock %}''')

create_admin_templates()

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