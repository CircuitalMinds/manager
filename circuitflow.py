from flask import request, jsonify, Flask
import yaml
from flask_sqlalchemy import SQLAlchemy


circuitflow = Flask(__name__)
circuitflow.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
circuitflow.config['SECRET_KEY'] = "circuitalminds"

_config = yaml.load(open('./manager/_config.yml'), Loader=yaml.FullLoader)
HOST = _config["HOST"]
PORT = _config["PORT"]
DEBUG = _config["DEBUG"]

db = SQLAlchemy(circuitflow)

class music_data(db.Model):
    id = db.Column('file_id', db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    url = db.Column(db.String(100))
    args = {
        "attrs": ["name", "url"]
    }
    
    def __init__(self, data):       
       self.name = data["name"]
       self.url = data["url"]

    def __repr__(self):
    
        return '<containers_data %r>' % self.name

class notebooks_data(db.Model):
    id = db.Column('notebook_id', db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    url = db.Column(db.String(100))
    args = {
        "attrs": ["name", "url"]
    }
    
    def __init__(self, data):
       self.name = data["name"]
       self.url = data["url"]
           
    def __repr__(self):
    
        return '<notebooks_data %r>' % self.name        

class repos_data(db.Model):
    id = db.Column('repo_id', db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    url = db.Column(db.String(100))
    args = {
        "attrs": ["name", "url"]
    }
    
    def __init__(self, data):
       self.name = data["name"]
       self.url = data["url"]
           
    def __repr__(self):
    
        return '<repos_data %r>' % self.name


class users_data(db.Model):
    id = db.Column('user_id', db.Integer, primary_key = True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    args = {
        "attrs": ["username", "email"]
    }
    
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
    status = db.Column(db.String(100))
    args = {
        "attrs": ["worker", "job", "argument", "status"]
    }
    
    def __init__(self, worker, job, argument, status):
       self.worker = worker
       self.job = job
       self.argument = argument
       self.status = status
           
    def __repr__(self):
    
        return '<workers %r>' % self.worker

    
books_data = {"music": music_data, "notebooks": notebooks_data, "repositories": repos_data}


@circuitflow.route('/workers_info')
def workers_info():
    worker = request.args.get('worker')
    job = request.args.get('job')
    argument = request.args.get('argument')
    status = request.args.get('status')
    option = request.args.get('option')
    if request.args.get('token') == circuitflow.config['SECRET_KEY']:
        if option is None:
            workers_data = workers.query.all()
            fdata = {}
            for data in workers_data:
                fdata[data.id] = {
                    "worker": data.worker,
                    "job": data.job,
                    "argument": data.argument,
                    "status": data.status
                }
            return jsonify(fdata)
        elif option == "update":
            workers.query.filter(workers.worker == worker).first_or_404(
                    description='There is no data with {}'.format(worker)
                )
            workers.query.filter(workers.worker == worker).update(
                {"worker": worker,
                 "job": job,
                 "argument": argument,
                 "status": status
                 }
            )
            db.session.commit()
            return jsonify(
                {
                    "request": "data updated"
                }
            )
        else:
            if option == "delete":
                worker_data = workers.query.filter(workers.worker == worker).first_or_404(
                    description='There is no data with {}'.format(worker)
                )
                db.session.delete(worker_data)
                db.session.commit()
                return jsonify(
                    {
                        "response": "data deleted"
                    }
                )
            elif option == "add":
                worker_data = workers(worker, job, argument, status)
                db.session.add(worker_data)
                db.session.commit()
                return jsonify(
                    {
                        "response": "data added"
                    }
                )
            else:
                return jsonify(
                    {
                        "response": "bad option"
                    }
                )
    else:
        return "sorry, bad token"


@circuitflow.route('/books')
def books():
    if request.args.get('token') == circuitflow.config['SECRET_KEY']:
        book = request.args.get('book')
        name = request.args.get('name')
        data = books_data[book].args["data"][name]
        if request.args.get('register'):
            refs_data = [refs.name for refs in books_data[book].query.all()]
            if refs_data:
                for key in list(data.keys()):
                    db.session.add(
                        books_data[book](
                            {
                                "name": key,
                                "url": data[key]
                            }
                        )
                    )
                db.session.commit()
            else:
                for key in list(data.keys()):
                    if not key in refs_data:
                        db.session.add(
                            books_data[book](
                                {
                                    "name": key,
                                    "url": data[key]
                                }
                            )
                        )
                db.session.commit()
            return jsonify(
                {
                    "response": "success"
                }
            )
        else:
            return jsonify(data)
    else:

        return "sorry, bad token"


@circuitflow.route('/get_data')
def get_data():
    if request.args.get('token') == circuitflow.config['SECRET_KEY']:
        name = request.args.get('name')
        option = request.args.get("option")
        book = request.args.get('book')
        data_object = books_data[book]
        data_dict = {}
        if name is None and option is not None:
            if option == "playlist":
                playlist = data_object.query.filter(data_object.name.endswith("mp4")).all()
                for song in playlist:
                    data_dict[song.name] = song.url
            elif option == "notebooks":
                    notebooks = data_object.query.filter(data_object.name.endswith("ipynb")).all()
                    for nb in notebooks:
                        data_dict[nb.name] = nb.url
        elif name is None:
            data_files = data_object.query.all()
            for fdata in data_files:
                data_dict[fdata.id] = {}
                for key in data_object.args["attrs"]:
                    data_dict[fdata.id][key] = fdata.__dict__[key]
        else:
            fdata = data_object.query.filter(data_object.name == name).first_or_404(
                description='There is no data with {}'.format(name)
            )
            data_dict[fdata.id] = {}
            for key in data_object.args["attrs"]:
                data_dict[fdata.id][key] = fdata.__dict__[key]
        return jsonify(data_dict)

    else:
        return "sorry, bad token"

@circuitflow.route('/delete_data')
def delete_data():
    if request.args.get('token') == circuitflow.config["SECRET_KEY"]:
        name = request.args.get('name')
        data = request.args.get('data')
        book = request.args.get('book')
        data_object = books_data[book]
        data_file = data_object.query.filter(data_object.name == name).first_or_404(
            description='There is no data with {}'.format(name)
        )
        db.session.delete(data_file)
        db.session.commit()
        return jsonify(
            {
                "response": "success"
            }
        )
    else:
        return "sorry, bad token"


@circuitflow.route('/add_data')
def add_data():
    if request.args.get('token') == circuitflow.config["SECRET_KEY"]:
        name = request.args.get('name')
        argument = request.args.get('argument')
        book = request.args.get('book')
        data_object = books_data[book]
        attributes = data_object.args["attrs"]
        db.session.add(
            data_object(
                {
                    attributes[0]: name,
                    attributes[1]: argument
                }
            )
        )
        db.session.commit()
        return jsonify(
            {
                "response": "success"
            }
        )
    else:
        return "sorry, bad token"


@circuitflow.route('/update_data')
def update_data():
    if request.args.get('token') == circuitflow.config["SECRET_KEY"]:
        name = request.args.get('name')
        argument = request.args.get('argument')
        book = request.args.get('book')
        data_object = books_data[book]
        data_object.query.filter(data_object.name == name).first_or_404(
            description='There is no data with {}'.format(name)
        )
        key = data_object.args["attrs"][1]
        data_object.query.filter(data_object.name == name).update(
            {
                key: argument
            }
        )
        db.session.commit()
        return jsonify(
            {
                "response": "success"
            }
        )
    else:
        return "sorry, bad token"


if __name__ == '__main__':
    db.create_all()
    circuitflow.run(host=HOST, port=80)
