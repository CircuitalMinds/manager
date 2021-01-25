from flask import request, flash, url_for, redirect, render_template, jsonify
import yaml
import requests
from database import container_data, app, db


@app.route('/get_data/')
def get_data():
    if request.args.get('token') == app.config["SECRET_KEY"]:
        
        file_name = request.args.get('name')

        if file_name == "all":

            data = container_data.query.all()
            fdata = {}
            for file_data in data:
                fdata[file_data.id] = {"container": file_data.container, "name": file_data.name, "url": file_data.url, "status": file_data.status}

            return jsonify(fdata)

        else:

            file_data = container_data.query.filter(container_data.name == file_name).first_or_404(description='There is no data with {}'.format(file_name))
            fdata = {"container": file_data.container, "name": file_data.name, "url": file_data.url, "status": file_data.status}

            return jsonify(fdata)

    else:
        
        return "sorry, bad token"
        
@app.route('/delete_data/')
def delete_data():
    
    if request.args.get('token') == app.config["SECRET_KEY"]:
        file_name = request.args.get('name')
        file_data = container_data.query.filter(container_data.name == file_name).first_or_404(description='There is no data with {}'.format(file_name))
        db.session.delete(file_data)
        db.session.commit()

        return 'Record was successfully deleted'
    
    else:
        
        return "sorry, bad token"

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

@app.route('/add_data/', methods = ['GET', 'POST'])
def add_data():
    
    if request.method == 'POST':
    
       if not request.form['container'] or not request.form['name'] or not request.form['url'] or not request.form['status']:
    
          jsonify({"response": "Error, Please enter all the fields"})
       else:
          fdata = {"container": request.form['container'], "name": request.form['name'], "url": request.form['url'], "status": request.form['status']} 
          data = container_data(fdata['container'], fdata['name'], fdata['url'], fdata['status'])     
          db.session.add(data)
          db.session.commit()
          
          return jsonify({"response": "Record was successfully added"})
    
    else:
    
        fdata = {"container": request.args.get('container'), "name": request.args.get('name'), "url": request.args.get('url'), "status": request.args.get('status')} 
        data = container_data(fdata['container'], fdata['name'], fdata['url'], fdata['status'])
        db.session.add(data)
        db.session.commit()
        
        return jsonify({"response": "Record was successfully added"})

@app.route('/update_data/')
def update_data():
    
    if request.args.get('token') == app.config["SECRET_KEY"]:
        
        containers = yaml.load(requests.get('https://raw.githubusercontent.com/alanmatzumiya/server-admin/main/database_containers.yml').content, Loader=yaml.FullLoader)
        for cont in containers:
            for key in list(containers[cont].keys()):
                db.session.add(container_data(cont, key, containers[cont][key], "available"))
        
        notebooks = yaml.load(requests.get('https://raw.githubusercontent.com/alanmatzumiya/server-admin/main/database_notebooks.yml').content, Loader=yaml.FullLoader)
        for nbs in notebooks:
            for key in list(notebooks[nbs].keys()):
                db.session.add(container_data(nbs, key, notebooks[nbs][key], "available"))
        db.session.commit()
    
        return jsonify({"response": "Record was successfully updated"})
    
    else:
    
        return "sorry, bad token"

if __name__ == '__main__':
    db.create_all()
    app.run("https://circuitflow.herokuapp.com/", 80)
