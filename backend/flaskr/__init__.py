from flask import Flask
from flask_migrate import Migrate 
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager




app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Nautilus5he!@localhost:5432/akdablog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER']='smtp.googlemail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
app.config['MAIL_USERNAME']="adedamolabasit09@gmail.com"
app.config['MAIL_PASSWORD']="Nautilus6he!"

mail=Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.init_app(app)
