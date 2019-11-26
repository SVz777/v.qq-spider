import re

from .downloader import SVzDownloader
from .parser import SVzParser
from .saver import SVzSaver
from .urlManager import SVzUrlManager


class SVzSpider():

    def __init__(self, name, urls, *, urlManager=SVzUrlManager, downloader=SVzDownloader, parser=SVzParser, saver=SVzSaver):
        self.name = name
        self.urlManager = urlManager(name, urls)
        self.downloader = downloader()
        self.parser = parser()
        self.saver = saver()

    def craw(self):
        while self.urlManager.has_url():
            try:
                url = self.urlManager.get_url()
                print(f"{self.name} crawing {url}")
                content = self.downloader.get(url)
                urls, datas = self.parser.parse(content, url=url, dl=self.downloader)
                self.urlManager.add_urls(urls)
                self.saver.save(datas, url=url)
            except Exception as e:
                self.saver.err(url+e)
