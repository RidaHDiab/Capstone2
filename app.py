from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client.news
CORS(app)  # Enable CORS for your Flask app


@app.route('/articles', methods=['GET'])
def get_articles():
    articles = list(db.articles.find({}, {'_id': 0}))

    return jsonify({'articles': articles})


@app.route('/articles/month', methods=['GET'])
def get_articles_per_month():
    regex_pattern = r"^\d{4}-\d{2}"  # Regex pattern for "YYYY-MM"
    pipeline = [
        {"$match": {"published_time": {"$exists": True, "$regex": regex_pattern}}},
        {"$project": {
            "year": {"$toInt": {"$substr": ["$published_time", 0, 4]}},
            "month": {"$toInt": {"$substr": ["$published_time", 5, 2]}}
        }},
        {"$group": {
            "_id": {"year": "$year", "month": "$month"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id.year": 1, "_id.month": 1}},
        {"$project": {
            "_id": 0,

            "month": "$_id.month",
            "count": 1
        }}
    ]
    result = list(db.articles.aggregate(pipeline))
    return jsonify({'articles_per_month': result})


@app.route('/articles/section', methods=['GET'])
def get_article_section_count():
    pipeline = [
        {"$match": {"article_section": {"$exists": True}}},
        {"$group": {
            "_id": "$article_section",
            "count": {"$sum": 1}
        }},
        {"$project": {
            "_id": 0,
            "article_section": "$_id",
            "count": 1
        }}
    ]

    result = list(db.articles.aggregate(pipeline))

    return jsonify({'article_section_count': result})


@app.route('/articles/wordcount', methods=['GET'])
def get_word_count_distribution():
    pipeline = [
        {"$group": {
            "_id": {"$ifNull": ["$word_count", "null"]},
            "count": {"$sum": 1}
        }},
        {"$project": {
            "_id": 0,
            "word_count": "$_id",
            "count": 1
        }}
    ]
    result = list(db.articles.aggregate(pipeline))

    return jsonify({'word_count_distribution': result})


@app.route('/articles/section/wordcount', methods=['GET'])
def get_avg_word_count_by_section():
    pipeline = [
        {"$match": {"word_count": {"$exists": True}}},
        {"$group": {
            "_id": "$article_section",
            "avg_word_count": {"$avg": "$word_count"},
            "count": {"$sum": 1}
        }},
        {"$project": {
            "_id": 0,
            "article_section": "$_id",
            "avg_word_count": 1,
            "count": 1
        }}
    ]

    result = list(db.articles.aggregate(pipeline))

    return jsonify({'avg_word_count_by_section': result})

if __name__ == '__main__':
    app.run()