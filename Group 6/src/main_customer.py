from flask import Flask, render_template, request, redirect, url_for, flash
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# In-memory schedule and booking store
class_schedule = [
    {
        'id': 1,
        'class_name': 'Zumba',
        'date': '2025-06-05',
        'time': '09:00 AM',
        'max_participants': 10,
        'participants': []
    },
    {
        'id': 2,
        'class_name': 'Yoga',
        'date': '2025-06-06',
        'time': '10:00 AM',
        'max_participants': 8,
        'participants': []
    },
    {
        'id': 3,
        'class_name': 'HIIT',
        'date': '2025-06-06',
        'time': '02:00 PM',
        'max_participants': 12,
        'participants': []
    }
]

@app.route('/')
@app.route('/schedule')
def schedule():
    # Group by date for display
    schedule_by_date = defaultdict(list)
    for session in sorted(class_schedule, key=lambda x: x['date']):
        schedule_by_date[session['date']].append(session)
    return render_template('customer_schedule.html', schedule_by_date=schedule_by_date)

@app.route('/book/<int:schedule_id>', methods=['GET', 'POST'])
def book(schedule_id):
    session = next((s for s in class_schedule if s['id'] == schedule_id), None)
    if not session:
        flash('Class not found.', 'danger')
        return redirect(url_for('schedule'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        if len(session['participants']) >= session['max_participants']:
            flash('Sorry, this class is fully booked.', 'danger')
        else:
            session['participants'].append({'name': name, 'email': email})
            flash(f'Booking successful for {session["class_name"]} on {session["date"]}.', 'success')
        return redirect(url_for('schedule'))

    return render_template('customer_book.html', session=session)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
