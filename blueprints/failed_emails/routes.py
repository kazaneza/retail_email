# blueprints/failed_emails/routes.py

from flask import render_template, send_file, url_for
from . import failed_emails_bp
import json
import os
import io

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

@failed_emails_bp.route('/failed_emails')
def failed_emails():
    data = read_config_file()
    failed_list = data.get('sample_data', {}).get('failed_emails', [])
    return render_template('failed_emails.html', failed_list=failed_list)

@failed_emails_bp.route('/download_failed_json')
def download_failed_json():
    data = read_config_file()
    failed_list = data.get('sample_data', {}).get('failed_emails', [])
    # Convert to JSON and send as file
    return send_file(
        io.BytesIO(json.dumps(failed_list, indent=4).encode()),
        mimetype='application/json',
        as_attachment=True,
        attachment_filename='failed_emails.json'
    )
