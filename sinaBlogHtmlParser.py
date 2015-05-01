import re

__author__ = 'p'
from bs4 import BeautifulSoup


class Blog(object):
    def __init__(self, title=None, url=None, text=None):
        self._title = title
        self._url = url
        self._text = text

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, newTitle):
        if isinstance(newTitle, str):
            self._title = newTitle
        else:
            raise ValueError('需要str类型')

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, newUrl):
        if isinstance(newUrl, str):
            self._url = newUrl
        else:
            raise ValueError('需要str类型')

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text


def getBlogListUrl(html):
    soup = BeautifulSoup(html, 'html5lib')
    navList = soup.find('div', class_='blognavInfo')
    if navList is not None:
        blogListLink = navList.find(name='a', text='博文目录', href=re.compile("^http://blog.sina.com.cn/s/articlelist_"))
        return blogListLink['href']
    else:
        return None


def getBlogText(html):
    result = []
    soup = BeautifulSoup(html, 'html5lib')
    # 模版一
    contentDiv = soup.find('div', id="sina_keyword_ad_area2", class_='articalContent   newfont_family')
    if contentDiv is None:
        pass

    allSpan = contentDiv.find_all('span')
    for x in allSpan:
        if x.find('span') is not None:
            continue
        else:
            t = x.text.replace('\xa0', '').replace('\n', '').replace(' ', '')
            result.append(t)
    return result


def getBlogListPageUrl(html, temurl):
    urls = []
    soup = BeautifulSoup(html, 'html5lib')
    ul = soup.find('ul', class_='SG_pages')
    #print(ul)
    numSapn = ul.find('span', style="color:#888888;")
    pageNum = int(numSapn.text[1:-1])
    lastSplash = temurl.rfind('_')
    urlPrefix = temurl[0:lastSplash+1] + '{}.html'
    #print("prefix=%s", urlPrefix)
    for x in range(2, pageNum+1):
        realUrl = str.format(urlPrefix, x)
        #print(realUrl)
        urls.append(realUrl)
    return urls

def getBlogsUrl(html):
    soup = BeautifulSoup(html, 'html5lib')
    blogSpans = soup.find_all('span', class_='atc_title')
    result = []
    for item in blogSpans:
        link = item.find('a', href=re.compile("^http://blog.sina.com.cn/s/"))
        result.append(link['href'])
    return result