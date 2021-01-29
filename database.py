from flask_sqlalchemy import SQLAlchemy
from flask import Flask


circuitflow = Flask(__name__)
circuitflow.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
circuitflow.config['SECRET_KEY'] = "circuitalminds"

db = SQLAlchemy(circuitflow)

class containers_data(db.Model):
    id = db.Column('file_id', db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    url = db.Column(db.String(100))
    args = { "attrs": ["name", "url"], 
    "path_data": "https://raw.githubusercontent.com/alanmatzumiya/server-admin/main/databases/containers.yml" }
    
    def __init__(self, data):       
       self.name = data["name"]
       self.url = data["url"]
      
    def __repr__(self):
    
        return '<containers_data %r>' % self.name

class notebooks_data(db.Model):
    id = db.Column('notebook_id', db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    url = db.Column(db.String(100))
    args = { "attrs": ["name", "url"], 
    "path_data": "https://raw.githubusercontent.com/alanmatzumiya/server-admin/main/databases/" }
    
    def __init__(self, data):
       self.name = data["name"]
       self.url = data["url"]
           
    def __repr__(self):
    
        return '<notebooks_data %r>' % self.name        

class repos_data(db.Model):
    id = db.Column('repo_id', db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    url = db.Column(db.String(100))
    args = { "attrs": ["name", "url"], 
    "path_data": "https://raw.githubusercontent.com/alanmatzumiya/server-admin/main/databases/" }
    
    def __init__(self, data):
       self.name = data["name"]
       self.url = data["url"]
           
    def __repr__(self):
    
        return '<repos_data %r>' % self.name
        
class users_data(db.Model):
    id = db.Column('user_id', db.Integer, primary_key = True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    args = { "attrs": ["username", "email"] }
    
    def __init__(self, data):
       self.username = data["username"]
       self.email = data["email"]
           
    def __repr__(self):
    
        return '<users_data %r>' % self.username 
        
class workers(db.Model):
    id = db.Column('worker_id', db.Integer, primary_key = True)
    worker = db.Column(db.String(100))
    job = db.Column(db.String(100))
    argument = db.Column(db.String(100))
    args = { "attrs": ["worker", "job", "argument"] }
    
    def __init__(self, worker, job, argument):
       self.worker = worker
       self.job = job
       self.argument = argument
           
    def __repr__(self):
    
        return '<workers %r>' % self.worker
