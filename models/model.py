from app import db
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
from datetime import date  # Example import


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # guest, registered, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200))

    def __repr__(self):
        return f'<Category {self.name}>'


class PackageType(db.Model):
    __tablename__ = 'package_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    duration_in_months = db.Column(db.Integer, nullable=False)  # e.g., 1 for monthly, 12 for yearly

    def __repr__(self):
        return f'<PackageType {self.name}>'


class Package(db.Model):
    __tablename__ = 'packages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    package_type_id = db.Column(db.Integer, db.ForeignKey('package_types.id'), nullable=False)
    
    category = db.relationship('Category', backref=db.backref('packages', lazy=True))
    package_type = db.relationship('PackageType', backref=db.backref('packages', lazy=True))

    def __repr__(self):
        return f'<Package {self.name}>'


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)  # e.g., 'confirmed', 'pending', 'cancelled'
    
    user = db.relationship('User', backref=db.backref('bookings', lazy=True))
    package = db.relationship('Package', backref=db.backref('bookings', lazy=True))

    def __repr__(self):
        return f'<Booking {self.id} - User: {self.user_id} - Package: {self.package_id}>'



class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(db.String(20), nullable=False)  # e.g., 'completed', 'pending'

    booking = db.relationship('Booking', backref=db.backref('payments', lazy=True))

    def __repr__(self):
        return f'<Payment {self.id} - Booking: {self.booking_id} - Amount: {self.amount}>'



class AdminSettings(db.Model):
    __tablename__ = 'admin_settings'

    id = db.Column(db.Integer, primary_key=True)
    setting_name = db.Column(db.String(50), nullable=False, unique=True)
    setting_value = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<AdminSettings {self.setting_name}>'
    
    
class Inquiry(db.Model):
    __tablename__ = 'inquiries'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Inquiry {self.name}>'

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already in use.')
        
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

class BookingForm(FlaskForm):
    package = SelectField('Package', choices=[], coerce=int)
    submit = SubmitField('Book')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Save')

class PackageForm(FlaskForm):
    name = StringField('Package Name', validators=[DataRequired(), Length(min=2, max=50)])
    category = SelectField('Category', coerce=int)
    submit = SubmitField('Save')

class UpdateBookingForm(FlaskForm):
    status = SelectField('Booking Status', choices=[('pending', 'Pending'), ('confirmed', 'Confirmed')], validators=[DataRequired()])
    submit = SubmitField('Update')

class ReportForm(FlaskForm):
    start_date = StringField('Start Date', validators=[DataRequired()])
    end_date = StringField('End Date', validators=[DataRequired()])
    submit = SubmitField('Generate Report')

class AdminProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Update Profile')


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

class PaymentForm(FlaskForm):
    booking_id = SelectField('Booking', coerce=int, validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired()])
    payment_type = StringField('Payment Type', validators=[DataRequired()])
    submit = SubmitField('Process Payment')
