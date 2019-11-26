from enum import Enum


class URL(Enum):
    MOVIE = 0,
    LIST = 1

    @classmethod
    def classify(cls, url):
        if 'cover' in url:
            return URL.MOVIE
        else:
            return URL.LIST

    @classmethod
    def is_movie(cls,url):
        return cls.classify(url) == cls.MOVIE

    @classmethod
    def is_list(cls,url):
        return cls.classify(url) == cls.LIST


