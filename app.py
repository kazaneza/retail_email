from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, Email
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

CONFIG_FILE = 'config.json'

# Function to read data from config.json
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

# Function to write data to config.json
def write_config_file(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Function to read configurations
def read_configurations():
    data = read_config_file()
    return data.get('configurations', [])

# Function to read email settings
def read_email_settings():
    data = read_config_file()
    return data.get('email_settings', {'paused': False, 'batch_size': 50})

# Function to read sample data
def read_sample_data():
    data = read_config_file()
    return data.get('sample_data', {})

# Form for adding/editing configurations
class ConfigurationForm(FlaskForm):
    name = StringField('Configuration Name', validators=[DataRequired()])
    instance = StringField('Instance', validators=[DataRequired()])
    database_name = StringField('Database Name', validators=[DataRequired()])
    authentication_method = SelectField('Authentication Method', choices=[('SQL', 'SQL Authentication'), ('Windows', 'Windows Authentication')], validators=[DataRequired()])
    username = StringField('Username')
    password = PasswordField('Password')
    table_name = StringField('Table Name', validators=[DataRequired()])
    submit = SubmitField('Save')

# Function to get the active configuration
def get_active_configuration():
    configs = read_configurations()
    if configs:
        return configs[0]  # For simplicity, use the first configuration
    return None

# Dashboard route
@app.route('/')
def dashboard():
    email_settings = read_email_settings()
    email_sending_paused = email_settings.get('paused', False)
    email_batch_size = email_settings.get('batch_size', 50)

    # Fetch sample data for design purposes
    sample_data = read_sample_data()
    dashboard_stats = sample_data.get('dashboard_stats', {'remaining': 0, 'sent': 0, 'failed': 0})
    remaining = dashboard_stats.get('remaining', 0)
    sent = dashboard_stats.get('sent', 0)
    failed = dashboard_stats.get('failed', 0)

    return render_template(
        'dashboard.html',
        remaining=remaining,
        sent=sent,
        failed=failed,
        paused=email_sending_paused,
        batch_size=email_batch_size
    )

# Configurations list route
@app.route('/configurations')
def configurations():
    configs = read_configurations()
    return render_template('configurations.html', configs=configs)

# Add configuration route
@app.route('/add_configuration', methods=['GET', 'POST'])
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

        configs = read_configurations()
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
        write_config_file({'configurations': configs, 
                           'email_settings': read_email_settings(),
                           'sample_data': read_sample_data()})
        flash('Configuration added successfully', 'success')
        return redirect(url_for('configurations'))
    return render_template('edit_configuration.html', form=form, action='Add')

# Edit configuration route
@app.route('/edit_configuration/<int:id>', methods=['GET', 'POST'])
def edit_configuration(id):
    form = ConfigurationForm()
    configs = read_configurations()
    config = next((config for config in configs if config['id'] == id), None)

    if not config:
        flash('Configuration not found', 'danger')
        return redirect(url_for('configurations'))

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

        write_config_file({'configurations': configs, 
                           'email_settings': read_email_settings(),
                           'sample_data': read_sample_data()})
        flash('Configuration updated successfully', 'success')
        return redirect(url_for('configurations'))

    return render_template('edit_configuration.html', form=form, action='Edit')

# Delete configuration route
@app.route('/delete_configuration/<int:id>')
def delete_configuration(id):
    configs = read_configurations()
    configs = [config for config in configs if config['id'] != id]
    write_config_file({'configurations': configs, 
                       'email_settings': read_email_settings(),
                       'sample_data': read_sample_data()})
    flash('Configuration deleted', 'info')
    return redirect(url_for('configurations'))

# Customers list route
@app.route('/customers')
def customers():
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'name')

    sample_data = read_sample_data()
    customers_list = sample_data.get('customers', [])

    # Implement search functionality
    if search:
        customers_list = [
            customer for customer in customers_list
            if search.lower() in customer['name'].lower() or search.lower() in customer['customer_id'].lower()
        ]

    # Implement sorting
    if sort_by == 'name':
        customers_list.sort(key=lambda x: x['name'])
    elif sort_by == 'status':
        customers_list.sort(key=lambda x: x['status'])

    return render_template('customers.html', customers=customers_list, search=search, sort_by=sort_by)

# Edit customer route
@app.route('/edit_customer/<int:id>', methods=['GET', 'POST'])
def edit_customer(id):
    # Placeholder implementation for design purposes
    # In a real application, you would fetch and update customer data here
    # For now, we'll just render the template with a sample customer
    class CustomerForm(FlaskForm):
        email = StringField('Email', validators=[Email()])
        phone = StringField('Phone', validators=[DataRequired()])
        submit = SubmitField('Save')

    form = CustomerForm()
    if form.validate_on_submit():
        # Handle form submission
        flash('Customer updated successfully (simulated)', 'success')
        return redirect(url_for('customers'))

    # Sample customer data
    customer = {
        'id': id,
        'name': f'Sample Customer {id}',
        'email': 'sample@example.com',
        'phone': '1234567890'
    }

    return render_template('edit_customer.html', form=form, customer=customer)

# Email settings route
@app.route('/email_settings', methods=['GET', 'POST'])
def email_settings():
    email_settings = read_email_settings()
    if request.method == 'POST':
        email_sending_paused = 'pause' in request.form
        batch_size = int(request.form.get('batch_size', 50))
        email_settings['paused'] = email_sending_paused
        email_settings['batch_size'] = batch_size
        # Write updated settings back to config.json
        data = read_config_file()
        data['email_settings'] = email_settings
        write_config_file(data)
        flash('Email settings updated successfully', 'success')
        return redirect(url_for('dashboard'))
    return render_template('email_settings.html', paused=email_settings.get('paused', False), batch_size=email_settings.get('batch_size', 50))

# Failed emails route
@app.route('/failed_emails')
def failed_emails():
    sample_data = read_sample_data()
    failed_list = sample_data.get('failed_emails', [])
    return render_template('failed_emails.html', failed_list=failed_list)

# Download failed emails as JSON route
@app.route('/download_failed_json')
def download_failed_json():
    sample_data = read_sample_data()
    failed_list = sample_data.get('failed_emails', [])
    # Convert to JSON and send as file
    return send_file(
        io.BytesIO(json.dumps(failed_list, indent=4).encode()),
        mimetype='application/json',
        as_attachment=True,
        attachment_filename='failed_emails.json'
    )

if __name__ == '__main__':
    app.run(debug=True)
