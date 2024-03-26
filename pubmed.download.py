import pandas as pd
from Bio import Entrez
from Bio import Medline
import urllib.error
import requests
import re
import html2text

#key="Duodenal adenocarcinoma"+" AND "+"Surgical treatment"+" AND "+"(ICI"+" OR "+"ICB"+" OR "+"CPI)"+" NOT "+"review"
key = input("请输入你想搜索的主题词：")
local_url=input("请输入你想存储的位置及名称：")
start_year = int(input("请输入开始年份: "))
end_year = int(input("请输入结束年份: "))
years_list = [str(year) for year in range(start_year, end_year + 1)]
turl="https://pubmed.ncbi.nlm.nih.gov/"
tdata=requests.get(turl,params={"term":key}).text
pat_allpage='<span class="total-pages">(.*?)</span>'
allpage=re.compile(pat_allpage,re.S).findall(tdata)
num=input("请输入大致想获取的文章数目（总数为"+str(int(allpage[0].replace('\n        ','').replace(',',''))*10)+"):")
for j in range(0,int(num)//10+1):
    url="https://pubmed.ncbi.nlm.nih.gov/"+"?term="+key+"&page="+str(j+1)
    data=requests.get(url,params={"term":key}).text
    pat1_content_url='<div class="docsum-wrap">.*?<.*?href="(.*?)".*?</a>'
    content_url=re.compile(pat1_content_url,re.S).findall(data)
    hd={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0','User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3741.400 QQBrowser/10.5.3863.400'}
    for i in range(0,len(content_url)):
        curl="https://pubmed.ncbi.nlm.nih.gov/"+content_url[i]
        try:
            cdata=requests.get(curl,headers=hd).text
            pat2_title="<title>(.*?)</title>"
            pat3_content='<div class="abstract-content selected".*?>(.*?)</div>'
            pat4_date='<span class="cit">(.*?)</span>'
            title=re.compile(pat2_title,re.S).findall(cdata)
            print("正则爬取的题目是："+title[0])
            content=re.compile(pat3_content,re.S).findall(cdata)
            date=re.compile(pat4_date,re.S).findall(cdata)
            fh = open(local_url + ".html", "a", encoding="utf-8")
            year = date[0][0:4]
            print(year)
            #print(type(year))
            #fh.write(str(title[0]) + ' ----' + str(date[0]) + "<br />" + str(content[0]) + "<br /><br />")
            if year in years_list:
                print(year)
                fh.write(str(title[0]) + ' ----' + str(date[0]) + "<br />" + str(content[0]) + "<br /><br />")
                print('record')
            fh.close

        except Exception as err:
            pass
        if int(num) < 10:
            if i+1 == int(num):
                break
        elif int(num) == 10:
            if i == 9:
                break
        elif (j*10)+i+1 == int(num):
            break


with open(local_url + ".html", "r", encoding="utf-8") as file:
    html_content = file.read()
 
text_content = html2text.html2text(html_content)
with open(local_url + ".txt",'w', encoding='utf-8') as f:
   f.write(text_content)

