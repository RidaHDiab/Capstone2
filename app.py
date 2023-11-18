from flask import Flask, jsonify, redirect, url_for, render_template
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client.news

CORS(app)  # Enable CORS for your Flask app


@app.route('/')
def homepage():
    article = db.articles.find()
    return render_template('homepage.html',data=article)


if __name__ == '__main__':
    app.run()
