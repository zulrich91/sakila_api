from typing import List
from flask import Flask, request
from flask import json
from flask.helpers import make_response, url_for
from flask.json import jsonify
from flask_mysqldb import MySQL
from werkzeug.exceptions import abort

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

# route pour recuperer un actor de ma bdd
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


# fonction pour creer une marque a partir de la base de donnee marque
def make_actor(actor_object):
    list_actors = list(actor_object)
    new_actor = {}
    new_actor["actor_id"] = int(list_actors[0])
    new_actor["first_name"] = str(list_actors[1])
    new_actor["last_name"] = str(list_actors[2])  
    new_actor["last_update"] = str(list_actors[3])
    return new_actor

# fonction pour creer une url de facon dynamique a partir d'une marque
def make_public_actor(actor):
    public_actor = {}
    for argument in actor:
        if argument == "actor_id":
            public_actor['url'] = url_for('get_actor_by_id', actor_id = actor['actor_id'], _external=True)
        else:
            public_actor[argument] = actor[argument]
    return public_actor 

# annotation app.route('URL')
@app.route('/', methods=['GET'])
def index():
    return "Welcome Actors!"

# lancer mon application
if __name__ == "__main__":
    app.run(debug=True)
