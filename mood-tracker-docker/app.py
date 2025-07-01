from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this in production

DATA_FILE = 'mood_data.csv'
USER_FILE = 'users.csv'


def ensure_files():
    if not os.path.exists(DATA_FILE):
        pd.DataFrame(columns=['username', 'date', 'mood']).to_csv(DATA_FILE, index=False)
    if not os.path.exists(USER_FILE):
        pd.DataFrame(columns=['username', 'password']).to_csv(USER_FILE, index=False)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    ensure_files()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = pd.read_csv(USER_FILE)
        user = users[(users['username'] == username) & (users['password'] == password)]

        if not user.empty:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    ensure_files()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = pd.read_csv(USER_FILE)
        if username in users['username'].values:
            return render_template('signup.html', error='Username already exists')

        users = pd.concat([users, pd.DataFrame([{'username': username, 'password': password}])], ignore_index=True)
        users.to_csv(USER_FILE, index=False)
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    ensure_files()
    today = datetime.now().strftime('%Y-%m-%d')

    if request.method == 'POST':
        mood = request.form['mood']
        df = pd.read_csv(DATA_FILE)

        # Remove existing entry for today
        df = df[~((df['username'] == session['username']) & (df['date'] == today))]
        new_row = {'username': session['username'], 'date': today, 'mood': mood}
        df = pd.concat([df, pd.DataFrame([new_row])])
        df.to_csv(DATA_FILE, index=False)

        return redirect(url_for('history'))

    return render_template('home.html')


@app.route('/history')
def history():
    if 'username' not in session:
        return redirect(url_for('login'))

    ensure_files()
    df = pd.read_csv(DATA_FILE)
    df = df[df['username'] == session['username']].sort_values('date').tail(7)

    dates = df['date'].tolist()
    moods = df['mood'].tolist()

    print("DATES:", dates)
    print("MOODS:", moods)

    return render_template('history.html', dates=dates, moods=moods)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
