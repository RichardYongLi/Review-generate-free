import pandas as pd
from Bio import Entrez
from Bio import Medline
import urllib.error
import requests
import re
import html2text
import sys

cdir = sys.path[0]
ref = pd.read_csv(cdir+'/2024-SCI-IF.csv')
default_jcr = ['Q1','Q2','Q3','Q4']
#jr = 'Nucleic Acids Res'


# #key="Duodenal adenocarcinoma"+" AND "+"Surgical treatment"+" AND "+"(ICI"+" OR "+"ICB"+" OR "+"CPI)"+" NOT "+"review"
key = input("请输入你想搜索的主题词：")
local_url=input("请输入你想存储的位置及名称：")

###JCR###################################################
JCR=input("请输入JCR分区,用英文逗号分隔（例如: Q1,Q2,Q3): ")
if not JCR:
    jcr_list = ['Q1', 'Q2', 'Q3', 'Q4']
else:
    jcr_list = [item.strip() for item in JCR.split(',')]
print(jcr_list)
###IF###################################################
min_if = int(input("请输入最低影响影子(若无请输入0): "))
max_if = int(input("请输入最高影响影子(若无请输入1000): "))

###年份###################################################
start_year = int(input("请输入开始年份: "))
end_year = int(input("请输入结束年份: "))
years_list = [str(year) for year in range(start_year, end_year + 1)]


turl="https://pubmed.ncbi.nlm.nih.gov/"
tdata=requests.get(turl,params={"term":key}).text
pat_allpage='<span class="total-pages">(.*?)</span>'
allpage=re.compile(pat_allpage,re.S).findall(tdata)
total = int(allpage[0].replace('\n        ','').replace(',',''))*10
num=input("请输入大致想获取的文章数目（总数为"+str(total)+"):")
n = 0
should_continue = True

with open(local_url + ".html", "a", encoding="utf-8") as file:
    while should_continue:
        for j in range(0,int(total)//10+1):
            url="https://pubmed.ncbi.nlm.nih.gov/"+"?term="+key+"&page="+str(j+1)
            data=requests.get(url,params={"term":key}, timeout=10).text
            pat1_content_url='<div class="docsum-wrap">.*?<.*?href="(.*?)".*?</a>'
            content_url=re.compile(pat1_content_url,re.S).findall(data)
            hd={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0','User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3741.400 QQBrowser/10.5.3863.400'}
            for i in range(0,len(content_url)):
                curl="https://pubmed.ncbi.nlm.nih.gov/"+content_url[i]
                try:
                    cdata=requests.get(curl,headers=hd).text
                    #print(cdata)
                    pat2_title="<title>(.*?)</title>"
                    pat3_content='<div class="abstract-content selected".*?>(.*?)</div>'
                    pat4_date='<span class="cit">(.*?)</span>'
                    pat5_journal='<meta[^>]*?name="citation_publisher[^>]*?content="(.*?)"'
                    title=re.compile(pat2_title,re.S).findall(cdata)
                    print("正则爬取的题目是："+title[0])
                    content=re.compile(pat3_content,re.S).findall(cdata)
                    date=re.compile(pat4_date,re.S).findall(cdata)
                    journal = re.compile(pat5_journal,re.S).findall(cdata)
                    jr = str(journal[0])
                    print(str(journal[0]))
                    filtered_jr = ref[ref["AbbrName"].str.contains(jr, case=False)]
                    jcr = filtered_jr['JCR'].to_list()
                    impact = filtered_jr['JIF'].to_list()
                    print(str(jcr[0]))
                    print(float(impact[0]))
                    fh = open(local_url + ".html", "a", encoding="utf-8")
                    year = date[0][0:4]
                    print(year)
                    #print(type(year))
                    #fh.write(str(title[0]) + ' ----' + str(date[0]) + "<br />" + str(content[0]) + "<br /><br />")
                    #print(year in years_list, str(jcr[0]) in jcr_list, float(min_if) <= float(impact[0]) <= float(max_if))
                    if year in years_list and str(jcr[0]) in jcr_list and float(min_if) <= float(impact[0]) <= float(max_if):
                        print(year,jr, str(jcr[0]),float(impact[0]))
                        fh.write(str(title[0])  + ' ----' + str(journal[0]) + ' ----' + str(year)+ ' ----' + str(jcr[0])+ 
                        ' ----' + str(float(impact[0])) +"<br />" + str(content[0]) + "<br /><br />")
                        n += 1
                        print('record: ' + str(n))

                        if n >= int(num):
                            print(str(num) + '篇符合要求的文献检索完毕')
                            should_continue = False
                            break
                        
                except Exception as err:
                    print(f"发生错误：{err}")

            if not should_continue:
                break
            



with open(local_url + ".html", "r", encoding="utf-8") as file:
    html_content = file.read()
 
text_content = html2text.html2text(html_content)
with open(local_url + ".txt",'w', encoding='utf-8') as f:
   f.write(text_content)

