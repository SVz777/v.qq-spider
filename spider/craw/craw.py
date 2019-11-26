import base64

import pymysql
import requests
from bs4 import BeautifulSoup

from spider.core import *
from spider.core import config

from core import *

rootUrl = 'https://v.qq.com/'


class Parser(SVzParser):

    def parse(self, content, **kwargs) -> (list, list):
        current_url = kwargs['url']
        if URL.is_movie(current_url):
            urls, datas = self._parse_movie(content, **kwargs)
        elif URL.is_list(current_url):
            urls, datas = self._parse_list(content, **kwargs)
        else:
            urls, datas = [], []
        return urls, datas

    def _parse_movie(self, content, **kwargs) -> (list, list):
        urls, datas = [], []
        data = {}
        bs = BeautifulSoup(content, 'html.parser')
        data['code'] = kwargs['url'].split('/')[-1][:-5]
        data['title'] = bs.select_one('h1.video_title').get_text().strip().replace("'","`")
        data['score'] = bs.select_one('span.video_score').get_text().strip()
        play_num = bs.select_one('em#mod_cover_playnum').get_text().strip()
        if play_num.endswith('万'):
            data['playnum'] = int(float(play_num[:-1]) * 1e4)
        elif play_num.endswith('亿'):
            data['playnum'] = int(float(play_num[:-1]) * 1e8)
        else:
            data['playnum'] = int(play_num)
        data['area'], data['year'], *data['tags'] = [i.get_text() for i in bs.select('div.video_tags a')]
        data['tags'] = ','.join(data['tags'])
        data['director'], *data['actors'] = [i.get_text() for i in bs.select('div.director a')]
        data['actors'] = ','.join(data['actors'])
        data['desc'] = bs.select_one('li.mod_summary.intro_item .video_summary .summary').get_text().strip()
        datas.append(data)
        return urls, datas

    def _parse_list(self, content, **kwargs) -> (list, list):
        urls, datas = [], []
        bs = BeautifulSoup(content, 'html.parser')
        list_item = bs.select('.figures_list .list_item')
        for item in list_item:
            a = item.select_one('a')
            url = a['href']
            urls.append(url)
            img_name = a['href'].split('/')[-1][:-5]
            img = a.select_one('img')['r-lazyload']
            img_data = requests.get(f'http:{img}').content
            data = {
                'code': img_name,
                'url': url,
                'img': base64.b64encode(img_data).decode()
            }
            datas.append(data)
        return urls, datas


class Saver(SVzSaver):
    def __init__(self):
        self.db = pymysql.connect(**config.db_server['no1'])
        self.cur = self.db.cursor()

    def save(self, datas, **kwargs):
        current_url = kwargs['url']
        if URL.is_movie(current_url):
            self.save_movie(datas, **kwargs)
        elif URL.is_list(current_url):
            self.save_list(datas, **kwargs)

    def err(self, url, **kwargs):
        logger.error(url,**kwargs)

    def save_movie(self, datas, **kwargs):
        sql = "UPDATE `qq_movie`.`movie` SET `title` = '{title}', `score` = '{score}', `playnum` = {playnum}, `area` = '{area}', `year` = {year}, `tags` = '{tags}', `director` = '{director}', `actors` = '{actors}', `desc` = '{desc}' WHERE `code` = '{code}';"
        for data in datas:
            logger.info(data)
            self.cur.execute(sql.format(**data))
            self.db.commit()

    def save_list(self, datas, **kwargs):
        sql = "INSERT INTO `qq_movie`.`movie`(`code`,`url`, `img`) VALUES ('{code}','{url}','{img}');"
        for data in datas:
            logger.info({
                'code':data['code'],
                'url':data['url']
            })
            self.cur.execute(sql.format(**data))
            self.db.commit()


def init_redis():
    listUrl = 'https://v.qq.com/x/list/movie?sort=19&subtype=%d&offset=%d'
    dl = SVzDownloader()
    um = SVzUrlManager('qq_movie', [])
    um.flushall()
    for i in range(1, 22):
        if i == 20:
            print(listUrl % (i, 1))
            um.add_url(listUrl % (i, 1))
            continue
        url = listUrl % (i, 0)
        content = dl.get(url)
        bs = BeautifulSoup(content, 'html.parser')
        pages = bs.select('._items')[-1]
        num = int(pages.select('a')[-1].get_text())
        for j in range(1, num):
            print(listUrl % (i, j*30))
            um.add_url(listUrl % (i, j*30))


def get_spider():
    # https://v.qq.com/x/list/movie?sort=19&subtype=21&offset=0
    spider = SVzSpider('qq_movie', urls=[], parser=Parser, saver=Saver)
    return spider

if __name__ == '__main__':
    um = SVzUrlManager('qq_movie', [])
    um.flushall()
    with open('list.txt','r') as f:
        l = f.read().split('\n')
        for i in l :
            print(i)
            um.add_url(i)