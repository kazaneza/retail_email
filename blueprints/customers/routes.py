# blueprints/customers/routes.py

from flask import render_template, request, redirect, url_for, flash
from . import customers_bp
from .forms import CustomerForm
from models import db, Customer
from sqlalchemy import or_

@customers_bp.route('/customers')
def customers():
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'name')
    page = request.args.get('page', 1, type=int)
    per_page = 50  # Adjust as needed

    query = Customer.query

    # Implement search functionality
    if search:
        query = query.filter(
            or_(
                Customer.short_name.ilike(f'%{search}%'),
                Customer.customer_id.ilike(f'%{search}%')
            )
        )

    # Implement sorting
    if sort_by == 'name':
        query = query.order_by(Customer.short_name)
    elif sort_by == 'status':
        query = query.order_by(Customer.status)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    customers_list = pagination.items

    return render_template('customers.html', customers=customers_list, search=search, sort_by=sort_by, pagination=pagination)

@customers_bp.route('/edit_customer/<int:id>', methods=['GET', 'POST'])
def edit_customer(id):
    form = CustomerForm()
    customer = Customer.query.get_or_404(id)

    if form.validate_on_submit():
        customer.email_d_1 = form.email.data
        customer.sms_d_1 = form.phone.data
        customer.status = int(form.status.data)
        try:
            db.session.commit()
            flash('Customer updated successfully', 'success')
            return redirect(url_for('customers.customers'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while updating the customer: {e}', 'danger')

    # Pre-fill form with existing data
    if request.method == 'GET':
        form.email.data = customer.email_d_1
        form.phone.data = customer.sms_d_1
        form.status.data = str(customer.status)

    return render_template('edit_customer.html', form=form, customer=customer)
