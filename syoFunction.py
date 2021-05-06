import re
import PySimpleGUI as sg
import requests
from pathlib import Path


#
# mainUrl：用于拼接小说链接
# url：打开的页面链接
# proxies：代理设置，自己使用的是v2ray自带的23000+1为http代理
# headers：请求头
# originalHtml：get请求后得到的页面源代码
#
# headers = {"User-Agent": "Chrome/68.0.3440.106"}
# mainUrl = 'https://ncode.syosetu.com'
def getHtml(url: str, port: int = None) -> str:
    headers = {"User-Agent": "Chrome/68.0.3440.106"}
    mainUrl = 'https://ncode.syosetu.com'
    if port is not None:
        return requests.get(url=url, headers=headers,
                            proxies={'http': 'http://localhost:%d' % port,
                                     'https': 'http://localhost:%d' % port}).text
    else:
        return requests.get(url=url, headers=headers).text


# originalHtml = getOriginalHtml(str)

def getNovelTitle(html: str) -> str:
    novelTitle = re.findall('<title>(.*)</title>', html)
    return novelTitle[0]


def getWriterName(html: str) -> str:
    # 如果不使用re.S参数，则只在每一行内进行匹配，如果一行没有，就换下一行重新开始。
    # 而使用re.S参数以后，正则表达式会将这个字符串作为一个整体，在整体中进行匹配。
    writerNameDiv = re.findall(r'<div class="novel_writername">(.*?)</div>', html, re.S)[0]
    # writerName = re.findall(r'<a href=".*?">(.*?)</a>', writerNameDiv)
    return writerNameDiv


def getNovelUrlList(html: str) -> list:
    pattern = re.compile(r"<dd class=" + "\"subtitle\">\n" + "<a href=" + "\"(.*?)\"" + ">(.*?)</a>\n" + "</dd>")
    novelUrlList = pattern.findall(html, re.S)
    return novelUrlList


def openNovelChapterUrl(novelTitle: str, writerName: str, NovelUrlList: list, port: int) -> str:
    mainUrl = 'https://ncode.syosetu.com'
    maxNumber = len(NovelUrlList)
    number = 1
    for novelUrlListItem in NovelUrlList:
        chapterUrl = mainUrl + novelUrlListItem[0]
        chapterName = novelUrlListItem[1]
        print("正在下载标题为[%s]的小说\nURL=[%s]" % (chapterName, chapterUrl))
        contentHtml = getHtml(chapterUrl, port)
        chapterContentHtml = getChapterContentHtml(contentHtml)
        content = dataClean(chapterContentHtml)
        if number <= maxNumber:
            saveChapterContent(novelTitle, writerName, chapterName, content, number)
            number = number + 1
    return "下载完成"


def getChapterContentHtml(chapterHtml: str) -> str:
    chapterPattern = re.compile(r'<div id="novel_honbun" class="novel_view">(.*?)</div>', re.S)
    chapterContent = chapterPattern.findall(chapterHtml)[0]
    return chapterContent


def dataClean(chapterContentHtml: str) -> str:
    dataCleanPattern = re.compile(r'<p id=".*?">(.*?)</p>', re.S)
    chapterContentList = dataCleanPattern.findall(chapterContentHtml)
    chapterContent = ''
    for item in chapterContentList:
        chapterContent = chapterContent + item + '\r\n'
    chapterContent = chapterContent.replace('<br />', '')
    chapterContent = chapterContent.replace('<rb>', '')
    chapterContent = chapterContent.replace('</rb>', '')
    chapterContent = chapterContent.replace('<rp>', '')
    chapterContent = chapterContent.replace('</rp>', '')
    chapterContent = chapterContent.replace('<rt>', '')
    chapterContent = chapterContent.replace('</rt>', '')
    chapterContent = chapterContent.replace('<ruby>', '')
    chapterContent = chapterContent.replace('</ruby>', '')
    return chapterContent


def saveChapterContent(novelTitle: str, writerName: str, novelChapterName: str, chapterContent: str,
                       count: int = None) -> str:
    path = 'novel/' + novelTitle + '/'
    if not Path(path).exists():
        Path(path).mkdir(parents=True, exist_ok=True)

    fp = Path(path + str(count) + '_' + novelChapterName + '.txt')

    fp.write_text(data=novelChapterName + "\n" + writerName + '\n\n' + chapterContent, encoding='utf-8')
    return '保存完成'


def main(url: str, port: int = None):
    try:
        if port is not None:
            originalHtml = getHtml(url=url, port=port)
        else:
            originalHtml = getHtml(url=url)
        novelTitle = getNovelTitle(originalHtml)
        writerName = getWriterName(originalHtml)
        states = openNovelChapterUrl(novelTitle, writerName, getNovelUrlList(originalHtml), port=port)
        return states
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    icon = 'image/icon.ico'

    layout = [[sg.Text('小说链接：', font=('黑体', '13'), pad=((10, 10), (5, 10))),
               sg.InputText(default_text='https://ncode.syosetu.com/n4445gy/')],
              [sg.Text('https代理端口号：', font=('黑体', '13'), pad=((10, 15), (10, 10))),
               sg.InputText(default_text='23001')],
              [sg.Button('Ok', size=(10, 2), pad=((150, 10), (10, 10))),
               sg.Button('Cancel', size=(10, 2))]
              # [sg.InputText(key='returnValue')]
              ]
    # 创造窗口
    window = sg.Window('syosetu', layout, resizable=False, size=(500, 200), icon=icon)
    # 事件循环并获取输入值
    while True:
        event, values = window.read()
        print('You entered ', event)
        if event in (None, 'Cancel'):  # 如果用户关闭窗口或点击`Cancel`
            break
        else:
            if values[1] == '':
                returnValue = main(values[0], None)
            else:
                returnValue = main(values[0], int(values[1]))
        while True:
            pop = sg.Window("通知", [[sg.Text(returnValue)]], icon=icon)
            if pop.read()[0] in (None, 'Cancel'):
                break
        pop.close()

    window.close()
