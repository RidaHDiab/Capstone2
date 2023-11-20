import base64
import urllib.parse

from PIL import Image
from flask import Flask, jsonify, redirect, url_for, render_template
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client.news

CORS(app)  # Enable CORS for your Flask app

@app.route('/')
def homepage():
    article = list(db.articles.find({}))
    for art in article:
        art["image"] = "/static/{}.jpeg".format(art["_id"])
    return render_template('homepage.html', data=article)


@app.route('/signup')
def signup():
    return render_template('signup.html')


if __name__ == '__main__':
    app.run()
