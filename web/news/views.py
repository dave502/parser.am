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


 
async def index(request):
    
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
    parsers = [parse_item(top_news_url, ARTICLE_FIELDS) for top_news_url in top_news_urls]
    # run tasks and get results when they are all will be ready
    news = await asyncio.gather(*parsers)
    
    # show results in template
    template = loader.get_template("news/index.html")

    context = {"news": news}
    return render(request, "news/index.html", context)


async def parse_item(url: str, fields: dict[str:list[str]]) -> dict:

    DETECT_FACES = True

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
    
    # process the fields
    for key, val in doc_values.items():

        if not (key and val):
            continue
        
        # the result fields are in the list with various level of nested, 
        # so lets try to get all data just as string values
        
        # for text field combine all elements inside the list
        if key == "text":
            while isinstance(val, list):
                if isinstance(val[0], list):
                    val = val[0]
                else:
                    val = " ".join(" ".join(val).split()[:50]) + "..."
                    doc_values[key] = val
        else:
            # for title and pic just get the nested list and get the string from it
            while isinstance(val, list):
                val = val[0]
            doc_values[key] = val.strip()
            
            # for image process url to working form
            if key == "img":
                if not val.startswith('https:'):
                    val = base_url + '/' + val.lstrip('/')
                    doc_values[key] = val
                elif val.startswith('https://www.youtube.com/embed/'):
                    video_id = re.findall('https://www.youtube.com/embed/(.*)\?.*', val)[0]
                    val = f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
                    doc_values[key] = val
                    
                if DETECT_FACES:
                    doc_values[key] = 'http://host.docker.internal:8080/' + quote(doc_values[key], safe='')
                    
    
    return doc_values