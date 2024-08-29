from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import urllib

app = Flask(__name__)

# Configure the Database URI: Replace with your actual SQL Server details
params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};"
                                 "SERVER=DESKTOP-0G8418J;"
                                 "DATABASE=Gym_ManagementSystem;"
                                  "Trusted_Connection=yes;" 
                                 )

app.config['SQLALCHEMY_DATABASE_URI'] = f'mssql+pyodbc:///?odbc_connect={params}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

  # Import and register blueprints or models here
from models import User, Category, PackageType, Package, Booking, Payment, AdminSettings, Inquiry ,RegistrationForm,LoginForm,UpdateProfileForm,BookingForm,ChangePasswordForm

if __name__ == '__main__':
    app.run(debug=True)
