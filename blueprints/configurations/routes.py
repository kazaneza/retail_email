from flask import render_template, request, redirect, url_for, flash
from . import configurations_bp
from .forms import ConfigurationForm
from blueprints.utils.db_utils import get_db_connection
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
def list_configurations():
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
        return redirect(url_for('configurations.list_configurations'))
    return render_template('edit_configuration.html', form=form, action='Add')

@configurations_bp.route('/edit_configuration/<int:id>', methods=['GET', 'POST'])
def edit_configuration(id):
    form = ConfigurationForm()
    data = read_config_file()
    configs = data.get('configurations', [])
    config = next((config for config in configs if config['id'] == id), None)

    if not config:
        flash('Configuration not found', 'danger')
        return redirect(url_for('configurations.list_configurations'))

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
        return redirect(url_for('configurations.list_configurations'))

    return render_template('edit_configuration.html', form=form, action='Edit')

@configurations_bp.route('/delete_configuration/<int:id>')
def delete_configuration(id):
    data = read_config_file()
    configs = data.get('configurations', [])
    configs = [config for config in configs if config['id'] != id]
    data['configurations'] = configs
    write_config_file(data)
    flash('Configuration deleted', 'info')
    return redirect(url_for('configurations.list_configurations'))

@configurations_bp.route('/fetch_customers', methods=['POST'])
def fetch_customers():
    data = read_config_file()
    configs = data.get('configurations', [])
    if not configs:
        flash('No database configurations available. Please add a configuration first.', 'danger')
        return redirect(url_for('configurations.list_configurations'))
    
    # For simplicity, use the first configuration
    config = configs[0]
    connection = get_db_connection(config)
    
    if not connection:
        flash('Failed to connect to the database. Please check your configuration.', 'danger')
        return redirect(url_for('configurations.list_configurations'))
    
    table_name = config.get('table_name', 'customers')
    
    try:
        cursor = connection.cursor()
        query = f"SELECT [recid], [short_name], [sms_d_1], [email_d_1], [customer_id] FROM {table_name}"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Map SQL data to application data model
        customers = []
        for row in rows:
            customer = {
                'id': row[0],  # Assuming 'recid' is unique and used as ID
                'customer_id': str(row[4]) if row[4] else '',
                'name': row[1] if row[1] else '',
                'email': row[3] if row[3] else '',
                'phone': row[2] if row[2] else '',
                'account': str(row[0]),
                'status': 'Not Yet'
            }
            customers.append(customer)
        
        # Update sample_data in config.json
        data['sample_data']['customers'] = customers
        
        # Update dashboard_stats
        data['sample_data']['dashboard_stats']['remaining'] = len([c for c in customers if c['status'] == 'Not Yet'])
        data['sample_data']['dashboard_stats']['sent'] = len([c for c in customers if c['status'] == 'Sent'])
        data['sample_data']['dashboard_stats']['failed'] = len([c for c in customers if c['status'] == 'Failed'])
        
        write_config_file(data)
        flash(f'Successfully fetched and updated {len(customers)} customers.', 'success')
    except Exception as e:
        flash(f'An error occurred while fetching customers: {e}', 'danger')
    finally:
        connection.close()
    
    return redirect(url_for('configurations.list_configurations'))
