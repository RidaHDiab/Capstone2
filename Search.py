from datetime import datetime
import json
from dateutil import parser
from urllib.error import HTTPError

import pyodbc
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from requests import RequestException

from Compare import Compare

from DatabaseConnection import Database

db = Database()

api_key = "AIzaSyDznFG_4V6H2X8Dx-BpzjhFvHnGj856ckA"
cx = "e11be5f70b2dc4e20"

base_url = "https://www.googleapis.com/customsearch/v1"


def generate_google_dork_query(site, keywords):
    site_operator = f"site:{site}"

    keywords_to_search = [keyword.strip() for keyword in keywords.split(',')]

    keywords_operator = " OR ".join(f'"{keyword.replace(" ", " ")}"' for keyword in keywords_to_search)

    google_dork_query = f"{site_operator} {keywords_operator}"

    return google_dork_query


class Search:

    def search_may(self, keywords):
        print(keywords)
        query = generate_google_dork_query("almayadeen.net", keywords)
        params = {'q': query, 'key': api_key, 'cx': cx}
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            results = response.json()

            titles = [item.get('title', '') for item in results.get('items', [])]
            urls = [item['link'] for item in results.get('items', [])]

            print(results)
        except HTTPError as e:
            print(e)
        if not titles:
            return
        for url in urls:
            if "/news/" in url:
                extract_mayadeen(url)

    def search_BBC(self, keywords):
        print(keywords)
        query = generate_google_dork_query("bbc.com", keywords)
        params = {'q': query, 'key': api_key, 'cx': cx}
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            results = response.json()

            titles = [item.get('title', '') for item in results.get('items', [])]
            urls = [item['link'] for item in results.get('items', [])]
        except HTTPError as e:
            print(e)
        if not titles:
            return
        for url in urls:
            if "/news/" in url:
                extract_BBC(url)

def extract_BBC(url):

    print('start extraction from BBC')
    connect_timeout = 100  # seconds
    read_timeout = 500  # seconds

    try:
        response = requests.get(url, timeout=(connect_timeout, read_timeout))
        html_content = response.content
        soup = BeautifulSoup(html_content, "lxml")

        # Extract the article body
        article_body = soup.find("article", class_="ssrcss-pv1rh6-ArticleWrapper e1nh2i2l5")

        article_text = ""
        for paragraph in article_body.find_all('p'):
            article_text += paragraph.get_text()

        print("article" + article_text + "end of article")
        # Find all script tags containing JSON-LD data
        script_tags = soup.find_all("script", type="application/ld+json")

        # Extract data from the first script tag
        if script_tags:
            first_script_tag = script_tags[0]
            json_ld_content = json.loads(first_script_tag.string)
            print(json_ld_content)

            title = soup.find('header', class_="ssrcss-1eqcsb1-HeadingWrapper e1nh2i2l4").find('h1').get_text()
            CIE_query = f"select id from may_art where title = '{title}';"
            db.init()
            id = db.db_execute(CIE_query)
            if not id is None:
                return
            description = soup.find('meta', {'name': 'description', 'data-rh': 'true'}).get('content')
            keywords = json_ld_content.get("keywords", None)
            author = json_ld_content.get("author", {}).get("name", None)
            published_time = datetime.strptime(json_ld_content.get("datePublished", None), '%Y-%m-%dT%H:%M:%S.%fZ').date() if json_ld_content.get("datePublished", None) else None
            article_body = article_text

            title = title.replace('\'', '"')
            description = description.replace('\'', '"')
            article_body = article_body.replace('\'', '"')

            insert_query = f"INSERT INTO {'bbc_art'} (title, description, body, keywords, author, publishedTime) OUTPUT INSERTED.id VALUES ('{title}','{description}', '{article_body}', '{keywords}', '{author}','{published_time}');"

            db.init()
            try:
                db.db_execute(insert_query)
            except Exception as e:
                print(f"error during insertion into mayadeen : {e}")
            db.db_close()
        else:
            print("JSON-LD script tag not found.")
    except RequestException as e:
        print(f"An error occurred during the request: {e} at this url : {url}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def extract_mayadeen(url):
    print('start extraction from mayadeen')
    connect_timeout = 100  # seconds
    read_timeout = 500  # seconds

    try:
        response = requests.get(url, timeout=(connect_timeout, read_timeout))
        html_content = response.content
        soup = BeautifulSoup(html_content, "lxml")

        # Extract the article body
        article_body = soup.find("div", class_="p-content")

        article_text = ""
        for paragraph in article_body.find_all('p'):
            article_text += paragraph.get_text()

        print("article" + article_text + "end of article")
        # Find all script tags containing JSON-LD data
        script_tags = soup.find_all("script", type="application/ld+json")

        # Extract data from the first script tag
        if script_tags:
            first_script_tag = script_tags[0]
            json_ld_content = json.loads(first_script_tag.string)
            print(json_ld_content)

            title = soup.find('div', class_="single-blog-wrapper").find('h1').get_text()
            title = title.replace('\'', '"')
            CIE_query = f"select id from bbc_art where title = '{title}';"
            db.init()
            id = db.db_execute(CIE_query)
            if not id is None:
                return
            description = soup.find('div', class_="single-blog-wrapper").find('p', class_='p-summary').get_text()
            keywords = json_ld_content.get("keywords", None)
            author = json_ld_content.get("author", {}).get("name", None)
            published_time = parser.parse(json_ld_content.get("datePublished", None)).date() if json_ld_content.get("datePublished", None) else None
            article_body = article_text



            description = description.replace('\'', '"')
            article_body = article_body.replace('\'', '"')


            insert_query = f"INSERT INTO {'may_art'} (title, description, body, keywords, author, publishedTime) OUTPUT INSERTED.id VALUES ('{title}', '{description}', '{article_body}', '{keywords}', '{author}', '{published_time}');"
            #values = (title, description, article_body, keywords, author, published_time)

            db.init()
            try:
                db.db_execute(insert_query)
            except Exception as e:
                print(f"error during insertion into mayadeen : {e}")
            db.db_close()
        else:
            print("JSON-LD script tag not found.")
    except RequestException as e:
        print(f"An error occurred during the request: {e} at this url : {url}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
