from typing import List
from flask import Flask, request
from flask import json
from flask.helpers import make_response, url_for
from flask.json import jsonify
from flask_mysqldb import MySQL
from werkzeug.exceptions import abort
from datetime import datetime

app = Flask(__name__)

# configuration a la connection mysql
app.config['MYSQL_HOST'] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config['MYSQL_PASSWORD'] = "Fr@16122018"
app.config['MYSQL_DB'] = "sakila"

mysql = MySQL(app)

# route pour recuperer la liste des acteurs de ma bdd
@app.route('/actors', methods=['GET'])
def get_actors():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM actor")
        reponse = cur.fetchall()
        cur.close()
        actors = []
        for actor in reponse:
            actor = make_actor(actor)
            actors.append(actor)
        return jsonify([make_public_actor(actor) for actor in actors])
    except Exception as e:
        print(e)
        abort(404)

# route pour recuperer un acteur de ma bdd
@app.route('/actors/<int:actor_id>', methods=['GET'])
def get_actor_by_id(actor_id):
    print(actor_id)
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM actor WHERE actor_id=%s", (str(actor_id),))
        reponse = cur.fetchone()
        cur.close()
        #print("Succeeded in getting {}".format(str(article_id)))
        return jsonify(make_public_actor(make_actor(reponse)))
    except Exception as e:
        print(f"Exception occured : {e}")
        abort(404)

# route pour modifier un article precise de ma bdd
@app.route('/actors/<int:actor_id>', methods=['PUT'])
def update_actor_by_id(actor_id):
    actor = get_actor_by_id(actor_id)
    if not request.json:
        abort(400)
    if "first_name" not in request.json or type(request.json['first_name']) != str:
        abort(400)
    if "last_name" in request.json and type(request.json['last_name']) != str:
        abort(400)
    # if "last_update" in request.json and type(request.json['last_update']) is not datetime:
    #     abort(400)
    try:
        first_name = request.json.get('first_name', actor.json['first_name'])
        last_name = request.json.get('last_name', actor.json['last_name'])
        last_update = request.json.get('last_update', actor.json['last_update'])
        cur = mysql.connection.cursor()
        cur.execute("UPDATE actor SET first_name=%s, last_name=%s WHERE actor_id=%s", (first_name, last_name,str(actor_id)))
        mysql.connection.commit()
        cur.close()
        return jsonify({'is':True })
    except Exception as e:
        print(e)
        return jsonify({'is':False})


# route pour ajouter une biere dans ma bdd
@app.route('/actors', methods=['POST'])
def create_actor():
    if not request.json and not "first_name" in request.json:
        abort(404)
    try:
        # creer les champs de ma nouvelle biere
        first_name = request.json.get('first_name','')
        last_name = request.json.get("last_name","")
        # creer ma connection et envoyer a ma bdd
        cur = mysql.connection.cursor()
        # get the max id in the db and insert a new value at max+1
        cur.execute("INSERT INTO actor(first_name, last_name, last_update) VALUES(%s,%s, %s)", (first_name, last_name, datetime.utcnow()))
        mysql.connection.commit()
        cur.close()
        return jsonify({'is':True})
    except Exception as e:
        print(e)
        return jsonify ({'is':False})

# fonction pour creer un actor a partir de la base de donnee actor
def make_actor(actor_object):
    list_actors = list(actor_object)
    new_actor = {}
    new_actor["actor_id"] = int(list_actors[0])
    new_actor["first_name"] = str(list_actors[1])
    new_actor["last_name"] = str(list_actors[2])  
    new_actor["last_update"] = list_actors[3]
    return new_actor

# fonction pour creer une url de facon dynamique a partir d'un actor
def make_public_actor(actor):
    public_actor = {}
    for argument in actor:
        if argument == "actor_id":
            public_actor['url'] = url_for('get_actor_by_id', actor_id = actor['actor_id'], _external=True)
        else:
            public_actor[argument] = actor[argument]
    return public_actor 

# route pour supprimer une biere de ma bdd
@app.route('/actors/<int:actor_id>', methods=['DELETE'])
def delete_actor(actor_id):
    actor = get_actor_by_id(actor_id)
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM actor WHERE actor_id=%s", (str(actor_id)))
        mysql.connection.commit()
        cur.close()
        return actor
    except Exception as e:
        print(e)
        return jsonify({'is':False})


# annotation app.route('URL')
@app.route('/', methods=['GET'])
def index():
    return "Welcome Actors!"

# lancer mon application
if __name__ == "__main__":
    app.run(debug=True)
