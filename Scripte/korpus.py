import json

from Scripte.settings import Settings
from pathlib import Path
from collections import Counter
import os
import re

class Korpus:
    """TODO: iterable for corpus"""
    def __init__(self, path):
        self.settings = Settings()
        self.corpusfiles = [x for x in path.glob("**/*") if x.is_file() if
                            x.suffix == ".json"]

        self.corpusdata = {"krimis": {"M": [], "W": [],},}

        for file in self.corpusfiles:
            rubrik, topic = file.parents[1].stem, file.parent.stem
            self.corpusdata[rubrik][topic].append(Novel(file))

        self.novels = flatten_list(flatten_dict(self.corpusdata))
        self.typeset = set()

        self.own_vector = Counter()

        for novel in self.get_novels():
            self.typeset.update(novel.get_typeset())
            self.own_vector += Counter(novel.get_counter())

    def get_novels(self) -> list:
        return self.novels

    def get_tokens(self) -> Counter:
        return sum([x.get_tokens() for x in self.get_novels()])

    def get_set(self):
        return self.typeset

    def get_own_vector(self):
        return self.own_vector


    def __iter__(self):
        from itertools import chain
        return chain(self.get_novels())

    @classmethod
    def single_topic(cls, rubrik: str, topic = None):
        """:returns a subcorpus given the right input to work on
        alternative classmethod used for construction."""
        if topic:
            return cls(Path(settings.jsondatadirectory / f"{rubrik}/{topic}"))
        else:
            return cls(Path(settings.jsondatadirectory / rubrik))

def flatten_dict(dictionary):
    values = []
    for k, v in dictionary.items():
        if isinstance(v, dict):
            values.append(flatten_dict(v))
        else:
            values.append(v)
    return values

def _prepare_text(text:str) -> str:
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    text = re.sub(r"\W+", " ", text)
    return text


def flatten_list(x: list) -> list:
    """short function that takes nested lists and recursively flattens them.
    Not using this on nested lists will throw AssertionErrors"""
    assert isinstance(x[0], list)
    flattened = [item for sublist in x for item in sublist]
    if isinstance(flattened[0], list):
        return flatten_list(flattened)
    else:
        return flattened


class Novel:
    """represents a work of Fanfiction, incorporating all metadata and easily giving access to it"""

    def __init__(self, path):
        with path.open(encoding="utf-8") as f:
            self.json_data = json.load(f)
        self.textdir = [Chapter(x) for x in self.json_data["chapters"].values()]

        self.tags = self.json_data["tags"]
        self.own_vector = Counter()
        self.typeset = set()

        for chapter in self:
            text = _prepare_text(chapter.text)
            x = text.split()
            self.typeset.update(x)
            self.own_vector += Counter(x)

    def get_typeset(self):
        return self.typeset

    def get_counter(self) -> Counter :
        return self.own_vector

    def get_name(self) -> str:
        return self.json_data["title"]

    def get_chapcount(self) -> int:
        return int(self.json_data["chapcount"])

    def __iter__(self):
        from itertools import chain
        return chain(self.textdir)

    def __str__(self):
        return f"""{self.get_name()} :\tchapters : {self.get_chapcount()}\ttokens : {self.json_data["wordcount"]}"""

    def __repr__(self):
        return self.__str__()

class Chapter:
    def __init__(self, sth):
        self.text = sth["text"]
        self.wordcount = sth["wordcount"]
        self.date = sth["chapter_release"]
        self.number = sth["chapter_number"]


settings = Settings()

#test = Korpus(settings.jsondatadirectory)