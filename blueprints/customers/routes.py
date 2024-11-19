# blueprints/customers/routes.py

from flask import render_template, request, redirect, url_for, flash
from . import customers_bp
from .forms import CustomerForm
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

@customers_bp.route('/customers')
def customers():
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'name')

    data = read_config_file()
    customers_list = data.get('sample_data', {}).get('customers', [])

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

@customers_bp.route('/edit_customer/<int:id>', methods=['GET', 'POST'])
def edit_customer(id):
    form = CustomerForm()
    data = read_config_file()
    customers = data.get('sample_data', {}).get('customers', [])
    customer = next((customer for customer in customers if customer['id'] == id), None)

    if not customer:
        flash('Customer not found', 'danger')
        return redirect(url_for('customers.customers'))

    if form.validate_on_submit():
        customer['email'] = form.email.data
        customer['phone'] = form.phone.data

        # Optionally, update dashboard stats if needed
        write_config_file(data)
        flash('Customer updated successfully', 'success')
        return redirect(url_for('customers.customers'))

    # Pre-fill form with existing data
    if request.method == 'GET':
        form.email.data = customer.get('email', '')
        form.phone.data = customer.get('phone', '')

    return render_template('edit_customer.html', form=form, customer=customer)
