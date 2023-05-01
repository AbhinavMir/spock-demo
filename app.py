from flask import Flask, request, jsonify, make_response
import sqlite3
import hashlib
import base64
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = 'supersecretkey'

# Initialize database
def init_db():
    conn = sqlite3.connect('health_records.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS admins
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT NOT NULL,
                 public_key TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS patients
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 age INTEGER NOT NULL,
                 gender TEXT NOT NULL,
                 height REAL NOT NULL,
                 weight REAL NOT NULL,
                 admin_id INTEGER NOT NULL,
                 FOREIGN KEY (admin_id) REFERENCES admins (id))''')
    conn.commit()
    conn.close()

# Add a new admin to the database
def add_admin(username, public_key):
    conn = sqlite3.connect('health_records.db')
    c = conn.cursor()
    c.execute("INSERT INTO admins (username, public_key) VALUES (?, ?)", (username, public_key))
    conn.commit()
    conn.close()

# Get the admin associated with a particular username
def get_admin(username):
    conn = sqlite3.connect('health_records.db')
    c = conn.cursor()
    c.execute("SELECT * FROM admins WHERE username = ?", (username,))
    admin = c.fetchone()
    conn.close()
    return admin

# Add a new patient to the database
def add_patient(name, age, gender, height, weight, admin_id):
    conn = sqlite3.connect('health_records.db')
    c = conn.cursor()
    c.execute("INSERT INTO patients (name, age, gender, height, weight, admin_id) VALUES (?, ?, ?, ?, ?, ?)", (name, age, gender, height, weight, admin_id))
    conn.commit()
    conn.close()

# Get the patient associated with a particular id
def get_patient(patient_id):
    conn = sqlite3.connect('health_records.db')
    c = conn.cursor()
    c.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    patient = c.fetchone()
    conn.close()
    return patient

# Authenticate the user based on the cookie present
def authenticate_user():
    # get cookie stored by key spock_request_cookie
    cookie = request.cookies.get('spock_request_cookie')
    if cookie is not None:
        value = json.loads(cookie)
        username = value['username']
        if(username == 'admin'):
            return True
        else :
            return False
        
def loggedin_user():
    # get cookie stored by key spock_request_cookie
    cookie = request.cookies.get('spock_request_cookie')
    if cookie is not None:
        value = json.loads(cookie)
        username = value['username']
        return username
    else:
        return None

@app.route('/add_admin', methods=['POST'])
def create_admin():
    username = request.form['username']
    public_key = request.form['public_key']
    add_admin(username, public_key)
    response = make_response(jsonify({'message': 'Admin created successfully'}), 200)
    response.headers['usesSpock'] = 'True'  # Add the header here
    return response

@app.route('/login', methods=['GET'])
def check():
    auth = authenticate_user()
    if auth:
        response = make_response(jsonify({'message': 'Authenticated'}), 200)
        response.set_cookie('username', value=loggedin_user())
        return response
    else:
        response = make_response(jsonify({'message': 'Not authenticated'}), 401)
        # print the request
        print(request.headers)
        response.headers['usesSpock'] = 'True'  # Add the header here
        return response

@app.route('/add_patient', methods=['POST'])
def create_patient():
    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    height = request.form['height']
    weight = request.form['weight']
    admin_id = request.form['admin_id']
    add_patient(name, age, gender, height, weight, admin_id)
    response = make_response(jsonify({'message': 'Patient created successfully'}), 200)
    response.headers['usesSpock'] = 'True'  # Add the header here
    return response

@app.route('/patient/<int:patient_id>', methods=['GET'])
def get_patient_endpoint(patient_id):
    if authenticate_user():
        patient = get_patient(patient_id)
        if patient is not None:
            response = make_response(jsonify({'name': patient[1], 'age': patient[2], 'gender': patient[3], 'height': patient[4], 'weight': patient[5]}), 200)
            response.headers['usesSpock'] = 'True'  # Add the header here
            return response
        return make_response(jsonify({'message': 'Patient not found'}), 404)
    return make_response(jsonify({'message': 'Not authenticated'}), 401)

@app.route('/get_users', methods=['GET'])
def get_users():
    if(loggedin_user() == 'admin'):
        conn = sqlite3.connect('health_records.db')
        c = conn.cursor()
        c.execute("SELECT * FROM patients")
        patients = c.fetchall()
        conn.close()
        user_list = []
        for patient in patients:
            user_list.append({'id': patient[0], 'name': patient[1], 'age': patient[2], 'gender': patient[3], 'height': patient[4], 'weight': patient[5]})
        response = make_response(jsonify({'users': user_list}), 200)
        response.headers['usesSpock'] = 'True'  # Add the header here
        return response
    else:
        return make_response(jsonify({'message': 'Not authenticated'}), 401)

# Initialize the database
init_db()

# Add initial admins to the database
# add_admin('admin', 'test')
# add_patient("test", 4, "M", 6, 25, 1)