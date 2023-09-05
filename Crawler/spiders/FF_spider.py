from Scripte.settings import Settings

import scrapy
from scrapy.crawler import CrawlerProcess
from pathlib import Path
from Scripte.linkfinder import link_collect
import requests

my_settings = Settings()


class HTMLCrawler(scrapy.Spider):
    """
    Crawler for the movie_ff
    """

    name = "FF_crawler"
    custom_settings = {"DOWNLOAD_DELAY": 1.0}
    topic = "unspecified"

    def start_requests(self):
        urls = my_settings.linklist.get(HTMLCrawler.topic)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, cb_kwargs={"topic": HTMLCrawler.topic})

    def parse(self, response, **kwargs):

        ftitle = response.url.split("/")[-1]
        chapter = response.url.split("/")[-2]
        filename = f"{chapter}.html"

        path = Path(fr'F:/Programming/Data/Forschungsmethoden/htmldata/{my_settings.current_topic}/{ftitle}')
        path.mkdir(parents=True, exist_ok=True)
        with open(path / filename, 'wb') as f:
            f.write(response.body)

        self.log(f'Saved file {filename} to {path}')
        next_page = \
            response.xpath('//*[@id="ffcbox-story-layer-SL"]/div/div[1]/div[2]/div[2]/div[2]/div[1]/form//@href')[
                -1].extract()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse, cb_kwargs={"topic": HTMLCrawler.topic})


class Linksearcher(scrapy.Spider):
    name = "Finder"
    custom_settings = {'DOWNLOAD_DELAY': 0.5}
    topic = "unspecified"

    def start_requests(self):
        urls = my_settings.start
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, cb_kwargs={"topic": Linksearcher.topic, "_counter": 1})

    def parse(self, response, **kwargs):

        link_collect(response.body)
        counter = kwargs.get('_counter') + 1
        next_page = f'https://www.fanfiktion.de/{my_settings.rubrikenstart.get(Linksearcher.topic)}{counter}/updatedate'
        if requests.get(next_page).status_code < 400:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse,
                                 cb_kwargs={"topic": Linksearcher.topic, "_counter": counter})


process = CrawlerProcess()
# change to proper Spider and change in Setting.py to use
Linksearcher.topic = my_settings.current_topic
HTMLCrawler.topic = my_settings.current_topic
if my_settings.mode == "linksearch":
    process.crawl(Linksearcher)
elif my_settings.mode == "htmlcrawl":
    process.crawl(HTMLCrawler)
process.start()
