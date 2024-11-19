# blueprints/configurations/routes.py

from flask import render_template, request, redirect, url_for, flash
from . import configurations_bp
from .forms import ConfigurationForm
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

@configurations_bp.route('/configurations')
def configurations():
    data = read_config_file()
    configs = data.get('configurations', [])
    return render_template('configurations.html', configs=configs)

@configurations_bp.route('/add_configuration', methods=['GET', 'POST'])
def add_configuration():
    form = ConfigurationForm()
    if form.validate_on_submit():
        name = form.name.data
        instance = form.instance.data
        database_name = form.database_name.data
        auth_method = form.authentication_method.data
        username = form.username.data
        password = form.password.data
        table_name = form.table_name.data

        data = read_config_file()
        configs = data.get('configurations', [])

        if any(config['name'] == name for config in configs):
            flash('Configuration with this name already exists', 'danger')
            return render_template('edit_configuration.html', form=form, action='Add')

        new_config = {
            'id': len(configs) + 1,
            'name': name,
            'instance': instance,
            'database_name': database_name,
            'authentication_method': auth_method,
            'username': username,
            'password': password,
            'table_name': table_name
        }
        configs.append(new_config)
        data['configurations'] = configs
        write_config_file(data)
        flash('Configuration added successfully', 'success')
        return redirect(url_for('configurations.configurations'))
    return render_template('edit_configuration.html', form=form, action='Add')

@configurations_bp.route('/edit_configuration/<int:id>', methods=['GET', 'POST'])
def edit_configuration(id):
    form = ConfigurationForm()
    data = read_config_file()
    configs = data.get('configurations', [])
    config = next((config for config in configs if config['id'] == id), None)

    if not config:
        flash('Configuration not found', 'danger')
        return redirect(url_for('configurations.configurations'))

    if request.method == 'GET':
        form.name.data = config['name']
        form.instance.data = config['instance']
        form.database_name.data = config['database_name']
        form.authentication_method.data = config['authentication_method']
        form.username.data = config['username']
        form.password.data = config['password']
        form.table_name.data = config['table_name']

    if form.validate_on_submit():
        config['name'] = form.name.data
        config['instance'] = form.instance.data
        config['database_name'] = form.database_name.data
        config['authentication_method'] = form.authentication_method.data
        config['username'] = form.username.data
        config['password'] = form.password.data
        config['table_name'] = form.table_name.data

        write_config_file(data)
        flash('Configuration updated successfully', 'success')
        return redirect(url_for('configurations.configurations'))

    return render_template('edit_configuration.html', form=form, action='Edit')

@configurations_bp.route('/delete_configuration/<int:id>')
def delete_configuration(id):
    data = read_config_file()
    configs = data.get('configurations', [])
    configs = [config for config in configs if config['id'] != id]
    data['configurations'] = configs
    write_config_file(data)
    flash('Configuration deleted', 'info')
    return redirect(url_for('configurations.configurations'))
