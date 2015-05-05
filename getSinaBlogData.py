__author__ = 'p'

import urllib.request
import gzip
import mysql.connector
import os
import sinaBlogHtmlParser

request_header = {'Host': 'blog.sina.com.cn',
                  'Connection': 'keep-alive',
                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36',
                  'Referer': 'http://blog.sina.com.cn/weiyouzhonghua',
                  'Accept-Encoding': 'gzip',
                  'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
                  'Cookie': '_s_loginuid=1217096645; blogAppAd_blog7article=1; blogAppAd_blog7articlelist=1; U_TRS1=0000001f.c0901528.5472fb84.7220d9b6; vjuids=-1eb324895.149e1268d26.0.f2da2c71; SGUID=1416968334801_38174158; UOR=www.google.com,finance.sina.com.cn,; SINAGLOBAL=114.255.40.30_1425343434.927168; U_TRS2=0000001e.98863b34.55233ae1.b4bd7209; SessionID=ipp3bvlm8v8spe2sk49u87kb20; _s_loginStatus=1217096645; SUB=_2AkMif_2ddcNhrAJTmf8VxW3kaIhH-jjGiefBAH-8JV5WHRjCEQETNOdf5Z_mqFkljOj3-jYJ-Q..; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WWk9BVHp4hjTwDO5xCD9jX3; Apache=114.255.40.30_1428391469.820717; ULV=1428456416843:3:1:1:114.255.40.30_1428391469.820717:1427514537363; _s_loginuid=1217096645; BLOG_TITLE=%E6%83%9F%E6%9C%89%E4%B8%AD%E5%8D%8E; lxlrtst=1428472513_o; ULOGIN_IMG=gz-935f4edd15b7cf26ef4220d4348f21f0138d; lxlrttp=1428472513; blogAppAd_blog7index=1; vjlast=1428456417.1428456418.10'}


def decodeResponseData(response):
    decodeType = response.getheader('Content-Encoding')
    if decodeType == 'gzip':
        return gzip.decompress(response.read()).decode()

#define
def requestUrl(url):
    requestTarget = urllib.request.Request(url=url,
                                           headers=request_header, method='GET')
    response = urllib.request.urlopen(requestTarget)
    return response.read()


bData = requestUrl('http://blog.sina.com.cn/weiyouzhonghua')
htmlData = gzip.decompress(bData).decode()
listUrl = sinaBlogHtmlParser.getBlogListUrl(htmlData)
connection_config = {'user': 'root',
                     'password': '12345678',
                     'host': '127.0.0.1',
                     'database': 'spyder'}
save_sql = "insert into original_html(html) VALUES (%s)"
if listUrl is not None:
    data = requestUrl(listUrl)
    blogListPage1Html = gzip.decompress(data).decode()

    # 通过博客文章列表1获获取其他列表页的url
    blogListPageUrls = sinaBlogHtmlParser.getBlogListPageUrl(blogListPage1Html, listUrl)
    allBlogUrls = [sinaBlogHtmlParser.getBlogsUrl(blogListPage1Html)]
    if allBlogUrls is not None:
        for x in blogListPageUrls:
            td = requestUrl(x)
            lph = gzip.decompress(td).decode()
            allBlogUrls.append(sinaBlogHtmlParser.getBlogsUrl(lph))

    print('共有%d页博客。' % len(allBlogUrls))
    for x in allBlogUrls:
        print(x)
    cnx = mysql.connector.connect(**connection_config)
    cursor = cnx.cursor()
    for alist in allBlogUrls:
        blogsData = []
        for k in alist:
            print('抓取:%s' % k)
            raw_html = requestUrl(k)
            blogsData.append((raw_html,))
        if len(blogsData) > 0:
            cursor.executemany(save_sql, blogsData)
            cnx.commit()
    print('抓取完毕')
    cursor.close()
    cnx.close()
    # os.system('py exactor/articleExactor.py')
    # 占位符两边不需要加单引号，简直被搞死了
    # 读取二进制文件：file_like=cStringIO.StringIO(data[0][0])
