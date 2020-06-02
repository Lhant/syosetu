
import requests
#正则表达式模块
import re

import os
#标题规范化
def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title
#目标小说URL
url1=input('请输入小说url编号：')
url='https://ncode.syosetu.com/%s/'%url1
print(url)
headers = {"user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
#模拟 http
rep=requests.get(url,headers=headers)
#目标小说主页源码
rep.encoding='utf-8'
html=rep.text

#返回title
title=re.findall(r'<p class="novel_title">(.*?)</p>',html)
#标题规范化
title=validateTitle(title[0])
print(title)

#返回作者
writer=re.findall(r'<div class="novel_writername">(.*?)</div>',html,re.S)[0]
print(writer[0])
#正则匹配
#返回匹配链接
dl=re.findall(r'<a href="/'+url1+'/'+'.*?'+'/">.*?</a>',html,re.S)

#返回需要链接
chapter_list=re.findall(r'<a href="(.*?)">(.*?)<',str(dl))
print(chapter_list)
#新建小说目录
os.mkdir('%s'%title)
#章节提示以防乱序
i=1
for x in chapter_list:
    chapter_title=x[1]
    chapter_url='https://ncode.syosetu.com%s'%x[0]
    print(chapter_url)
    chapter_rep=requests.get(chapter_url,headers=headers)
    chapter_rep.encoding='utf-8'
    chapter_html=chapter_rep.text
    chapter_content=re.findall(r'<div id="novel_honbun" class="novel_view">(.*?)</div>',chapter_html,re.S)[0]
    replacething=re.findall(r'<p id=' + '.*?' + '>', chapter_content)
    for y in replacething:
        chapter_content=chapter_content.replace(y,'')
    chapter_content=chapter_content.replace('</p>','\r\n')
    chapter_content = chapter_content.replace('<br />', '')
    chapter_content = chapter_content.replace('<rb>', '')
    chapter_content = chapter_content.replace('</rb>', '')
    chapter_content = chapter_content.replace('<rp>', '')
    chapter_content = chapter_content.replace('</rp>', '')
    chapter_content = chapter_content.replace('<rt>', '')
    chapter_content = chapter_content.replace('</rt>', '')
    chapter_content = chapter_content.replace('<ruby>', '')
    chapter_content = chapter_content.replace('</ruby>', '')
    chapter_title=validateTitle(chapter_title)
    print(chapter_title)
    #写入
    file = open('%s\%d_%s.txt'%(title,i,chapter_title), 'w+', encoding='utf-8')
    i+=1#章节自增
    file.write(chapter_title)
    file.write(writer)
    file.write(chapter_content)
    file.close()