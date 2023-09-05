import re
import json

from bs4 import BeautifulSoup
from pathlib import Path
from tqdm import tqdm

from Scripte.settings import Settings


class Scrape_Novel():
    def __init__(self, path: Path):
        self.path = path
        self.chapter_html = [x for x in path.glob('**/*') if x.is_file() if x.suffix == ".html"]
        with open(self.chapter_html[0], "r", encoding="utf-8") as f:
            text = f.read()

        self.soup = BeautifulSoup(text, features="lxml")
        self.chapters = [Scrape_Chapter(x) for x in self.chapter_html]
        self.metadata = {"tags": [x.text for x in self.soup.select_one(
            '#ffcbox-story-layer-SL > div > div > div.grid-33.splitview-left > div > div > div:nth-child(6)').find_all(
            "span")],
                         "chapcount": self.soup.select_one(
                             '#ffcbox-story-layer-SL > div > div > div.grid-33.splitview-left > div > div > div:nth-child(8) > div:nth-child(2) > span.semibold').text,
                         "wordcount": self.soup.select_one(
                             '#ffcbox-story-layer-SL > div > div > div.grid-33.splitview-left > div > div > div:nth-child(8) > div:nth-child(3) > span.semibold').text,
                         "chapters": {key: value for (key, value) in
                                      [(x.get_chapternumber(), x.get_data()) for x in self.chapters]},
                         "title": self.soup.select_one(
                             '#ffcbox-story-layer-SL > div > div > div.grid-33.splitview-left > div > div > h4').text,
                         "topic": self.path.parents[0].name,
                         "release": self.soup.select_one(
                             "#ffcbox-story-layer-SL > div > div > div.grid-33.splitview-left > div > div > div:nth-child(7) > div:nth-child(1)").text,
                         "author": self.soup.select_one(
                             "#ffcbox-story-layer-SL > div > div > div.grid-33.splitview-left > div > div > div:nth-child(3) > a").text,
                         }

        # self.set_dates()

    def set_dates(self):
        self.metadata["release"], self.metadata["update"] = [x.text.strip() for x in self.soup.select_one(
            '#ffcbox-story-layer-SL > div > div > div.grid-33.splitview-left > div > div > div:nth-child(7)').find_all(
            "div")]

    def tojson(self):
        outpath = Path(settings.jsondatadirectory) / self.path.parents[1].name / self.path.parents[0].name
        outpath.mkdir(parents=True, exist_ok=True)
        with open(outpath / f"{self.path.name}.json", "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=4)


class Scrape_Chapter:
    def __init__(self, path: Path):
        with open(path, "rb") as f:
            text = f.read()
            text = text.decode("utf-8", "strict")
        self.soup = BeautifulSoup(text, features="lxml")
        self.text = self.soup.select_one("#storytext > div > div > div").text.strip()
        self.text = re.sub(r"(\w+[.,])(\w+)", "\1 \2", self.text)
        self.text = re.sub(r"\s+", " ", self.text)
        self.metadata = {"text": self.text,
                         "wordcount": self.soup.select_one(
                             '#ffcbox-story-layer-SL > div > div > div.grid-66.splitview-right > div.story-right > div:nth-child(2) > div.chapterinfo.centered.small-font.table > span:nth-child(2)').text,
                         "chapter_release": self.soup.select_one(
                             '#ffcbox-story-layer-SL > div > div > div.grid-66.splitview-right > div.story-right > div:nth-child(2) > div.chapterinfo.centered.small-font.table > span:nth-child(1)').text,
                         "chapter_number": path.stem,
                         }

    def get_data(self):
        return self.metadata

    def get_chapternumber(self):
        return self.metadata["chapter_number"]


settings = Settings()
for rubrik in settings.htmldatadirectory.iterdir():
    if rubrik.is_dir():
        for topic in rubrik.iterdir():
            for novel in tqdm(direct := topic.iterdir(), desc=f"Krimiiteration for {topic.stem}"):
                if novel.is_dir():
                    try:
                        print(f"Scraping {topic}{novel.absolute()}")
                        FF_object = Scrape_Novel(novel.absolute())
                        FF_object.tojson()
                    except:
                        print(f"Error in {novel.absolute()}")
                        continue
