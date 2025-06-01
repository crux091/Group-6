from flask import Flask

app = Flask(__name__)
app.secret_key = 'admin-secret-key-2024'

@app.route('/')
def index():
    return "Welcome to the Home Page!"

@app.route('/schedules')
def schedules():
    return "This is the Schedules Page."

@app.route('/bookings')
def bookings():
    return "This is the Bookings Page."

if __name__ == '__main__':
    app.run(debug=True)
