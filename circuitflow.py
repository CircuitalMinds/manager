from flask import request, flash, url_for, redirect, render_template, jsonify
import yaml
import requests
from database import workers, containers_data, notebooks_data, repos_data, circuitflow, db
from tools import data_files

books_data = {"containers": containers_data, "notebooks": notebooks_data, "repos": repos_data}
_config = yaml.load(open("./_config.yml"), Loader=yaml.FullLoader)

SETTINGS = _config["SETTINGS"]
HOST = SETTINGS["HOST"]
PORT = SETTINGS["PORT"]
DEBUG = SETTINGS["DEBUG"]


@circuitflow.route('/workers')
def worker():
    worker = request.args.get('worker')
    job = request.args.get('job')
    argument = request.args.get('argument')
    status = request.args.get('status')
    option = request.args.get('query')

    if request.args.get('token') == circuitflow.config['SECRET_KEY']:

        if option is None:
            workers_data = workers.query.all()
            fdata = {}
            for data in workers_data:
                fdata[data.id] = {"worker": data.worker, "job": data.job, "argument": data.argument, "status": status}
            return jsonify(fdata)
        elif option == "update":
            workers.query.filter(workers.worker == worker).first_or_404(
                    description='There is no data with {}'.format(worker)
                )
            workers.query.filter(workers.worker == worker).update({"worker": data.worker, "job": data.job, "argument": data.argument, "status": status})    
            db.session.commit()
            return jsonify({"request": "data updated"})
        else:
            if option == "add":
                worker_data = workers.query.filter(workers.worker == worker).first_or_404(
                    description='There is no data with {}'.format(worker)
                )
                db.session.delete(worker_data)
                db.session.commit()
                return jsonify({"response": "data added"})
            elif option == "delete":
                worker_data = workers(worker, job, argument, status)
                db.session.add(worker_data)
                db.session.commit()
                return jsonify({"response": "data deleted"})
            else:

                return jsonify({"response": "bad option"})

    else:

        return "sorry, bad token"


@circuitflow.route('/books')
def data():
    if request.args.get('token') == circuitflow.config['SECRET_KEY']:

        book = request.args.get('book')
        name = request.args.get('name')
        data = books_data[book].args["data"][name]

        if request.args.get('register'):
            refs_data = [refs.name for refs in books_data[book].query.all()]
            if refs_data:
                for key in list(data.keys()):
                    db.session.add(books_data[book]({"name": key, "url": data[key]}))
                db.session.commit()
            else:
                for key in list(data.keys()):
                    if not key in refs_data:
                        db.session.add(books_data[book]({"name": key, "url": data[key]}))
                db.session.commit()
            return jsonify({"response": "success"})
        else:
            return jsonify(data)
    else:

        return "sorry, bad token"


@circuitflow.route('/get_data')
def get_data():
    if request.args.get('token') == circuitflow.config['SECRET_KEY']:
        data = request.args.get('data')
        name = request.args.get('name')
        option = request.args.get("option")
        data_object = books_data[data]
        data_dict = {}
        if option == "playlist":
            playlist = data_object.query.filter(data_object.name.endswith("mp4")).all()
            for song in playlist:
                data_dict[song.name] = song.url
            return jsonify(data_dict)
        elif name is None and option is None:
            data_files = data_object.query.all()
            for fdata in data_files:
                data_dict[fdata.id] = {}
                for key in data_object.args["attrs"]:
                    data_dict[fdata.id][key] = fdata.__dict__[key]
            return jsonify(data_dict)
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
        data_object = books_data[data]
        data_file = data_object.query.filter(data_object.name == name).first_or_404(
            description='There is no data with {}'.format(name)
        )
        db.session.delete(data_file)
        db.session.commit()
        return jsonify({"response": "success"})
    else:
        return "sorry, bad token"


@circuitflow.route('/add_data')
def add_data():
    if request.args.get('token') == circuitflow.config["SECRET_KEY"]:
        name = request.args.get('name')
        argument = request.args.get('argument')
        data = request.args.get('data')
        data_object = books_data[data]
        attributes = data_object.args["attrs"]
        db.session.add(data_object({attributes[0]: name, attributes[1]: argument}))
        db.session.commit()
        return jsonify({"response": "success"})

    else:
        return "sorry, bad token"


@circuitflow.route('/update_data')
def update_data():
    if request.args.get('token') == circuitflow.config["SECRET_KEY"]:
        name = request.args.get('name')
        argument = request.args.get('argument')
        data = request.args.get('data')
        data_object = books_data[data]
        data_object.query.filter(data_object.name == name).first_or_404(
            description='There is no data with {}'.format(name)
        )
        key = data_object.args["attrs"][1]
        data_object.query.filter(data_object.name == name).update({key: argument})
        db.session.commit()
        return jsonify({"response": "success"})
    else:
        return "sorry, bad token"


if __name__ == '__main__':
    db.create_all()
    circuitflow.run(HOST, PORT, DEBUG)
