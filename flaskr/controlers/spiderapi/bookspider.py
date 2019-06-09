
from multiprocessing.pool import Pool
from urllib.parse import quote, urlparse, urlsplit

import requests
from pyquery import PyQuery as pq

from flaskr.common.utils import get_spider_db

from .base import BaseSpider


class BookSpider(BaseSpider):
    def __init__(self, core):
        super().__init__(core)

    def find_all(self):
        sorts = [23, 25, 26, 27, 28, 29, 55]
        results = []
        try:
            pool = Pool()
            pool.map(self._handle_by_threading, sorts)
            pool.close()
            pool.join()
        except Exception as e:
            raise e

        return results

    def find(self, *args):
        keyword = args[0]
        url = 'http://www.zxcs.me/index.php?keyword=%s' % quote(keyword)

        youshu_url = 'http://www.yousuu.com/search/%s?type=all' % quote(
            keyword)
        results = []
        try:
            resp = requests.get(url, headers=self.headers)
            doc = pq(resp.text)
            results = self._analysis_zhixuan(doc)

            # resp2 = requests.get(youshu_url, headers=self.headers)
            # doc2 = pq(resp2.text)
            # extend_infos = self.analysis_youshu(doc2)

            # for outer in results:
            #     for inner in extend_infos:
            #         if outer.get('bookname') == inner.get('bookname'):
            #             outer['score'] = inner['score']
            #             break

        except Exception as e:
            raise e

        return results
    
    def find_other_info(self, keyword):
        youshu_url = 'http://www.yousuu.com/search/%s?type=all' % quote(keyword)
        try:
            resp = requests.get(youshu_url, headers=self.headers)
            
            doc = pq(resp.text)
            extend_infos = self._analysis_youshu(doc)
            if len(list(extend_infos))> 0:
                print('%s 数据库操作' % youshu_url)
                self._operate_db(extend_infos) 
        except Exception as e:
            print(e)

    def _handle_by_threading(self, sort):
        maxpages = 15
        url = 'http://www.zxcs.me/sort/%s/page/%s'
        flg = False
        idx = 1
        results = []
        while not flg and idx != 100:
            real_url = url % (sort, idx)

            resp = requests.get(real_url, headers=self.headers)
            doc = pq(resp.text)

            dl_tags = doc.find('dl[id=plist]')
            size = len(list(dl_tags.items()))

            if size < maxpages:
                flg = True

            print('%s 爬取到%s本小说' % (real_url, size))
            results.extend(self._analysis_zhixuan(doc))

            idx += 1
        
        if len(results) > 0:
            print('%s 数据库操作' % real_url)
            self._operate_db(results) 

    def _analysis_youshu(self, doc):
        d_list = doc.find('div.bd.booklist-subject')

        results = []
        for div_tag in d_list.items():
            bookname = div_tag.find('div.title a').text()
            img_url = div_tag.find('div.post a img').attr('src')
            abstract = div_tag.find('div.abstract').text().split()

            yield {
                'bookname': bookname,
                'img_url2': img_url,
                'numOfCharacters': abstract[3],
                'lastUpdateDate': abstract[5],
                'score': abstract[7]
            }

    def _analysis_zhixuan(self, doc):
        results = []
        detail_url = 'http://www.zxcs.me/post/%s'
        down_url = 'http://www.zxcs.me/download.php?id=%s'
        dl_tags = doc.find('dl[id=plist]')

        for dl_tag in dl_tags.items():
            # 书籍一览页面
            full_text = dl_tag.find('dt a').text()
            url = dl_tag.find('dt a').attr('href')
            uid = url.split('/')[-1]
            # 书籍详细页面
            resp = requests.get(detail_url % uid, headers=self.headers)
            doc = pq(resp.text)
            content = doc.find('div#content')
            booktype = content.find('p.date a').eq(2).text()
            img_url = content.find('a[id^="ematt"]').attr('href')

            resp = requests.get(down_url % uid, headers=self.headers)
            doc = pq(resp.text)
            file_url = doc.find('span.downfile').eq(
                0).find('a').attr('href')
            fragments = full_text[1:].split('》', 1)
            yield {
                'bookname': fragments[0],
                'author': fragments[1].split('：')[1],
                'booktype': booktype,
                'img_url': img_url,
                'full_text': full_text,
                'download_url': file_url
            }
    
    def _operate_db(self, results):
        db = get_spider_db()
        colection = db.books

        for rec in results:
            conditon = {'bookname': rec.get('bookname')}
            r = colection.find_one(conditon)
            if not r:
                colection.insert_one(rec)
            else:
                colection.update_one(conditon, {'$set': rec})
