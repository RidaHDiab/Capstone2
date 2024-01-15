import sys

from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from werkzeug.serving import make_server

from NewsCrawling import DataExtractor

app = Flask(__name__)

da = DataExtractor()


@app.route('/start_article_gathering', methods=['GET', 'POST'])
def start_article_gathering():
    da.start()


#@app.route('/stop_extraction', methods=['GET', 'POST'])
#def stop_extraction():
  #  sys.exit()


if __name__ == '__main__':
    app.run()
