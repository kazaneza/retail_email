# blueprints/email_settings/routes.py

from flask import render_template, request, redirect, url_for, flash
from . import email_settings_bp
import json
import os

CONFIG_FILE = 'config.json'

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

def write_config_file(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@email_settings_bp.route('/email_settings', methods=['GET', 'POST'])
def email_settings():
    data = read_config_file()
    email_settings = data.get('email_settings', {'paused': False, 'batch_size': 50})

    if request.method == 'POST':
        email_sending_paused = 'pause' in request.form
        batch_size = int(request.form.get('batch_size', 50))
        email_settings['paused'] = email_sending_paused
        email_settings['batch_size'] = batch_size
        data['email_settings'] = email_settings
        write_config_file(data)
        flash('Email settings updated successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('email_settings.html', paused=email_settings.get('paused', False), batch_size=email_settings.get('batch_size', 50))
