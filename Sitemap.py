import urllib.request
import urllib.error
from bs4 import BeautifulSoup


class Sitemap:
    def get_sitemap(self, url):
        """Scrapes an XML sitemap from the provided URL and returns XML source.
        Args:
            url (string): Fully qualified URL pointing to XML sitemap.
        Returns:
            xml (string): XML source of scraped sitemap.
        """
        headers = {
            'User-Agent': 'Your User-Agent String',  # Replace with your actual User-Agent
        }
        req = urllib.request.Request(url, headers=headers)

        try:
            response = urllib.request.urlopen(req)
            xml = BeautifulSoup(response,
                                'lxml-xml',
                                from_encoding=response.info().get_param('charset'))
            return xml
        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason}")
            return None
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason} for URL: {url}")
            return None
        except Exception as e:
            print(f"An error occurred while saving data to JSON: {e}")

    def get_sitemap_type(self, xml):
        """Parse XML source and returns the type of sitemap.
        Args:
            xml (string): Source code of XML sitemap.
        Returns:
            sitemap_type (string): Type of sitemap (sitemap, sitemapindex, or None).
        """
        sitemapindex = xml.find_all('sitemapindex')
        sitemap = xml.find_all('urlset')

        if sitemapindex:
            return 'sitemapindex'
        elif sitemap:
            return 'urlset'
        else:
            return

    def get_child_sitemaps(self, xml):
        """Return a list of child sitemaps present in a XML sitemap file.

        Args:
            xml (string): XML source of sitemap.

        Returns:
            sitemaps (list): Python list of XML sitemap URLs.
        """

        sitemaps = xml.find_all("sitemap")

        output = []

        for sitemap in sitemaps:
            # loc = sitemap.findNext("loc").text
            output.append(sitemap.findNext("loc").text)

        return output

    def process_sitemap(self, url):
        sitemap = self.get_sitemap(url)
        sitemap_type = self.get_sitemap_type(sitemap)

        if sitemap_type == 'sitemapindex':
            sitemaps = self.get_child_sitemaps(sitemap)
        else:
            sitemaps = [sitemap]

        return sitemaps
