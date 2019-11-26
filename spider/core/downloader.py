import requests


class SVzDownloader:
    def __init__(self, headers=None):
        baseheaders = {
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
        }
        if headers is not None:
            baseheaders.update(headers)
        self.rq = requests.session()
        self.rq.headers.update(baseheaders)

    def get(self, url, params=None, **kwargs):
        if url is None:
            return None
        content = self.rq.get(url, params=params, **kwargs)
        return content.content.decode('utf8')

    def post(self, url, data=None, **kwargs):
        if url is None:
            return None
        content = self.rq.get(url, data=data, **kwargs)
        return content.content.decode('utf8')


if __name__ == '__main__':
    d = SVzDownloader()
    d.get('https://so.gushiwen.org/authors/')
