import io
import json
import sys
import time
import urllib.request

import requests
from bs4 import BeautifulSoup
from bson import ObjectId
from pymongo import MongoClient
from requests.exceptions import RequestException
from PIL import Image
from Sitemap import Sitemap
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

client = MongoClient("mongodb://localhost:27017")
db = client["news"]
collection = db["articles"]


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
                        obj.extract_mayadeen(url=loc_element.get_text())

            else:
                print(f"Failed to fetch sitemap: {sitemap_url}")
        print(f'returned loc : {locs}')
        return locs

    def extract_mayadeen(self, url):
        print('start extraction from mayadeen')
        connect_timeout = 100  # seconds
        read_timeout = 500  # seconds

        try:
            response = requests.get(url, timeout=(connect_timeout, read_timeout))
            html_content = response.content
            soup = BeautifulSoup(html_content, "lxml")

            # Extract the article body
            article_body = soup.find("div", class_="article-content-wrap")

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
                if not typee == "Article":
                    return

                data = {
                    "site": json_ld_content.get("publisher", {}).get("url", None),
                    "url": json_ld_content.get("url", None),
                    "title": json_ld_content.get("headline", None),
                    "description": json_ld_content.get("description", None),
                    'keywords': json_ld_content.get("keywords", None),
                    'author': json_ld_content.get("author", {}).get("name", None),
                    'published_time': json_ld_content.get("datePublished", None),
                    'modified_time': json_ld_content.get("dateModified", None),
                    'article_section': json_ld_content.get("articleSection", None),
                    'word_count': json_ld_content.get("wordCount", None),
                    'language': json_ld_content.get("inLanguage", None),
                    'date_created': json_ld_content.get("dateCreated", None),
                    'article_body': article_text
                }

                image_id = collection.insert_one(data).inserted_id
                image_str = str(image_id)

                response = requests.get(json_ld_content.get("thumbnailUrl", None))
                if response.status_code == 200:
                    with open(r"templates/"+image_str+".jpeg", "wb") as file:
                        file.write(response.content)

                print(f'inserted: {data}')
            else:
                print("JSON-LD script tag not found.")
        except RequestException as e:
            print(f"An error occurred during the request: {e} at this url : {url}")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")


def main():
    sitemap_extractor = Sitemap()
    data = DataExtractor()
    sitemap_url = 'https://www.almayadeen.net/sitemaps/all.xml'
    sitemaps = sitemap_extractor.process_sitemap(sitemap_url)
    article_urls = data.extract_locs_from_sitemap(xml_sitemaps=sitemaps)
    print('finished and now extracting')

    client.close()


if __name__ == '__main__':
    main()
