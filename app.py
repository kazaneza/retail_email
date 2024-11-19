# app.py

from flask import Flask, redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from blueprints.configurations import configurations_bp
from blueprints.customers import customers_bp
from blueprints.email_settings import email_settings_bp
from blueprints.failed_emails import failed_emails_bp
from models import db, Customer
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

# Load database configurations from config.json
CONFIG_FILE = 'config.json'

def load_db_config():
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError("config.json file not found.")
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    if not config.get('configurations'):
        raise ValueError("No configurations found in config.json.")
    # Use the first configuration for database URI
    db_config = config['configurations'][0]
    if db_config['authentication_method'] == 'SQL':
        return f"mssql+pyodbc://{db_config['username']}:{db_config['password']}@{db_config['instance']}/{db_config['database_name']}?driver=ODBC+Driver+17+for+SQL+Server"
    elif db_config['authentication_method'] == 'Windows':
        return f"mssql+pyodbc://@{db_config['instance']}/{db_config['database_name']}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    else:
        raise ValueError("Unsupported authentication method.")

app.config['SQLALCHEMY_DATABASE_URI'] = load_db_config()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Register Blueprints
app.register_blueprint(configurations_bp, url_prefix='/configurations')
app.register_blueprint(customers_bp, url_prefix='/customers')
app.register_blueprint(email_settings_bp, url_prefix='/email_settings')
app.register_blueprint(failed_emails_bp, url_prefix='/failed_emails')

# Define the root route
@app.route('/')
def home():
    # Redirect to the list_configurations endpoint
    return redirect(url_for('configurations.list_configurations'))

# Define the dashboard route
@app.route('/dashboard')
def dashboard():
    # Read configuration data
    def read_config_file():
        if not os.path.exists(CONFIG_FILE) or os.path.getsize(CONFIG_FILE) == 0:
            # Initialize config.json with default data if it doesn't exist or is empty
            with open(CONFIG_FILE, 'w') as f:
                json.dump({
                    "configurations": [],
                    "email_settings": {"paused": False, "batch_size": 50},
                    "sample_data": {
                        "customers": [],
                        "failed_emails": [],
                        "dashboard_stats": {"remaining": 0, "sent": 0, "failed": 0}
                    }
                }, f, indent=4)
        with open(CONFIG_FILE, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                # If JSON is invalid, re-initialize with default data
                data = {
                    "configurations": [],
                    "email_settings": {"paused": False, "batch_size": 50},
                    "sample_data": {
                        "customers": [],
                        "failed_emails": [],
                        "dashboard_stats": {"remaining": 0, "sent": 0, "failed": 0}
                    }
                }
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(data, f, indent=4)
        return data

    data = read_config_file()
    dashboard_stats = data.get('sample_data', {}).get('dashboard_stats', {})
    email_settings = data.get('email_settings', {})
    paused = email_settings.get('paused', False)
    batch_size = email_settings.get('batch_size', 50)

    return render_template('dashboard.html',
                           remaining=dashboard_stats.get('remaining', 0),
                           sent=dashboard_stats.get('sent', 0),
                           failed=dashboard_stats.get('failed', 0),
                           paused=paused,
                           batch_size=batch_size)

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
