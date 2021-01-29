from flask import request, flash, url_for, redirect, render_template, jsonify
import yaml
import requests
from database import workers, containers_data, notebooks_data, repos_data, circuitflow, db
from tools import data_files


books_data = { "containers": containers_data, "notebooks": notebooks_data, "repos": repos_data }

@circuitflow.route('/workers')
def worker():
    
    option = request.args.get('option')
    worker = request.args.get('worker')
    job = request.args.get('job')
    argument = request.args.get('argument')
    
    if option == "view":
        workers_data = workers.query.all()
        fdata = {}
        for data in workers_data:
            fdata[data.id] = {"worker": data.worker, "job": data.job, "argument": data.argument}
        
        return jsonify(fdata)
    
    elif option == "delete":
        worker_data = workers.query.filter(workers.worker == worker).first_or_404(description='There is no data with {}'.format(worker))
        db.session.delete(worker_data)
        db.session.commit()
        
        return jsonify({"response": "Record was successfully deleted"})  
    
    else:
        worker_data = workers(worker, job, argument)
        db.session.add(worker_data)
        db.session.commit()
        
        return jsonify({"response": "Record was successfully added"})
    
@circuitflow.route('/get_data/<book>')
def get_data(book):

    if request.args.get('token') == circuitflow.config['SECRET_KEY']:
        file_name = request.args.get("name")
        fdata = {}
        if file_name == "playlist":
            data = books_data[book].query.filter(books_data[book].name.endswith(tuple(["mkv", "webm", "mp4"]))).all()
            for file_data in data:
                fdata[file_data.name] = file_data.url     
            return jsonify(fdata)
        elif file_name == None:
            data = books_data[book].query.all()
            for file_data in data:
                fdata[file_data.id] = {}
                for key in books_data[book].args["attrs"]:
                    fdata[file_data.id][key] = file_data.__dict__[key]     
            return jsonify(fdata)
        else:
            file_data = books_data[book].query.filter(books_data[book].name == file_name).first_or_404(description='There is no data with {}'.format(file_name))
            fdata[file_data.id] = {}
            for key in books_data[book].args["attrs"]:
                fdata[file_data.id][key] = file_data.__dict__[key]
            return jsonify(fdata)
    else:
        return "sorry, bad token"
        
@circuitflow.route('/update_data/<book>')
def update_data(book):
    
    if request.args.get('token') == circuitflow.config['SECRET_KEY']:
        dict_data = data_files(books_data[book].args["path_data"])
        refs_data = [ refs.name for refs in books_data[book].query.all() ]
        for file_data in list(dict_data.keys()):
            if not file_data in refs_data:
                db.session.add(books_data[book]({"name": file_data, "url": dict_data[file_data]}))
        db.session.commit()
        return jsonify({"response": "Record was successfully updated"})
    else:
        return "sorry, bad token"
                     
@circuitflow.route('/delete_data/<book>')
def delete_data(book):
  
    if request.args.get('token') == circuitflow.config["SECRET_KEY"]:
        file_name = request.args.get('name')
        file_data = books_data[book].query.filter(books_data[book].name == file_name).first_or_404(description='There is no data with {}'.format(file_name))
        db.session.delete(file_data)
        db.session.commit()
        return 'Record was successfully deleted'  
    else:
        return "sorry, bad token"
    
@circuitflow.route('/add_data/<book>', methods = ['GET', 'POST'])
def add_data(book):
    
    if request.method == 'POST':
       if not request.form['name'] or not request.form['url']:
          return jsonify({"response": "Error, Please enter all the fields"})
       else:
          db.session.add(books_data[book]({ "name": request.form['name'], "url": request.form['url'] }))
          db.session.commit()
          return jsonify({"response": "Record was successfully added"})
    else:
        db.session.add(books_data[book]({ "name": request.args.get('name'), "url": request.args.get('url') }))
        db.session.commit()
        return jsonify({"response": "Record was successfully added"})

if __name__ == '__main__':
    db.create_all()
    circuitflow.run("127.0.0.1", 4000)
