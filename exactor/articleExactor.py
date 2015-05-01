# encoding: utf-8
from __future__ import division

__author__ = 'p'

import gzip
import StringIO
import sys
import os
import math
from goose import Goose
from goose.text import StopWordsChinese
import mysql.connector
from multiprocessing import pool

connection_config = {'user': 'root',
                     'password': '12345678',
                     'host': '127.0.0.1',
                     'database': 'spyder'}

fetch_sql = 'select * from original_html limit %d,%d'
getcount_sql = 'select count(*) from original_html'
saved_sql = 'insert into blog(title,author,text) VALUES (%s,%s,%s)'


class ArticleExtractor(object):
    def __init__(self):
        self.g = Goose({'stopwords_class': StopWordsChinese})

    def extractUrl(self, url=None):
        if url is not None:
            return self.g.extract(url=url)
        return None

    def extractHtm(self, html=None):
        if html is not None:
            return self.g.extract(raw_html=html)
        return None


def worker(start, count):
    g = ArticleExtractor()
    print('开始连接数据库')
    cnx = mysql.connector.connect(**connection_config)
    read_cursor = cnx.cursor()
    print('连接成功，开始读取数据')
    read_cursor.execute(fetch_sql % (start, count))
    data = read_cursor.fetchall()
    # print('读取数据成功,共%d条数据' % len(data))
    read_cursor.close()
    # python offer a executemany method for optimizing the multi insert statement
    write_cursor = cnx.cursor()
    number = 0
    for x in data:
        try:
            zipdata = StringIO.StringIO(x[1])
            zipper = gzip.GzipFile(fileobj=zipdata, mode='r')
            article = g.extractHtm(zipper.read().decode('utf8'))
            print(u'process-%d:提取No%d:' % (os.getpid(), number) + article.title)

            number += 1
            write_cursor.execute(saved_sql, (article.title, '惟有中华', article.cleaned_text))
            cnx.commit()
        except Exception, e:
            print(e)
            break
            # del insert_data[:]
            # dataLen = 0
    print('提取完毕。')
    write_cursor.close()
    cnx.close()


if __name__ == '__main__':
    ccnx = mysql.connector.connect(**connection_config)
    acursor = ccnx.cursor()
    acursor.execute(getcount_sql)
    itemCount = acursor.fetchone()[0]
    taskNum = int(math.ceil(itemCount / 50))
    procesPool = pool.Pool()

    for i in range(0, taskNum):
        procesPool.apply_async(worker, args=(i*50, 50))
    procesPool.close()
    procesPool.join()
    print('处理结束')