import base64
import time
import urllib.parse

from PIL import Image
from flask import Flask, jsonify, redirect, url_for, render_template, request, flash, session
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
app.secret_key = 'Ma5asak!@#'
client = MongoClient('mongodb://localhost:27017/')
db = client.news

CORS(app)  # Enable CORS for your Flask app


@app.route('/')
def homepage():
    article = list(db.articles.find({}))
    for art in article:
        art["image"] = "/static/{}.jpeg".format(art["_id"])
    role = session.get('role')
    return render_template('homepage.html', data=article, data1=role)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'password': request.form.get('password')
        }
        db.users.insert_one(user)
        return redirect('/')
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = {
            'email': request.form.get('email'),
            'password': request.form.get('password')
        }
        userdb = db.users.find_one({'email': user['email']})
        print(userdb)
        if not userdb['password'] == user['password']:
            message = 'Email or password incorrect'
            return render_template('login.html', data=message)
        session['role'] = userdb["role"]
        return redirect('/')
    return render_template('Login.html')


if __name__ == '__main__':
    app.run()
