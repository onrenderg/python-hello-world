from flask import Flask, request, render_template_string, redirect, url_for, session
import psycopg2
from psycopg2 import sql

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key for session management

# Database configuration
DATABASE_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres.pidvimlpfbtztwitweml',
    'password': 'MAY23/postgressql/v1',
    'host': 'aws-0-ap-south-1.pooler.supabase.com',
    'port': '5432'
}

def get_db_connection():
    conn = psycopg2.connect(
        dbname=DATABASE_CONFIG['dbname'],
        user=DATABASE_CONFIG['user'],
        password=DATABASE_CONFIG['password'],
        host=DATABASE_CONFIG['host'],
        port=DATABASE_CONFIG['port']
    )
    return conn

# Root route to serve the HTML form
@app.route('/')
def index():
    html_form = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register or Login</title>
    </head>
    <body>
        <h2>Register</h2>
        <form method="POST" action="/register">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required><br><br>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required><br><br>
            <input type="submit" value="Register">
        </form>
        <h2>Login</h2>
        <form method="POST" action="/login">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required><br><br>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required><br><br>
            <input type="submit" value="Login">
        </form>
    </body>
    </html>
    """
    return render_template_string(html_form)

# Route to handle the registration form submission
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Create table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                password VARCHAR(50) NOT NULL
            )
        """)
        # Insert user data into the table
        cur.execute("""
            INSERT INTO users (username, password)
            VALUES (%s, %s)
        """, (username, password))
        conn.commit()
        cur.close()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"An error occurred: {e}")
        return "An error occurred while registering the user."
    finally:
        if conn:
            conn.close()

    return "Registration successful!"

# Route to handle the login form submission
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Check if the user exists in the database
        cur.execute("""
            SELECT * FROM users WHERE username = %s AND password = %s
        """, (username, password))
        user = cur.fetchone()
        cur.close()
        if user:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return "Invalid username or password."
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while logging in."
    finally:
        if conn:
            conn.close()

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'logged_in' in session and session['logged_in']:
        return "<p>Hi</p>"
    else:
        return redirect(url_for('index'))

# Route to handle logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
