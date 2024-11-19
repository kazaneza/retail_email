# app.py

from flask import Flask, render_template
from blueprints.configurations.routes import configurations_bp
from blueprints.customers.routes import customers_bp
from blueprints.email_settings.routes import email_settings_bp
from blueprints.failed_emails.routes import failed_emails_bp
import json
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = 'kazaneza'  # Replace with a secure secret key in production

    # Register Blueprints
    app.register_blueprint(configurations_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(email_settings_bp)
    app.register_blueprint(failed_emails_bp)

    # Main Dashboard Route
    @app.route('/')
    def dashboard():
        data = read_config_file()
        email_settings = data.get('email_settings', {'paused': False, 'batch_size': 50})
        dashboard_stats = data.get('sample_data', {}).get('dashboard_stats', {'remaining': 0, 'sent': 0, 'failed': 0})
        remaining = dashboard_stats.get('remaining', 0)
        sent = dashboard_stats.get('sent', 0)
        failed = dashboard_stats.get('failed', 0)

        return render_template(
            'dashboard.html',
            remaining=remaining,
            sent=sent,
            failed=failed,
            paused=email_settings.get('paused', False),
            batch_size=email_settings.get('batch_size', 50)
        )

    # Function to read data from config.json
    def read_config_file():
        CONFIG_FILE = 'config.json'
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

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
