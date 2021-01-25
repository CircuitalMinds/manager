from flask import request, flash, url_for, redirect, render_template, jsonify
import yaml
import requests
from database import container_data, app, db


@app.route('/')
def show_data():
    
    return render_template('show_data.html', data = container_data.query.all())

@app.route('/get_data/')
def get_data():

    file_name = request.args.get('name')
    file_data = container_data.query.filter(container_data.name == file_name).first()
    fdata = {"container": file_data.container, "name": file_data.name, "url": file_data.url, "status": file_data.status}
    
    return jsonify(fdata)

@app.route('/get_playlist/')
def get_playlist():
    
    if request.args.get('token') == app.config["SECRET_KEY"]:

        data = container_data.query.filter(container_data.name.endswith(".mp4")).all()
        playlist = {}
    
        for fdata in data:
            playlist[fdata.name] = fdata.url
    
        return jsonify(playlist)
    
    else:
        
        return "sorry, bad token"

@app.route('/add_data', methods = ['GET', 'POST'])
def add_data():
    
    if request.method == 'POST':
    
       if not request.form['container'] or not request.form['name'] or not request.form['url'] or not request.form['status']:
    
          flash('Please enter all the fields', 'error')
       else:
        
          data = container_data(request.form['container'], request.form['name'], request.form['url'], request.form['status'])     
          db.session.add(data)
          db.session.commit()
          flash('Record was successfully added')
    
          return redirect(url_for('show_data'))
    
    return render_template('add_data.html')

@app.route('/update_data/')
def update_data():
    
    if request.args.get('token') == app.config["SECRET_KEY"]:
        
        containers = yaml.load(requests.get('https://raw.githubusercontent.com/alanmatzumiya/server-admin/main/database_containers.yml').content, Loader=yaml.FullLoader)
        for cont in containers:
            for key in list(containers[cont].keys()):
                db.session.add(container_data(cont, key, containers[cont][key], "available"))
    
        db.session.commit()
    
        return redirect(url_for('show_data'))
    
    else:
    
        return "sorry, bad token"

if __name__ == '__main__':
    db.create_all()
    app.run("https://circuitflow.herokuapp.com/", 80)
