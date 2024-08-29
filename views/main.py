from flask import render_template, request, flash, redirect, url_for
from app import app, db
from models.model import Inquiry,RegistrationForm, LoginForm , User , UpdateProfileForm, BookingForm, Booking,Package,ChangePasswordForm, Category, PackageType,admin_required,CategoryForm, PackageForm, UpdateBookingForm, ReportForm, AdminProfileForm, Payment,PaymentForm
from app import app, db, bcrypt
from flask_login import login_user, logout_user, login_required, current_user
from datetime import date  # Example import

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/trainers')
def trainers():
    return render_template('trainers.html')

@app.route('/equipment')
def equipment():
    return render_template('equipment.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # Save inquiry to the database
        inquiry = Inquiry(name=name, email=email, message=message)
        db.session.add(inquiry)
        db.session.commit()
        
        flash('Your inquiry has been sent!', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password, role='registered')
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Check email and password.', 'danger')
    return render_template('login.html', form=form)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('profile.html', form=form)


@app.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    form = BookingForm()
    form.package.choices = [(pkg.id, pkg.name) for pkg in Package.query.all()]
    if form.validate_on_submit():
        booking = Booking(user_id=current_user.id, package_id=form.package.data, status='confirmed')
        db.session.add(booking)
        db.session.commit()
        flash('Your package has been booked!', 'success')
        return redirect(url_for('booking_history'))
    return render_template('book.html', form=form)




@app.route('/booking-history')
@login_required
def booking_history():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('booking_history.html', bookings=bookings)


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password_hash, form.current_password.data):
            hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            current_user.password_hash = hashed_password
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Current password is incorrect.', 'danger')
    return render_template('change_password.html', form=form)


@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    total_bookings = Booking.query.count()
    active_packages = Package.query.filter_by(is_active=True).count()
    total_categories = Category.query.count()
    total_package_types = PackageType.query.count()
    return render_template('admin/dashboard.html', total_bookings=total_bookings,
                           active_packages=active_packages,
                           total_categories=total_categories,
                           total_package_types=total_package_types)


@app.route('/admin/categories')
@login_required
@admin_required
def manage_categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        new_category = Category(name=form.name.data)
        db.session.add(new_category)
        db.session.commit()
        flash('Category added successfully!')
        return redirect(url_for('manage_categories'))
    return render_template('admin/add_category.html', form=form)

@app.route('/admin/categories/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!')
    return redirect(url_for('manage_categories'))


@app.route('/admin/packages')
@login_required
@admin_required
def manage_packages():
    packages = Package.query.all()
    return render_template('admin/packages.html', packages=packages)

@app.route('/admin/packages/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_package():
    form = PackageForm()
    if form.validate_on_submit():
        new_package = Package(name=form.name.data, description=form.description.data,
                              price=form.price.data, package_type_id=form.package_type.data)
        db.session.add(new_package)
        db.session.commit()
        flash('Package added successfully!')
        return redirect(url_for('manage_packages'))
    return render_template('admin/add_package.html', form=form)

@app.route('/admin/packages/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_package(id):
    package = Package.query.get_or_404(id)
    db.session.delete(package)
    db.session.commit()
    flash('Package deleted successfully!')
    return redirect(url_for('manage_packages'))


@app.route('/admin/bookings')
@login_required
@admin_required
def manage_bookings():
    bookings = Booking.query.all()
    return render_template('admin/bookings.html', bookings=bookings)

@app.route('/admin/bookings/update/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update_booking(id):
    booking = Booking.query.get_or_404(id)
    form = UpdateBookingForm(obj=booking)
    if form.validate_on_submit():
        booking.status = form.status.data
        booking.payment_status = form.payment_status.data
        db.session.commit()
        flash('Booking updated successfully!')
        return redirect(url_for('manage_bookings'))
    return render_template('admin/update_booking.html', form=form, booking=booking)


@app.route('/admin/reports', methods=['GET', 'POST'])
@login_required
@admin_required
def generate_reports():
    form = ReportForm()
    bookings = []
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        bookings = Booking.query.filter(Booking.date.between(start_date, end_date)).all()
    return render_template('admin/reports.html', form=form, bookings=bookings)



@app.route('/admin/profile', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_profile():
    form = AdminProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/profile.html', form=form)

@app.route('/admin/change-password', methods=['GET', 'POST'])
@login_required
@admin_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('Password changed successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/change_password.html', form=form)


@app.route('/admin/process_payment', methods=['GET', 'POST'])
@admin_required
def process_payment():
    form = PaymentForm()
    form.booking_id.choices = [(booking.id, f'Booking #{booking.id} - {booking.user.username}') for booking in Booking.query.all()]
    
    if form.validate_on_submit():
        payment = Payment(
            booking_id=form.booking_id.data,
            payment_date=date.today(),
            amount=form.amount.data,
            payment_type=form.payment_type.data
        )
        db.session.add(payment)
        
        # Update the booking amount paid
        booking = Booking.query.get(form.booking_id.data)
        booking.amount_paid += form.amount.data
        
        # Update booking status if fully paid
        if booking.amount_paid >= booking.total_amount:
            booking.status = 'Paid'
        
        db.session.commit()
        flash('Payment processed successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/process_payment.html', form=form)


@app.route('/user/booking_history')
@login_required
def booking_history():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('user/booking_history.html', bookings=bookings)
