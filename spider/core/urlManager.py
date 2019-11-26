from urllib.parse import urljoin

from redis import Redis

from . import config


class SVzUrlManager:
    def __init__(self, name, urls, **kwargs):
        self.redis = Redis(**config.redis_server['no1'], decode_responses=True)
        self.newUrls = name + '_new'
        self.oldUrls = name + '_old'
        self.add_urls(urls)

    def has_url(self):
        num = self.redis.scard(self.newUrls)
        return num if num else False

    def get_url(self):
        url = self.redis.spop(self.newUrls)
        self.redis.sadd(self.oldUrls, url)
        return url

    def add_url(self, url):
        if self.redis.sismember(self.newUrls, url) or self.redis.sismember(self.oldUrls, url):
            return 0
        self.redis.sadd(self.newUrls, url)
        return 1

    def add_urls(self, urls):
        if urls is None:
            return
        count = 0
        for url in urls:
            count += self.add_url(url)
        return count

    def flushall(self):
        self.redis.flushall()
