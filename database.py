from flask_sqlalchemy import SQLAlchemy
from flask import Flask

# app manager
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///container_data.sqlite3'
app.config['SECRET_KEY'] = "circuitalminds"

# setup database
db = SQLAlchemy(app)

class container_data(db.Model):
    id = db.Column('file_id', db.Integer, primary_key = True)
    container = db.Column(db.String(100))
    name = db.Column(db.String(100))
    url = db.Column(db.String(100))
    
    def __init__(self, container, name, url):
       
       self.container = container
       self.name = name
       self.url = url
           
    def __repr__(self):
    
        return '<container_data %r>' % self.name 
