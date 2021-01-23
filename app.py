from flask import Flask, request, flash, url_for, redirect, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import yaml
import requests


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///container_data.sqlite3'
app.config['SECRET_KEY'] = "random string"

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
    
@app.route('/')
def show_data():
    
    return render_template('show_data.html', data = container_data.query.all())

@app.route('/get_data/')
def get_data():

    file_name = request.args.get('name')
    file_data = container_data.query.filter(container_data.name == file_name).first()
    fdata = {"url": file_data.url}
    
    return jsonify(fdata)

@app.route('/get_playlist/')
def get_playlist():
    
    data = container_data.query.filter(container_data.name.endswith(".mp4")).all()
    playlist = {}
    
    for fdata in data:
        playlist[fdata.name] = fdata.url
    
    return jsonify(playlist)

@app.route('/add_data', methods = ['GET', 'POST'])
def add_data():
    
    if request.method == 'POST':
    
       if not request.form['container'] or not request.form['name'] or not request.form['url']:
    
          flash('Please enter all the fields', 'error')
       else:
    
          data = container_data(request.form['container'], request.form['name'], request.form['url'])     
          db.session.add(data)
          db.session.commit()
          flash('Record was successfully added')
    
          return redirect(url_for('show_data'))
    
    return render_template('add_data.html')

@app.route('/update_data/')
def update_data():
        
    containers = yaml.load(requests.get('https://raw.githubusercontent.com/alanmatzumiya/server-admin/main/database_containers.yml').content, Loader=yaml.FullLoader)
    for cont in containers:
        for key in list(containers[cont].keys()):
            db.session.add(container_data(cont, key, containers[cont][key]))
    
    db.session.commit()
    
    return redirect(url_for('show_data'))

if __name__ == '__main__':
    db.create_all()
    app.run("https://circuitflow.herokuapp.com/", 80)
