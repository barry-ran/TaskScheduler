import urllib.request
from bs4 import BeautifulSoup
import os


def Download(url, picAlt, name):
    path = 'D:\\tupian\\' + picAlt + '\\'
    # 判断系统是否存在该路径，不存在则创建
    if not os.path.exists(path):
        os.makedirs(path)
    # 下载图片并保存在本地
    urllib.request.urlretrieve(url, '{0}{1}.jpg'.format(path, name))

#定义请求头
header = {
    "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive'
}

#网页分析
def run(targetUrl, beginNUM, endNUM):
    #创建网络请求对象
    req = urllib.request.Request(url=targetUrl, headers=header)
    response = urllib.request.urlopen(req)  # 这里的req可看成一种更为高级的URL
    #设置请求参数
    html = response.read().decode('gb2312', 'ignore')  # 解码 得到这个网页的html源代码：这个网站的编码使用的是GB2312格式，更常见的网站编码格式应该是UTF-8了吧
    soup = BeautifulSoup(html, 'html.parser')  # 将得到的HTML代码使用python自带的解析器（也可以使用lxml解析器，性能会更好，本代码从简
    # 获取图片div
    Divs = soup.find_all('div', attrs={'id': 'big-pic'})
    #当前页
    nowpage = soup.find('span', attrs={'class': 'nowpage'}).get_text()
    #所有页
    totalpage = soup.find('span', attrs={'class': 'totalpage'}).get_text()
    if beginNUM == endNUM:  # 跳出条件
        return
    for div in Divs:
        beginNUM = beginNUM + 1
        #判断是否存在图片
        if div.find("a") is None:  # 如果这张图片没有下一张图片的链接
            print("没有图片")
            return
        # 有链接，但是是 空链接
        elif div.find("a")['href'] is None or div.find("a")['href'] == "":
            print("没有图片")
            return
        #展示进度
        print("下载信息：总进度：", beginNUM, "/", endNUM, " ，正在下载组图：(",nowpage, "/", totalpage, ")")

        # 变换成下一页
        if int(nowpage) < int(totalpage):
            #获取下一张图片链接
            nextPageLink = "http://www.mmonly.cc/mmtp/qcmn/" + (div.find('a')['href'])
        elif int(nowpage) == int(totalpage):
            #获取下一组图片链接
            nextPageLink = (div.find('a')['href'])
        #获取图片链接
        picLink = (div.find('a').find('img')['src'])  # 本网站大图的SRC属性是下一张图片的链接
        picAlt = (div.find('a').find('img'))['alt']  # 图片的名字alt属性
        print('图片链接:', picLink)
        print('组图名：[ ', picAlt, ' ] ')
        #print('开始下载...........')
        #Download(picLink, picAlt, nowpage)
        #print("下载成功！")
        #print('下一页链接:', nextPageLink)
        # 递归
        run(nextPageLink, beginNUM, endNUM)
        return


#主函数
if __name__ == '__main__':
    # http://www.mmonly.cc/mmtp/qcmn任意一个网址开始爬取，是爬取的起点（）
    targetUrl ="http://www.mmonly.cc/mmtp/qcmn/237273_10.html"
    run(targetUrl, beginNUM=0, endNUM=10)  # 设置下载图片数量：endNUM-beginNUM 数字相减为总数量