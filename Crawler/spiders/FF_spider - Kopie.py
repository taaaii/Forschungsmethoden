from Scripte.settings import Settings

import scrapy
from scrapy.crawler import CrawlerProcess
from pathlib import Path

my_settings = Settings()

class MovieCrawler(scrapy.Spider):
    """
    Crawler for the movie_ff
    """

    name = "FF_crawler"
    custom_settings = {"DOWNLOAD_DELAY": 0.5}
    topic = "unspecified"

    def start_requests(self):
        urls = my_settings.movielist.get(MovieCrawler.topic)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, cb_kwargs={"topic": MovieCrawler.topic})

    def parse(self, response, **kwargs):

        ftitle = response.url.split("/")[-1]
        chapter = response.url.split("/")[-2]
        filename = f"{chapter}.html"

        path = Path(fr'G:/Uni/Forschungsmethoden/htmldata/movies/{kwargs.get("topic")}/{ftitle}')
        path.mkdir(parents=True, exist_ok=True)
        with open(path / filename, 'w') as f:
            f.write(response.body.decode("utf-8", "strict"))

        self.log(f'Saved file {filename} to {path}')

        next_page = \
            response.xpath('//*[@id="ffcbox-story-layer-SL"]/div/div[1]/div[2]/div[2]/div[2]/div[1]/form//@href')[
                -1].extract()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse, cb_kwargs={"topic": MovieCrawler.topic})

class BookCrawler(scrapy.Spider):
    name = "BookCrawler"
    custom_settings = {"DOWNLOAD_DELAY": 0.5}
    topic = "unspecified"

    def start_requests(self):
        urls = my_settings.booklist.get(BookCrawler.topic)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_books, cb_kwargs={"topic": BookCrawler.topic})

    def parse_books(self, response, **kwargs):
        ftitle = response.url.split("/")[-1]
        chapter = response.url.split("/")[-2]
        filename = f"{chapter}.html"
        path = Path(fr'G:/Uni/Forschungsmethoden/htmldata/books/{kwargs.get("topic")}/{ftitle}')
        path.mkdir(parents=True, exist_ok=True)
        with open(path / filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
        next_page = \
            response.xpath('//*[@id="ffcbox-story-layer-SL"]/div/div[1]/div[2]/div[2]/div[2]/div[1]/form//@href')[
                -1].extract()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse_books, cb_kwargs={"topic": BookCrawler.topic})

class GameCrawler(scrapy.Spider):
    name = "GameCrawler"
    custom_settings = {"DOWNLOAD_DELAY": 0.5}
    topic = "unspecified"

    def start_requests(self):
        urls = my_settings.gamelist.get(GameCrawler.topic)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_books, cb_kwargs={"topic": GameCrawler.topic})

    def parse_books(self, response, **kwargs):
        ftitle = response.url.split("/")[-1]
        chapter = response.url.split("/")[-2]
        filename = f"{chapter}.html"
        path = Path(fr'G:/Uni/Forschungsmethoden/htmldata/games/{kwargs.get("topic")}/{ftitle}')
        path.mkdir(parents=True, exist_ok=True)
        with open(path / filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
        next_page = \
            response.xpath('//*[@id="ffcbox-story-layer-SL"]/div/div[1]/div[2]/div[2]/div[2]/div[1]/form//@href')[
                -1].extract()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse_books, cb_kwargs={"topic": GameCrawler.topic})

process = CrawlerProcess()
GameCrawler.topic = "Detroit"
process.crawl(GameCrawler)
process.start()
