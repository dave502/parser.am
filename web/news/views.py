from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.template import loader
import pymongo

from urllib.parse import urlparse, quote
from lxml import html
import requests
import asyncio
import re
import os


 
async def index(request):
    
    img_detect = bool(int(request.GET.get("img", False)))
    txt_summarize = bool(int(request.GET.get("txt", False)))
    
    START_URL = "https://news.am/eng/"
    
    # xPath to top 5 news
    URL_TOP_NEWS_ARTICLE = "//div[@class='news-list short-top']/a[@class='news-item']/@href"
    
    # xPathes to news elements (they are changeable, so their variants are in the lists)
    ARTICLE_FIELDS = {
        'title': 
            [
                "//div[@class='article-title']/text()", 
                "//div[contains(@id,'opennews')]//h1/text()",
            ],
        'img': 
            [
                "//div[@class='article-text']/img/@src", 
                "//div[@id='opennewstext']/img/@src",
                "//div[@class='article-text']/iframe[contains(@src, 'youtube')]/@src"
            ],
        'text': 
            [
                "string(//span[@class='article-body'])", 
                "//div[@id='opennewstext']//*[not(self::h1 or self::div or self::img)]/text()",
            ],
        }

    # get response from start page
    resp = requests.get(START_URL)
    # get elements tree
    tree = html.fromstring(resp.content)
    # get top 5 news 
    top_news_urls = tree.xpath(URL_TOP_NEWS_ARTICLE)
    # create a list of tasks for parsing for every news article 
    parsers = [parse_item(top_news_url, ARTICLE_FIELDS, img_detect, txt_summarize) \
                for top_news_url in top_news_urls]
    # run tasks and get results when they are all will be ready
    news = await asyncio.gather(*parsers)
    
    # show results in template
    template = loader.get_template("news/index.html")

    context = {"news": news}
    return render(request, "news/index.html", context)


async def parse_item(url: str, 
                    fields: dict[str:list[str]], 
                    img_detect:bool=False, 
                    txt_summarize:bool=False) -> dict:

    img_server = os.getenv('IMG_SERVER', 'http://213.171.14.158:8080/') 
    txt_server = os.getenv('TXT_SERVER', 'http://213.171.14.158:8070/') 

    base_url = 'https://news.am'
    # some urls are wihout domain and some (from news branches) are with domain,
    # so make all urls with domains
    if "news.am/" not in url:
        url = base_url + url
    else:
        url_parsed = urlparse(url)
        if url_parsed.hostname.split('.')[0] != "news":
            base_url = url_parsed.scheme + "://" + url_parsed.hostname
        
    # make request to article url and get element's tree    
    resp = requests.get(url)
    tree = html.fromstring(resp.content)
    
    # get from tree all fields with given tags
    doc_values = {field_key: ([tree.xpath(field_val) for field_val in fields if tree.xpath(field_val)]) 
        for (field_key, fields) in fields.items()}
    
    print(f"{len(doc_values)=}")    
        
    if title := doc_values.get("title"):
        while isinstance(title, list):
            title = title[0]
        doc_values["title"] = title.strip()     
     
    print(f"{doc_values.get('title')=}")     
        
    if text := doc_values.get("text"):
        while isinstance(text, list):
            if isinstance(text[0], list):
                text = text[0]
            else:
                print(f"{text=}")   
                if txt_summarize:
                    resp = requests.get(txt_server, params={'text': text[0]})
                    text = resp.json().get('text')
                else:
                    text = " ".join(" ".join(text).split()[:50]) + "..."
        doc_values["text"] = text   
        
    print(f"{doc_values.get('text')=}")  
    
    if img_url := doc_values.get("img"):
        # for title and pic just get the nested list and get the string from it
        while isinstance(img_url, list):
            img_url = img_url[0]
        img_url = img_url.strip()
        
        if not img_url.startswith('https:'):
            img_url = base_url + '/' + img_url.lstrip('/')
            
        elif img_url.startswith('https://www.youtube.com/embed/'):
            video_id = re.findall('https://www.youtube.com/embed/(.*)\?.*', img_url)[0]
            img_url = f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
            
        if img_detect:
            doc_values['orig_img'] = img_url   
            doc_values["img"] = img_server + 'img/' + quote(img_url, safe='')
        else:
            doc_values["img"] = img_url

    print(f"{doc_values.get('img')=}")                 
    
    return doc_values