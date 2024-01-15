import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from flask import json
from requests.exceptions import RequestException
from Compare import Compare
from Search import Search
from Sitemap import Sitemap
from DatabaseConnection import Database

db = Database()


class DataExtractor:

    def extract_locs_from_sitemap(self, xml_sitemaps):
        locs = []

        obj = DataExtractor()

        for sitemap_url in xml_sitemaps:
            response = requests.get(sitemap_url)

            if response.status_code == 200:
                xml_content = response.text
                soup = BeautifulSoup(xml_content, "xml")
                url_elements = soup.find_all("url")
                for url_element in url_elements:
                    loc_element = url_element.find("loc")
                    if loc_element:
                        locs.append(loc_element.get_text())
                        print(f'{loc_element.get_text()} grabbed')

                        if "aljazeera.com" in loc_element.get_text():
                            if obj.extract_aljazeera(url=loc_element.get_text()) == "stop":
                                break
            else:
                print(f"Failed to fetch sitemap: {xml_sitemaps}")

        print(f'returned loc : {locs}')
        return locs

    def extract_aljazeera(self, url):
        print('start extraction from aljazeera')
        connect_timeout = 100  # seconds
        read_timeout = 500  # seconds
        search = Search()
        try:
            response = requests.get(url, timeout=(connect_timeout, read_timeout))
            html_content = response.content
            soup = BeautifulSoup(html_content, "lxml")

            # Extract the article body  wysiwyg wysiwyg--all-content css-1vkfgk0
            article_body = soup.find("div", class_="wysiwyg wysiwyg--all-content css-ibbk12")

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
                typee = json_ld_content.get("@type", None)
                if not typee == "NewsArticle":
                    return

                title = json_ld_content.get("headline", None)
                CIE_query = f"select id from jaz_art where title = '{title}';"
                db.init()
                id = db.db_execute(CIE_query)
                if not id is None:
                    return
                db.db_close()
                description = json_ld_content.get("description", None)
                keywords = soup.find('meta', {'name': 'keywords'}).get('content')
                author = json_ld_content.get("author", {}).get("name", None)
                published_time = datetime.strptime(json_ld_content.get("datePublished", None),
                                                   '%Y-%m-%dT%H:%M:%SZ').date() if json_ld_content.get("datePublished",
                                                                                                       None) else None
                article_body = article_text
                image_url = json_ld_content.get('image', [{}])[0].get('url', None)

                search.search_may(keywords)
                search.search_BBC(keywords)

                compare = Compare()
                may_id, bbc_id = compare.initCompare(title, article_body, description, published_time)
                if not may_id and bbc_id:
                    return
                if bbc_id is None:
                    bbc_id = 99
                if may_id is None:
                    may_id = 99
                insert_query = f"INSERT INTO {'jaz_art'} (title, description, body, keywords, author,publishedTime,image_url, id_may, id_bbc) VALUES ('{title}', '{description}', '{article_body}', '{keywords}', '{author}', '{published_time}','{image_url}',{may_id}, {bbc_id});"

                db.init()
                db.db_execute(insert_query)
                db.db_close()

            else:
                print("JSON-LD script tag not found.")
        except RequestException as e:
            print(f"An error occurred during the request: {e} at this url : {url}")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    @staticmethod
    def start():
        sitemap_extractor = Sitemap()
        data = DataExtractor()
        sitemaps_aljazera = sitemap_extractor.process_sitemap("https://www.aljazeera.com/sitemap.xml")

        data.extract_locs_from_sitemap(sitemaps_aljazera)

        print('finished and now extracting')
