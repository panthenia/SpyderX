__author__ = 'p'
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
import re
import gzip


class Book(object):
    def __init__(self, name, url):
        """
        :type name: str
        :type url: str
        """
        self.name = name
        self.url = url
    def print(self):
        print('书籍名称：'+self.name+',url:'+self.url)


mlook_request_header = {'Host': 'www.mlook.mobi',
                        'Connection': 'keep-alive',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36',
                        'Accept-Encoding': 'gzip',
                        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
                        'Cookie': 'a=47caVQVf0Ypw8GbupR1Id%252B6rEFy8uEEo1Is9USev4UKezkoDuP%252FEMaJ%252BwK9hVxOfNXzF1MSH3zDGoXK2wjR35bNBMV4gyR0fvaJdwW23qQBPqw; username=myjsy; category=all'}


def parseBookInfo(html):
    books = []
    print(html)
    soup = BeautifulSoup(html, 'html5lib')
    booksContainerDiv = soup.find('div', class_='books')

    booksDivs = booksContainerDiv.find_all('div', class_='book clearfix')

    if len(booksDivs) != 0:
        for abook in booksDivs:
            print(abook.find('a', href=re.compile("^/book/info/")))
            book = Book(abook.text, abook['href'])
            book.print()
            books.append(book)
    else:
        print('未找到这本书')


def searchBook(bookName):
    url = 'https://www.mlook.mobi/search?' + urllib.parse.urlencode({'q': bookName})
    requestTarget = urllib.request.Request(url=url,
                                           headers=mlook_request_header, method='GET')
    response = urllib.request.urlopen(requestTarget)
    html = gzip.decompress(response.read()).decode()
    books = parseBookInfo(html)


if __name__ == '__main__':
    searchBook('天龙八部')