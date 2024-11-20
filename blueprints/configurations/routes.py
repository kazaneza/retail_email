# blueprints/configurations/routes.py

from flask import render_template, request, redirect, url_for, flash
from . import configurations_bp
from .forms import ConfigurationForm
from models import db, Customer
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
                "email_settings": {"paused": False, "batch_size": 50}
            }, f, indent=4)
    with open(CONFIG_FILE, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            # If JSON is invalid, re-initialize with default data
            data = {
                "configurations": [],
                "email_settings": {"paused": False, "batch_size": 50}
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f, indent=4)
    return data

def write_config_file(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@configurations_bp.route('/', methods=['GET'])
def list_configurations():
    data = read_config_file()
    configs = data.get('configurations', [])
    return render_template('configurations.html', configs=configs)

@configurations_bp.route('/add', methods=['GET', 'POST'])
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

@configurations_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
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

@configurations_bp.route('/delete/<int:id>', methods=['GET'])
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
        
        for row in rows:
            customer = Customer.query.get(row[0])
            if customer:
                # Update existing customer without modifying customer_id
                customer.short_name = row[1] or ''
                customer.sms_d_1 = row[2] or ''
                customer.email_d_1 = row[3] or ''
                # Removed: customer.customer_id = row[4] or ''
                customer.status = 1  # Not Yet
            else:
                # Add new customer, assuming customer_id is auto-generated or handled appropriately
                new_customer = Customer(
                    recid=row[0],
                    short_name=row[1] or '',
                    sms_d_1=row[2] or '',
                    email_d_1=row[3] or '',
                    # Handle customer_id appropriately:
                    # If auto-generated, omit it
                    # If not, ensure the value is valid and not an identity column
                    # customer_id=row[4] or '',
                    status=1  # Not Yet
                )
                db.session.add(new_customer)
        
        db.session.commit()
        flash(f'Successfully fetched and updated {len(rows)} customers.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while fetching customers: {e}', 'danger')
    finally:
        connection.close()
    
    return redirect(url_for('configurations.list_configurations'))
